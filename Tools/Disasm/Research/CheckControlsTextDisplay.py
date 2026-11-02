"""Сравнение текстового окна с независимой моделью на исходных байтах банка 1."""
from pathlib import Path
import collections
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
import ReferenceControlsTextDisplay as reference


def main():
    base = base_memory()
    counts = collections.Counter()
    # Проверка инициализации на исходных байтах до использования её результата в остальных сценариях.
    memory = list(base)
    expected = list(base)
    reference.initialize(expected)
    execute(memory, 0xEC0E)
    assert memory[0xC000:] == expected[0xC000:]
    initialized = list(memory)
    counts['initialize'] += 1

    def check(entry, prepare, model, name, registers=None):
        memory = list(initialized)
        # Создание различимого фона для выявления неверной строки, колонки и тетрады.
        for address in range(0x4000, 0x5B00):
            memory[address] = (address * 73 + (address >> 8) * 29 + counts[name] * 31) & 255
        prepare(memory)
        expected = list(memory)
        expected_events = []
        value = model(expected, expected_events)
        events, steps = execute(memory, entry, value or 0, registers)
        assert events == expected_events, (name, counts[name], events, expected_events)
        # Проверка всей RAM вне CPU-стека и операнда сохранённого SP прокрутки.
        ignored = {0xEFC1, 0xEFC2}
        for start, end in ((0, 0xBF00), (0xC000, 65536)):
            differences = [a for a in range(start, end) if a not in ignored and memory[a] != expected[a]]
            assert not differences, (name, counts[name], [(hex(a), memory[a], expected[a]) for a in differences[:8]])
        counts[name] += 1
        return steps

    # Проверка каждого исходного кода символа при обеих тетрадах и при переполнении колонки.
    for character in range(256):
        for column in (*range(26), 127, 255):
            check(0xEFC4, lambda m, c=column: m.__setitem__(reference.COLUMN, c),
                  lambda m, e, v=character: (reference.glyph(m, v, e), v)[1], 'glyph')
    print('Glyph cases', counts['glyph'], flush=True)
    # Проверка общего рисователя с иной строкой экрана, как у второго вызывающего фрагмента F188.
    for code in range(16, 32):
        for next_column in range(256):
            source = 0xC600 + 6 * (code // 2)
            destination = 0x5120 + next_column // 2
            check(0xEFF1, lambda m: None,
                  lambda m, e, src=source, dst=destination, c=next_column, index=code:
                      reference.draw_rows(m, src, dst, c, index), 'shared_rows',
                  {'HL': destination, 'DE': source, 'BC': 0x3600 | next_column, '^AF': code * 256 + 0xA5})
    # Проверка числового вывода и реальной прокрутки при пересечении правой границы.
    for value in range(256):
        for column in (0, 21, 22, 23, 24, 255):
            check(0xECF3, lambda m, c=column: m.__setitem__(reference.COLUMN, c),
                  lambda m, e, v=value: (reference.decimal(m, v, e), v)[1], 'decimal')
    # Проверка числового потребителя при каждом значении и обходе конечного маркера.
    for value in range(256):
        for wrap in (False, True):
            def prepare(m, v=value, wrapped=wrap):
                reference.put_word(m, reference.READER, 0xEC9E if wrapped else 0xEC7E)
                m[0xEC80:0xEC82] = [2, v]
                m[reference.COLUMN] = v % 26
            check(0xECA2, prepare, reference.consume, 'consumer_number')
    # Проверка строк из очереди и активного указателя, LF, CR и повторных CR без подмены CALL.
    for character in range(256):
        for active in (False, True):
            def prepare(m, v=character, already=active):
                m[0x9000:0x9005] = [13, 13, v, 10, 1]
                m[0xEC80:0xEC82] = [0x90, 0]
                if already:
                    reference.put_word(m, reference.ACTIVE, 0x9000)
                m[reference.COLUMN] = v
            check(0xECA2, prepare, reference.consume, 'consumer_string')
    # Проверка немедленного выхода на свободной записи с сохранением занятой записи после неё.
    for wrap in (False, True):
        def prepare(m, wrapped=wrap):
            reference.put_word(m, reference.READER, 0xEC9E if wrapped else 0xEC7E)
            m[0xEC80:0xEC84] = [1, 255, 2, 123]
        check(0xECA2, prepare, reference.consume, 'consumer_free')
    report = dict(passed=True, cases_by_kind=dict(counts), total_cases=sum(counts.values()),
        original_instructions=True, called_procedures_executed=True, calls_stubbed=False,
        independent_screen_and_queue_model=True, every_non_stack_ram_byte_compared=True,
        saved_scroll_sp_operand_excluded=True, exact_register_contract_proved=False,
        all_character_bytes=True, font_out_of_range_bytes_preserved=True,
        irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsTextDisplayVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


def execute(memory, entry, value=0, overrides=None):
    memory[0xBFFE:0xC000] = [255, 63]
    simulator = Simulator(memory)
    arguments = dict(AF=value * 256 + 0xA5, HL=0x1357,
        DE=0x2468, BC=0x369C, IX=0xABCD, IY=0x5C3A,
        **{'^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC},
        SP=0xBFFE, PC=entry)
    arguments.update(overrides or {})
    initial = get_registers(arguments, None, False)
    initial[14], initial[26], initial[27] = value, value & 1, value % 3
    simulator.registers[:] = initial
    events = []
    for steps in range(20000):
        pc = simulator.registers[PC]
        if pc == 0x3FFF:
            assert simulator.registers[SP] == 0xC000
            # Проверка сохраняемых регистров всех публичных путей вывода, IX меняется только инициализатором.
            preserved = (10, 11, 14, 22, 23, 26, 27) + (() if entry == 0xEC0E else (8, 9))
            assert all(simulator.registers[i] == initial[i] for i in preserved), ('preserved', hex(entry))
            return events, steps
        if pc == 0xEFC4:
            events.append(('glyph', simulator.registers[0]))
        elif pc == 0xED28:
            events.append(('scroll',))
        simulator.run()
    raise AssertionError(('не достигнут внешний RET', hex(entry), hex(simulator.registers[PC])))


if __name__ == '__main__':
    main()

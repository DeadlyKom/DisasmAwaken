"""Проверка исходных F10D/F142/F188 против BCD-арифметики и экранной модели."""
from pathlib import Path
import collections
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
import ReferenceControlsBcdCounter as reference


def main():
    base = base_memory()
    counts = collections.Counter()
    def check(entry, value, gate=128, mask=0, column=0):
        memory = list(base)
        for address in range(0x4000, 0x5B00):
            memory[address] = (address * 73 + value * 31 + gate) & 255
        memory[0x9BBD:0x9BC1] = reference.encode(value % 100000000)
        memory[0xF10E] = gate
        memory[0xBFFE:0xC000] = [255, 63]
        expected = list(memory)
        wanted = []
        e, d, l, h = expected[0x9BBD:0x9BC1]
        args = {'HL': h * 256 + l, 'DE': d * 256 + e,
                'BC': mask * 256 + column, 'AF': (value & 255) * 256 + 0xA5,
                'IX': 0xABCD, 'IY': 0x5C3A, '^AF': 0xDEF0,
                '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, 'SP': 0xBFFE, 'PC': entry}
        if entry == 0xF10D:
            reference.tick(expected, wanted)
        elif entry == 0xF142:
            reference.display(expected, (l, h, e, d), mask, wanted)
        else:
            reference.nibble(expected, value & 255, column, wanted)
        simulator = Simulator(memory)
        initial = get_registers(args, None, False)
        initial[14], initial[26], initial[27] = value & 255, value & 1, value % 3
        simulator.registers[:] = initial
        observed = []
        for _ in range(4000):
            registers = simulator.registers
            pc = registers[PC]
            if pc == 0x3FFF:
                break
            if pc == 0xF188:
                observed.append((registers[0] & 15, registers[3]))
            simulator.run()
        else:
            raise AssertionError(('возврат', hex(entry), value, gate, mask, column))
        assert observed == wanted, ('знаки', hex(entry), value, gate, mask, column, observed, wanted)
        assert memory[:0xBF00] == expected[:0xBF00] and memory[0xC000:] == expected[0xC000:], ('память', hex(entry), value, gate, mask, column)
        assert registers[SP] == 0xC000
        assert all(registers[i] == initial[i] for i in (8, 9, 10, 11, 14, 26, 27))
        # Проверка сохранения основных пар у рисователя тетрады и у диспетчера вывода пар.
        if entry == 0xF188:
            assert registers[2:8] == initial[2:8]
        elif entry == 0xF142:
            assert registers[4:8] == initial[4:8] and registers[2] == mask
        elif not gate & 1:
            assert registers[2:12] == initial[2:12] and registers[16:24] == initial[16:24]
        counts[format(entry, '04X')] += 1

    # Проверка всех входных байтов и всех экранных колонок общего вывода тетрады.
    for value in range(256):
        for column in range(256):
            check(0xF188, value, column=column)
    print('Nibble cases', counts['F188'], flush=True)
    # Проверка каждой маски выбора пар при разных значениях четырёх BCD-байтов.
    for value in (0, 1, 12345678, 99999999, 90909090, 1010101):
        for mask in range(256):
            check(0xF142, value, mask=mask)
    # Проверка всех состояний делителя и границ переносов каждой десятичной пары.
    boundary = (0, 8, 9, 98, 99, 100, 9998, 9999, 10000, 999998, 999999,
                1000000, 99999998, 99999999)
    for value in boundary:
        for gate in range(256):
            check(0xF10D, value, gate=gate)
    # Проверка инкремента на воспроизводимом наборе корректных восьмизначных BCD-чисел.
    for index in range(4096):
        check(0xF10D, (index * 65537 + index * index * 73) % 100000000, gate=1)
    report = dict(passed=True, total_cases=sum(counts.values()), cases_by_entry=dict(counts),
        all_nibble_inputs_and_columns=True, all_pair_selection_masks=True, all_gate_bytes=True,
        valid_bcd_carry_boundaries=True, overflow_modulo_100000000=True,
        original_instructions=True, actual_draw_rows_executed=True, calls_stubbed=False,
        screen_and_counter_independently_checked=True, memory_outside_test_stack_compared=True,
        primary_pair_preservation_checked=True, irq_executed=False, native_execution=False,
        invalid_bcd_inputs_proved=False, independent_full_flag_model=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsBcdCounterVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

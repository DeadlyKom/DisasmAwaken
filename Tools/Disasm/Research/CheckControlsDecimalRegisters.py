"""Регистры десятичного вывода, настоящий шрифт и прокрутка, без сборки."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckControlsTextDisplay import execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from ReferenceControlsTextDisplay import initialize, glyph, COLUMN


class ScreenModel(list):
    def __init__(self, values):
        super().__init__(values)
        self.writes = []

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self.writes.extend(zip(range(*key.indices(len(self))), value))
        else:
            self.writes.append((key, value))
        super().__setitem__(key, value)


def main():
    flat = list(base_memory())
    check_init = list(flat)
    initialize(check_init)
    execute(flat, 0xEC0E)
    assert flat[0xC000:] == check_init[0xC000:]
    base = [bytearray([0xA0 + i] * 16384) for i in range(8)]
    base[5], base[2], base[1] = (bytearray(flat[0x4000:0x8000]),
                               bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:]))
    memory = RecordedBanks(banks=[bytearray(b) for b in base], out7ffd=17)
    sim = Simulator(memory)
    cases = scrolls = 0
    profiles = [(v, c) for v in range(256) for c in (0, 21, 22, 23, 24, 255)]
    profiles += [(v, c) for v in (0, 255) for c in range(256)]
    for value, column in profiles:
        memory.recording = False
        for bank, original in zip(memory.banks, base):
            bank[:] = original
        screen = [(cases + i * 73 + (i >> 8) * 29) & 255 for i in range(0x1B00)]
        memory.banks[5][:0x1B00] = bytes(screen)
        memory[COLUMN] = column
        put(memory, 0xBFFE, (255, 63))
        initial = get_registers({
            'AF': value * 256 + ((cases * 109) & 255), 'HL': 0x1357,
            'DE': 0x2468, 'BC': 0x369C, '^HL': 0x1234, '^DE': 0x5678,
            '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x5C3A,
            'SP': 0xBFFE, 'PC': 0xECF3,
        }, None, False)
        initial[14], initial[26], initial[27] = cases & 255, cases & 1, cases % 3
        wanted = list(initial)
        expected_flat = ScreenModel(flat)
        expected_flat[0x4000:0x5B00] = screen
        expected_flat[COLUMN] = column
        expected_flat[0xBFFE:0xC000] = [255, 63]
        expected_flat.writes = []
        digits = format(value, '02d').encode('ascii')
        # Расчёт последних сохранённых слов прокрутки до очистки и рисования очередной цифры.
        for index, digit in enumerate(digits):
            if expected_flat[COLUMN] >= 24:
                wanted[18:22] = [expected_flat[0x55FD], expected_flat[0x55FC],
                                 expected_flat[0x55FF], expected_flat[0x55FE]]
                saved = 0xBFFA if index == len(digits) - 1 else 0xBFF6
                expected_flat[0xEFC1] = saved & 255
                expected_flat[0xEFC2] = saved >> 8
                scrolls += 1
            last_column = 0 if expected_flat[COLUMN] >= 24 else expected_flat[COLUMN]
            glyph(expected_flat, digit, [])
        # Расчёт выходов последнего глифа по его колонке, шрифту и независимому экранному результату.
        next_column = expected_flat[COLUMN]
        mask = 0xF0 if next_column & 1 else 15
        destination = 0x55F4 + last_column // 2
        source = 0xC600 + 6 * ((digits[-1] - 32) // 2) + 5
        result = expected_flat[destination]
        flags = (result & 0xA8) | (0x40 if result == 0 else 0) | (4 if result.bit_count() % 2 == 0 else 0)
        wanted[0:8] = [result, flags, result & (mask ^ 255), mask,
                       source >> 8, source & 255, destination >> 8, destination & 255]
        wanted[16:18] = [next_column, 0x10 | (next_column & 0x28) | (0x44 if not next_column & 1 else 0)]
        wanted[12], wanted[24] = 0xC000, 0x3FFF
        sim.registers[:] = initial
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        sim.run(start=0xECF3, stop=0x3FFF)
        memory.recording = False
        # Проверка регистров кроме R, всей RAM вне восьми временных байтов и кратности остальных записей.
        assert all(wanted[i] == sim.registers[i] for i in (*range(15), *range(16, 25), 26, 27)), (
            value, column, [(i, wanted[i], sim.registers[i]) for i in (*range(15), *range(16, 25), 26, 27)
                            if wanted[i] != sim.registers[i]])
        allowed = set(range(0xBFF6, 0xBFFE))
        nonstack = [(offset + {5: 0x4000, 2: 0x8000, 1: 0xC000}[bank], v)
                    for bank, offset, v in memory.writes
                    if not (bank == 2 and offset + 0x8000 in allowed)]
        assert Counter(nonstack) == Counter(expected_flat.writes), (value, column, 'writes')
        for address in allowed:
            expected_flat[address] = memory[address]
        expected = [bytearray(b) for b in base]
        expected[5], expected[2], expected[1] = (bytearray(expected_flat[0x4000:0x8000]),
                                               bytearray(expected_flat[0x8000:0xC000]), bytearray(expected_flat[0xC000:]))
        assert memory.banks == expected and not trace.writes and memory.o7ffd == 17
        cases += 1
    report = dict(passed=True, total_cases=cases, scroll_calls=scrolls,
                  all_input_byte_values=True, all_initial_columns_for_zero_and_255=True,
                  exact_registers_except_R=True, all_physical_RAM_except_8_stack_bytes=True,
                  nonstack_write_multiplicity_checked=True, actual_glyph_and_scroll_executed=True,
                  last_glyph_AFprime_column_and_BIT_flags_checked=True,
                  complete_joint_input_product_exhausted=False, stack_residue_values_proved=False,
                  R_proved=False, timing_proved=False, irq_executed=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsDecimalRegistersVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

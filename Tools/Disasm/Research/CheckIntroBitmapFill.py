"""128 строк INTRO, полная RAM, кратность записей и точный конечный контекст."""
from collections import Counter
import json

from CheckIntro import ROOT, original_memory, Simulator, get_registers
from CheckPreviewCoordinateMultiply import Memory
from ReferenceControlsPointRespawn import refresh


def main():
    memory = Memory(original_memory())
    cpu = Simulator(memory)
    cases = 0
    # Проверка каждого заполнителя и каждого начального F отдельными сериями.
    profiles = [(value, value ^ 0xA5) for value in range(256)]
    profiles += [(0x69, flags) for flags in range(256)]
    for value, flags in profiles:
        memory.recording = False
        memory[0x4000:0x5B00] = [(i * 37 + cases) & 255 for i in range(6912)]
        stack = (0x7FFE, 0x8000, 0x8001, 0xBFFE)[cases % 4]
        memory[stack:stack + 2] = [255, 63]
        initial = get_registers(dict(SP=stack, PC=0x6A67, HL=0x1357,
                                    DE=((value ^ 0x3C) << 8) | 0x7A,
                                    BC=0xA500 | value, AF=(0xC3 << 8) | flags,
                                    IX=0xABCD, IY=0x5C3A,
                                    **{'^HL': 0x1234, '^DE': 0x5678,
                                       '^BC': 0x9ABC, '^AF': 0xDEF0}), None, False)
        initial[14], initial[15], initial[27] = value, flags, cases % 3
        cpu.registers[:] = initial
        expected_memory = list(memory)
        expected_memory[0x4000:0x5000] = [value] * 4096
        expected = initial[:]
        expected[0:8] = [0, 0x41, 0, value, value ^ 0x3C, 0xE0, 0x50, 0]
        expected[12], expected[15], expected[24] = stack + 2, refresh(flags, 9069), 0x3FFF
        memory.writes = []
        memory.recording = True
        measured = 0
        # Проверка каждого реального шага, чтобы оборачивания R не скрывали ошибку полного M1.
        for _ in range(10000):
            if cpu.registers[24] == 0x3FFF:
                break
            previous_r = cpu.registers[15]
            cpu.run()
            increment = (cpu.registers[15] - previous_r) & 127
            assert increment == 1
            measured += increment
        else:
            raise AssertionError('заливка INTRO не вернулась')
        r = cpu.registers
        assert measured == 9069, measured
        assert r[:25] == expected[:25] and r[26:] == expected[26:], (value, flags, r, expected)
        assert list(memory) == expected_memory
        assert Counter(memory.writes) == Counter({(address, value): 1 for address in range(0x4000, 0x5000)})
        cases += 1
    report = dict(passed=True, cases=cases, all_fill_bytes=True, all_initial_F=True,
                  complete_fill_and_F_product_exhausted=False,
                  exact_full_RAM_and_write_multiplicity=True, bytes_written_once=4096,
                  exact_main_alternate_and_index_registers=True,
                  full_M1=9069, R_I_IM_IFF_checked=True,
                  tested_stack_addresses=[0x7FFE, 0x8000, 0x8001, 0xBFFE],
                  flat_loaded_intro_view=True, irq_executed=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroBitmapFillVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

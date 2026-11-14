"""Байтовый счётчик строк HELP DB69, все Y/F', без подмены печати её моделью."""
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1'),
                str(ROOT / 'Tools/Disasm/Research')]
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from ReferenceControlsPointRespawn import refresh
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers


def main():
    memory = Memory([0] * 65536)
    raw = payload(8)
    memory[0xDB00:0xDB00 + len(raw)] = raw
    memory[0x7FFE:0x8000] = [255, 63]
    cpu = Simulator(memory)
    initial = get_registers(dict(SP=0x7FFE, HL=0x1357, DE=0x2468,
                                BC=0x369C, AF=0xA55A, IX=0xABCD, IY=0x5C3A,
                                **{'^HL': 0x1234, '^DE': 0x5678,
                                   '^BC': 0x9ABC, '^AF': 0xDEF0}), None, False)
    cases = 0
    for y in range(256):
        for alternate_flags in range(256):
            memory.recording = False
            memory[0x6320:0x6322] = [0xA7, y]
            cpu.registers[:] = initial
            r = cpu.registers
            r[14], r[15], r[17], r[27] = y, alternate_flags, alternate_flags, y % 3
            expected = r[:]
            # Расчёт результата по байтовой разности Y и исходного начала восьмой строки.
            delta = (y - 8) & 255
            rows = delta // 8 + 1
            flags = (rows & 0x28) | (0x10 if rows == 16 or rows == 32 else 0) | ((delta >> 2) & 1)
            expected[0:2] = [8, alternate_flags]
            expected[16:18] = [rows, flags]
            expected[12], expected[15], expected[24] = 0x8000, refresh(alternate_flags, 13), 0x3FFF
            r[24] = 0xDB69
            memory.recording = True
            memory.writes = []
            measured = 0
            # Проверка тринадцати выборок, включая три двухбайтовых префикса SRL.
            for _ in range(16):
                if r[24] == 0x3FFF:
                    break
                old_r = r[15]
                cpu.run()
                increment = (r[15] - old_r) & 127
                assert increment in (1, 2)
                measured += increment
            else:
                raise AssertionError('хвост HELP не вернулся')
            assert measured == 13
            # Проверка полного регистрового контекста без времени исполнения.
            assert r[:25] == expected[:25] and r[26:] == expected[26:], (y, alternate_flags, r, expected)
            assert Counter(memory.writes) == Counter({(0x6321, 8): 1})
            assert memory[0x6320] == 0xA7 and memory[0x7FFE:0x8000] == [255, 63]
            cases += 1
    report = dict(passed=True, cases=cases, entry=0xDB69,
                  all_CursorY_and_alternate_F_pairs=True,
                  exact_registers_and_single_cursor_write=True,
                  full_tail_M1=13, R_I_IM_IFF_checked=True,
                  preceding_PrintAfterCR_executed=False,
                  flat_view_of_selected_help_bank=True,
                  irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/HelpRowCountTailVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

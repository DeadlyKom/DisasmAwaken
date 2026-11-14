"""Точный договор хвостового входа финального эффекта до общего рисователя.

Документация: ../../../Docs/IntroScrolledFrame.md#хвостовой-вход-финального-кадра
"""
from hashlib import sha256
from itertools import product
import json

from CheckIntro import ROOT, original_memory
from CheckStationFlightCycle import DISK, ENTRIES
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, R, get_registers


def main():
    flat = original_memory()
    code = bytes(flat[0x661E:0x662C])
    offset = ENTRIES[3]['offset'] + 0x31E
    assert code == DISK[offset:offset + 14]
    count = 0
    for flags, refresh in product(range(256), (0, 127, 128, 255)):
        memory = flat.copy()
        initial = get_registers(dict(PC=0x661E, SP=0x5FFE + 2 * (flags & 1),
            HL=0x1234, DE=0x2345, BC=0x3456, AF=0xA500 | flags,
            IX=0x4567, IY=0x5678, I=flags, R=refresh,
            **{'^HL':0x6789, '^DE':0x789A, '^BC':0x89AB, '^AF':0x9ABC}),
            {'im':flags % 3, 'iff':flags & 1}, False)
        cpu = Simulator(memory)
        cpu.registers[:] = initial
        # Проверка передачи без исполнения первой инструкции общего рисователя.
        cpu.run(0x661E, 0x66A3)
        expected = initial.copy()
        expected[:8] = [0x16, flags, 0x66, 0x32, 0xFF, 0xFF, 0x66, 0x2C]
        expected[PC] = 0x66A3
        expected[R] = (refresh & 128) | ((refresh + 5) & 127)
        compared = (*range(25), 26, 27)
        assert all(cpu.registers[i] == expected[i] for i in compared), (flags, refresh)
        assert cpu.registers[SP] == initial[SP] and memory == flat
        count += 1
    report = dict(passed=True, total_cases=count, original_entry_sha256=sha256(code).hexdigest(),
                  all_F_values_checked=True, tested_R=[0,127,128,255], M1_before_tail_target=5,
                  full_RAM_unchanged=True, exact_registers_except_T_compared=True,
                  stopped_before_DrawScrolledTexture=True, IRQ_executed=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/IntroFinalFrameEntryVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

"""Все состояния изменяемого операнда строк значений выборки F000..FFFF.

Документация: ../../../Docs/IntroGeneratedEffects.md#фаза-строк-значений
"""
from collections import Counter
from hashlib import sha256
import json

from CheckIntro import original_memory, ROOT
from CheckMusicGateTicks import Memory
from CheckStationFlightCycle import DISK, ENTRIES
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, get_registers


def pointer_bytes(phase):
    def first(row):
        if phase == 0x80:
            return 0xB0 - (row + 1) // 2
        if phase == 0:
            return 0xB0 - row // 2
        return 0xB0
    return bytes(0x89 + (min(0x7F, max(0x70, first(row) - column)) - 0x70) // 2
                 for row in range(256) for column in range(16))


def main():
    flat = original_memory()
    code = bytes(flat[0x6D1D:0x6D4C])
    offset = ENTRIES[3]['offset'] + 0xA1D
    assert code == DISK[offset:offset + len(code)]
    memory = Memory(flat)
    cpu = Simulator(memory)
    summaries = []
    for phase in range(256):
        memory.recording = False
        memory[:] = flat
        memory[0x6D40] = phase
        memory[0xF000:0x10000] = [0xA5] * 4096
        expected = list(memory)
        table = pointer_bytes(phase)
        expected[0xF000:0x10000] = table
        initial = get_registers(dict(PC=0x6D1D, SP=0x5FFE, IX=0x1357, IY=0x5C3A, I=0x3C,
            **{'^HL':0x2468, '^DE':0x369C, '^BC':0x47AD, '^AF':0x58BE}), {'im':1, 'iff':0}, False)
        cpu.registers[:] = initial
        memory.writes = []
        memory.recording = True
        cpu.run(0x6D1D, 0x6D4C)
        memory.recording = False
        r = cpu.registers
        assert list(memory) == expected, phase
        assert Counter(address for address, _ in memory.writes) == Counter({**dict.fromkeys(range(0xF000, 0x10000), 1), 0x6D40:256})
        assert [value for address, value in memory.writes if address == 0x6D40] == [phase ^ (0x80 if index & 1 == 0 else 0) for index in range(256)]
        assert r[PC] == 0x6D4C and r[SP] == 0x5FFE and r[2:4] == [0, 0] and r[6:8] == [0, 0]
        assert r[4] == (0x30 if phase in (0, 0x80) else 0xB0)
        assert r[5] == (0x21 if phase == 0 else 0x20 if phase == 0x80 else 0xA0)
        assert r[:2] == [phase, 0x42 | int(phase < 128)]
        assert all(r[index] == initial[index] for index in (*range(8, 12), 14, *range(16, 24), 26, 27))
        if phase not in (0, 0x80):
            assert table == bytes([0x90] * 4096)
        summaries.append(dict(initial_phase=phase, final_phase=memory[0x6D40], final_DE=r[4] * 256 + r[5],
                              final_AF=r[0] * 256 + r[1], table_sha256=sha256(table).hexdigest()))
    report = dict(passed=True, total_cases=256, original_pointer_loop_sha256=sha256(code).hexdigest(),
                  all_phase_bytes_executed=True, full_RAM_and_write_counts_compared=True,
                  table_bytes=4096, phase_operand_writes_per_case=256,
                  only_00_and_80_decrement_row_base=True, other_254_states_fill_90=True,
                  phase_restored_after_256_rows=True, final_HL=0, final_BC=0, stack_unchanged=True,
                  initial_80_vs_00_differing_table_bytes=sum(a != b for a,b in zip(pointer_bytes(0),pointer_bytes(0x80))),
                  native_reachability_of_other_phase_states_proved=False,
                  warm_phases_and_renderer_executed=False, IRQ_executed=False,
                  native_execution=False, assembly_executed=False, cases=summaries)
    (ROOT / 'Tools/Disasm/Reports/IntroLookupPointerRowsVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены все 256 фаз строк значений, две рабочие раскладки и 254 вырожденных состояния.')


if __name__ == '__main__':
    main()

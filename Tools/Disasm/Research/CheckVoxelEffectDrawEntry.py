"""Две проекции FA3A и проверка параметров на входе EC7F.

Документация: ../../../Docs/ActionVisualEffectWalk.md#обновление-r-в-обёртке-двух-проекций
"""
from collections import Counter
from itertools import chain, product
import json
from random import Random

from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory
from CheckVoxelEffectProjection import projection_memory, signed_byte
from ReferenceActionLogRatio import evaluate
from ReferenceControlsPointRespawn import refresh
from skoolkit.simutils import R
from CheckStationFlightCycle import DISK, ENTRIES
from hashlib import sha256


def project(horizontal, vertical, depth, offsets, scale, writes=None, refresh_counts=None):
    mode = scale.bit_length() - 4
    if refresh_counts is not None:
        assert 0 <= mode <= 6 and scale == 1 << (mode + 3)
    if depth & 0x8000:
        if refresh_counts is not None:
            refresh_counts.append(8)
        return None
    first = evaluate((vertical + scale * signed_byte(offsets >> 8)) & 65535, depth)
    if writes is not None:
        writes.extend(first['writes'])
    if first['af'][1] & 1:
        if refresh_counts is not None:
            refresh_counts.append(26 + mode + first['refresh_m1'])
        return None
    second = evaluate((horizontal + scale * signed_byte(offsets & 255)) & 65535, depth)
    if writes is not None:
        writes.extend(second['writes'])
    if refresh_counts is not None:
        refresh_counts.append((46 if second['af'][1] & 1 else 48) + 2 * mode
                              + first['refresh_m1'] + second['refresh_m1'])
    if second['af'][1] & 1 or 0x7F80 <= second['hl'] <= 0x7FFF:
        return None
    return (second['hl'] + 128) & 65535, (first['hl'] + 48) & 65535


def signed_quarter(word):
    return (((word ^ 0x8000) - 0x8000) // 4) & 65535


def main():
    baseline = projection_memory()
    # Проверка исходного тела обёртки до настройки собственных операндов.
    offset = ENTRIES[21]['offset'] + 0xFA3A - 0xEC00
    assert bytes(baseline[0xFA3A:0xFAC8]) == DISK[offset:offset + 0x8E]
    counts = Counter()
    rng = Random(0xFA3A)
    fixed = product(range(7), (0, 0x7FFF, 0xFFFF), (0, 0x8000, 0xFFFF),
                    (0, 1, 256, 4096, 32767, 32768), (0, 0x0101, 0x0102, 0x7F7F, 0xFFFF))
    sampled = ((rng.randrange(7), *(rng.randrange(65536) for _ in range(4))) for _ in range(2048))
    stack_floor = 0xBFFE
    costs = {}
    sampled_r = set()
    for case, (mode, horizontal, vertical, depth, offsets) in enumerate(chain(fixed, sampled)):
        scale = 1 << (mode + 3)
        doubled = offsets * 2 & 65535
        opposite = ((-(doubled >> 8) & 255) << 8) | (-(doubled & 255) & 255)
        writes = [(0xF9FA, 6 - mode), (0xFA1D, 6 - mode)]
        for address, word in ((0xFA67, horizontal), (0xFA6D, vertical), (0xFA6A, depth)):
            writes.extend(((address, word & 255), (address + 1, word >> 8)))
        projection_costs = []
        first = project(horizontal, vertical, depth, opposite, scale, writes, projection_costs)
        second = project(horizontal, vertical, depth, doubled, scale, writes, projection_costs) if first else None
        outcome = 'first_rejected' if first is None else 'second_rejected'
        route = outcome
        expected_m1 = sum(projection_costs) + (29 if first is None else 49)
        if second is not None:
            dx, dy = ((b - a) & 65535 for a, b in zip(first, second))
            outcome = 'clip_sprite' if 0 < dx < 1024 and 0 < dy < 1024 else 'size_rejected'
            # Расчёт собственной стоимости по первому сработавшему выходу после проекций.
            if dx == 0:
                route, own_m1 = 'zero_width', 53
            elif dx >= 1024:
                route, own_m1 = 'wide_width', 60
            elif dy == 0:
                route, own_m1 = 'zero_height', 72
            elif dy >= 1024:
                route, own_m1 = 'wide_height', 79
            else:
                route, own_m1 = 'clip_sprite', 113
            expected_m1 = sum(projection_costs) + own_m1
        memory = Memory(baseline)
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0xFA3A, 'SP': 0xBFFE, 'A': mode,
                                         'HL': horizontal, 'DE': vertical, 'BC': depth,
                                         '^HL': offsets, '^DE': 0xD800, '^BC': 0xA55A,
                                         'IX': 0x1357, 'IY': 0x5C3A, 'I': 0x3C,
                                         'R': case & 255}, {'im':2, 'iff':0}, False)
        assert sim.registers[27] == 2 and sim.registers[26] == 0
        initial = sim.registers.copy()
        memory.writes = []
        memory.recording = True
        measured_m1 = 0
        initial_r = sim.registers[R]
        for _ in range(700):
            if sim.registers[PC] in (0x3FFF, 0xEC7F):
                break
            opcode = memory[sim.registers[PC]]
            assert opcode not in (0xDD, 0xFD)
            measured_m1 += 2 if opcode in (0xCB, 0xED) else 1
            sim.run()
            assert sim.registers[R] == refresh(initial_r, measured_m1)
        memory.recording = False
        r = sim.registers
        context = (mode, horizontal, vertical, depth, offsets, outcome, first, second)
        assert all(r[index] == initial[index] for index in (8, 9, 10, 11, 14, 18, 19, 20, 21, 26, 27)), context
        assert memory[0xF9FA] == memory[0xFA1D] == 6 - mode, context
        if outcome == 'clip_sprite':
            assert r[PC] == 0xEC7F and r[SP] == 0xBFFE, context
            assert r[6] * 256 + r[7] == signed_quarter(first[0]), context
            assert r[4] * 256 + r[5] == signed_quarter(first[1]), context
            assert r[2:4] == [dy >> 2, dx >> 2], context
            assert r[20:24] == [0xD8, 0, (doubled >> 8) >> 1, (doubled & 255) >> 1], context
        else:
            assert r[PC] == 0x3FFF and r[SP] == 0xC000, context
        assert [(a, v) for a, v in memory.writes if not 0xBFF2 <= a < 0xBFFE] == writes, context
        stack_floor = min(stack_floor, *(a for a, _ in memory.writes if 0xBFF2 <= a < 0xBFFE))
        assert measured_m1 == expected_m1, (context, route, measured_m1, expected_m1)
        costs.setdefault(route, set()).add(expected_m1)
        sampled_r.add(initial_r)
        counts[outcome] += 1
    assert len(counts) == 4, counts
    assert sampled_r == set(range(256))
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  stopped_before_clip_sprite=True, exact_code_writes=True, deepest_stack_write=stack_floor,
                  r_checked_after_every_instruction=True, r_independent_path_formula_checked=True,
                  refresh_m1_by_route={key: sorted(value) for key, value in costs.items()},
                  initial_r_codes_sampled_across_cases=sorted(sampled_r),
                  all_initial_r_codes_crossed_with_all_inputs=False,
                  original_draw_entry_code_sha256=sha256(bytes(baseline[0xFA3A:0xFAC8])).hexdigest(),
                  alternate_BC_DE_index_registers_I_IM_IFF_preserved_before_clip=True,
                  initial_I=0x3C, initial_IM=2, initial_IFF=0,
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/VoxelEffectDrawEntryVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

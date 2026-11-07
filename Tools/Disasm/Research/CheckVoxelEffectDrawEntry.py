"""Две проекции FA3A и проверка параметров на входе EC7F."""
from collections import Counter
from itertools import chain, product
import json
from random import Random

from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory
from CheckVoxelEffectProjection import projection_memory, signed_byte
from ReferenceActionLogRatio import evaluate


def project(horizontal, vertical, depth, offsets, scale, writes=None):
    if depth & 0x8000:
        return None
    first = evaluate((vertical + scale * signed_byte(offsets >> 8)) & 65535, depth)
    if writes is not None:
        writes.extend(first['writes'])
    if first['af'][1] & 1:
        return None
    second = evaluate((horizontal + scale * signed_byte(offsets & 255)) & 65535, depth)
    if writes is not None:
        writes.extend(second['writes'])
    if second['af'][1] & 1 or 0x7F80 <= second['hl'] <= 0x7FFF:
        return None
    return (second['hl'] + 128) & 65535, (first['hl'] + 48) & 65535


def signed_quarter(word):
    return (((word ^ 0x8000) - 0x8000) // 4) & 65535


def main():
    baseline = projection_memory()
    counts = Counter()
    rng = Random(0xFA3A)
    fixed = product(range(7), (0, 0x7FFF, 0xFFFF), (0, 0x8000, 0xFFFF),
                    (0, 1, 256, 4096, 32767, 32768), (0, 0x0101, 0x0102, 0x7F7F, 0xFFFF))
    sampled = ((rng.randrange(7), *(rng.randrange(65536) for _ in range(4))) for _ in range(2048))
    stack_floor = 0xBFFE
    for mode, horizontal, vertical, depth, offsets in chain(fixed, sampled):
        scale = 1 << (mode + 3)
        doubled = offsets * 2 & 65535
        opposite = ((-(doubled >> 8) & 255) << 8) | (-(doubled & 255) & 255)
        writes = [(0xF9FA, 6 - mode), (0xFA1D, 6 - mode)]
        for address, word in ((0xFA67, horizontal), (0xFA6D, vertical), (0xFA6A, depth)):
            writes.extend(((address, word & 255), (address + 1, word >> 8)))
        first = project(horizontal, vertical, depth, opposite, scale, writes)
        second = project(horizontal, vertical, depth, doubled, scale, writes) if first else None
        outcome = 'first_rejected' if first is None else 'second_rejected'
        if second is not None:
            dx, dy = ((b - a) & 65535 for a, b in zip(first, second))
            outcome = 'clip_sprite' if 0 < dx < 1024 and 0 < dy < 1024 else 'size_rejected'
        memory = Memory(baseline)
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0xFA3A, 'SP': 0xBFFE, 'A': mode,
                                         'HL': horizontal, 'DE': vertical, 'BC': depth,
                                         '^HL': offsets, '^DE': 0xD800}, None, False)
        memory.writes = []
        memory.recording = True
        for _ in range(700):
            if sim.registers[PC] in (0x3FFF, 0xEC7F):
                break
            sim.run()
        memory.recording = False
        r = sim.registers
        context = (mode, horizontal, vertical, depth, offsets, outcome, first, second)
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
        counts[outcome] += 1
    assert len(counts) == 4, counts
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  stopped_before_clip_sprite=True, exact_code_writes=True, deepest_stack_write=stack_floor, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/VoxelEffectDrawEntryVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

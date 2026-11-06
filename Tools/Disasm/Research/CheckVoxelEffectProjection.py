"""Проверка F9E9 с настоящим AE73 и исходными байтами страницы VOXAL."""
from collections import Counter
from itertools import chain, product
import json
from random import Random

from CheckActionParameterActivation import flat_action
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionLogRatio import EXP, LOG, evaluate


def signed_byte(value):
    return value if value < 128 else value - 256


def projection_memory():
    baseline = flat_action()
    baseline[0xC000:] = memory_image()[0xC000:]
    baseline[0x9100:0x9200] = [word & 255 for word in LOG]
    baseline[0x9200:0x9300] = [word >> 8 for word in LOG]
    baseline[0x9300:0x9400] = EXP
    baseline[0xBFFE:0xC000] = [255, 63]
    return baseline


def main():
    baseline = projection_memory()
    counts = Counter()
    rng = Random(0xF9E9)
    edges = (0, 1, 255, 256, 0x7FFF, 0x8000, 0xFFFF)
    fixed = product(range(7), edges, edges, edges, (0, 0x7F80, 0x807F, 0xFFFF))
    sampled = ((rng.randrange(7), *(rng.randrange(65536) for _ in range(4))) for _ in range(2048))
    for mode, horizontal, depth, vertical, offsets in chain(fixed, sampled):
        memory = baseline.copy()
        memory[0xF9FA] = memory[0xFA1D] = 6 - mode
        multiplier = 1 << (mode + 3)
        writes = []
        outcome = 'negative_depth'
        if depth < 0x8000:
            first = evaluate((vertical + multiplier * signed_byte(offsets >> 8)) & 65535, depth)
            writes.extend(first['writes'])
            outcome = 'first_overflow'
            if not first['af'][1] & 1:
                second = evaluate((horizontal + multiplier * signed_byte(offsets & 255)) & 65535, depth)
                writes.extend(second['writes'])
                outcome = 'second_overflow' if second['af'][1] & 1 else 'success'
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0xF9E9, 'SP': 0xBFFE, 'HL': horizontal,
                                         'DE': depth, 'BC': vertical, '^HL': offsets}, None, False)
        for _ in range(300):
            if sim.registers[PC] == 0x3FFF:
                break
            sim.run()
        r = sim.registers
        assert r[PC] == 0x3FFF and r[SP] == 0xC000, (mode, horizontal, depth, vertical, offsets)
        if outcome == 'success':
            assert r[6] * 256 + r[7] == (second['hl'] + 128) & 65535, (mode, horizontal, depth, vertical, offsets, r[:8], second)
            assert r[4] * 256 + r[5] == (first['hl'] + 48) & 65535
            assert r[2:4] == [0, 128]
            assert bool(r[1] & 4) == (0x7F80 <= second['hl'] <= 0x7FFF)
        else:
            restored = (first['hl'] + 48) & 65535 if outcome == 'second_overflow' else horizontal
            assert r[0:2] == [3, 4] and r[6] * 256 + r[7] == restored
        expected = baseline.copy()
        expected[0xF9FA] = expected[0xFA1D] = 6 - mode
        for addr, value in writes:
            expected[addr] = value
        assert memory[:0xBFF8] == expected[:0xBFF8] and memory[0xBFFE:] == expected[0xBFFE:]
        counts[outcome] += 1
    assert set(counts) == {'negative_depth', 'first_overflow', 'second_overflow', 'success'}
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  modes=list(range(7)), whole_draw_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/VoxelEffectProjectionVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

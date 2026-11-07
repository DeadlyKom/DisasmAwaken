"""Проверка F9E9 с настоящим AE73 и исходными байтами страницы VOXAL."""
from collections import Counter
from itertools import chain, product
import json
from random import Random

from CheckActionParameterActivation import flat_action
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory
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
        memory = Memory(baseline)
        memory[0xF9FA] = memory[0xFA1D] = 6 - mode
        multiplier = 1 << (mode + 3)
        initial = get_registers({'PC': 0xF9E9, 'SP': 0xBFFE, 'HL': horizontal,
                                 'DE': depth, 'BC': vertical, '^HL': offsets, '^BC': 0xA55A,
                                 '^DE': 0x46FD, '^AF': 0x91D7, 'IX': 0xC345, 'IY': 0xFEDC}, None, False)
        expected = list(initial)
        expected[PC], expected[SP] = 0x3FFF, 0xC000
        writes = []

        def push(address, word):
            writes.extend(((address - 2, word & 255), (address - 1, word >> 8)))

        def pair(index, word):
            expected[index:index + 2] = [word >> 8, word & 255]

        push(0xBFFE, horizontal)
        expected[0:2] = [3, 4]
        outcome = 'negative_depth'
        if depth < 0x8000:
            first = evaluate((vertical + multiplier * signed_byte(offsets >> 8)) & 65535, depth)
            push(0xBFFC, depth)
            push(0xBFFA, 0xFA09)
            writes.extend(first['writes'])
            pair(2, first['bc'])
            expected[16:18] = list(first['alternate_af'])
            outcome = 'first_overflow'
            if not first['af'][1] & 1:
                y = (first['hl'] + 48) & 65535
                push(0xBFFE, y)
                push(0xBFFC, 0xFA2B)
                second = evaluate((horizontal + multiplier * signed_byte(offsets & 255)) & 65535, depth)
                writes.extend(second['writes'])
                expected[16:18] = list(second['alternate_af'])
                outcome = 'second_overflow'
                if second['af'][1] & 1:
                    pair(2, second['bc'])
                    pair(4, second['de'])
                    pair(6, y)
                else:
                    outcome = 'success'
                    x = second['hl'] + 128
                    value = x & 65535
                    flags = (value >> 8) & 0xA8
                    flags |= 64 if not value else 0
                    flags |= 16 if (second['hl'] & 4095) + 128 >= 4096 else 0
                    flags |= 4 if 0x7F80 <= second['hl'] <= 0x7FFF else 0
                    flags |= int(x >= 65536)
                    expected[0:2] = [second['af'][0], flags]
                    pair(2, 128)
                    pair(4, y)
                    pair(6, value)
        sim = Simulator(memory)
        sim.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(300):
            if sim.registers[PC] == 0x3FFF:
                break
            sim.run()
        memory.recording = False
        context = (mode, horizontal, depth, vertical, offsets, outcome)
        checked = (*range(13), 14, *range(16, 25), 26, 27)
        assert all(sim.registers[i] == expected[i] for i in checked), (
            context, [(i, sim.registers[i], expected[i]) for i in checked if sim.registers[i] != expected[i]]
        )
        assert memory.writes == writes, (context, memory.writes, writes)
        counts[outcome] += 1
    assert set(counts) == {'negative_depth', 'first_overflow', 'second_overflow', 'success'}
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  modes=list(range(7)), registers_except_r_compared=True, exact_code_and_stack_writes=True,
                  whole_draw_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/VoxelEffectProjectionVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

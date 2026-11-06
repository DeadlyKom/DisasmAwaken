"""Обновление списка широких векторов 688A до поиска близкой цели."""
from itertools import product
import json
from random import Random

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionNearVectorSearch import evaluate as search
from ReferenceControlsPointRespawn import cp_flags


def main():
    baseline = flat_action()
    baseline[0xBFFE:0xC000] = [255, 63]
    rng = Random(0x688A)
    outcomes = {'empty': 0, 'moved': 0}
    results = {'near_zero': 0, 'other': 0}
    for count, serial in product(range(7), range(512)):
        memory = baseline.copy()
        memory[0x688B] = count
        components = [rng.randrange(-32768, 32768) for _ in range(3)] if serial else [0, 1, -1]
        for address, value in zip((0xE5B3, 0xE5D2, 0xE5ED), components):
            memory[address:address + 2] = list((value & 65535).to_bytes(2, 'little'))
        for address in range(0x9B27, 0x9B6F):
            memory[address] = rng.randrange(256)
        if count and serial % 4 == 0:
            for axis, value in enumerate(components):
                address = 0x9B27 + axis * 4
                sample = ((value // 4 or 1) + (serial & 0xF8)) & 0xFFFFFFFF
                memory[address:address + 4] = list(sample.to_bytes(4, 'little'))
        memory[0x6693], memory[0x668E], memory[0x9BC5] = serial & 255, 0xA5, serial >> 1
        expected = memory.copy()
        deltas = [value // 4 or 1 for value in components]
        if count:
            for address, delta in zip((0x68D5, 0x68FD, 0x6925), deltas):
                expected[address:address + 2] = list((delta & 65535).to_bytes(2, 'little'))
            for index in range(count):
                for axis, delta in enumerate(deltas):
                    address = 0x9B27 + index * 12 + axis * 4
                    value = int.from_bytes(bytes(memory[address:address + 4]), 'little')
                    expected[address:address + 4] = list(((value - delta) & 0xFFFFFFFF).to_bytes(4, 'little'))
            expected[0xBFFC:0xBFFE] = [0x53, 0x69]
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0x688A, 'SP': 0xBFFE}, None, False)
        for _ in range(700):
            if sim.registers[PC] in (0x69BE, 0x3FFF):
                break
            sim.run()
        context = (count, serial, components)
        if count:
            assert sim.registers[PC] == 0x69BE and sim.registers[SP] == 0xBFFC, context
            assert sim.registers[10:12] == list((0x9B27 + count * 12).to_bytes(2, 'big')), context
        else:
            assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        assert memory == expected, (context, [(i, a, b) for i, (a, b) in enumerate(zip(memory, expected)) if a != b][:8])
        outcomes['moved' if count else 'empty'] += 1
        if count:
            rows = tuple(tuple(int.from_bytes(bytes(expected[address:address + 4]), 'little')
                               for address in range(start, start + 12, 4))
                         for start in range(0x9B27, 0x9B27 + count * 12, 12))
            local = search(sim.registers, rows)
            for address, value in local['writes']:
                expected[address] = value
            r = local['registers']
            if r[7] == 0:
                panel = ((-r[6]) & 255) >> 1
                expected[0x6693], expected[0x668E] = min(panel, 46), 1
                af = [1, cp_flags(panel, 47)]
                results['near_zero'] += 1
            else:
                if expected[0x6693]:
                    expected[0x668E], expected[0x6693] = expected[0x6693], 0
                af = [expected[0x9BC5], cp_flags(expected[0x9BC5], r[5])]
                results['other'] += 1
            sim.run(0x69BE, 0x3FFF)
            assert sim.registers[:2] == af and sim.registers[2:12] == r[2:12], context
            assert sim.registers[SP] == 0xC000 and memory == expected, context
    report = dict(passed=True, total_cases=sum(outcomes.values()), outcomes=outcomes,
                  physical_record_counts=list(range(7)), panel_outcomes=results,
                  actual_search_executed=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionWideMotionPrefixVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

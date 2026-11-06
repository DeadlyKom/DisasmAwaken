"""Числовой выбор класса в 7B78 до записи класса либо возврата."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionFoldedRandom import step


def main():
    original = flat_action()
    memory = original.copy()
    sim = Simulator(memory)
    seeds = {}
    for seed in range(65536):
        value = step(seed, 0)['word'] >> 8
        seeds.setdefault(value, seed)
        if len(seeds) == 256:
            break
    assert len(seeds) == 256
    outcomes = Counter()
    for maximum, high, inhibit in product(range(128), range(256), (0, 255)):
        seed = seeds[high]
        memory[0xEBEA:0xEBED] = [seed & 255, seed >> 8, 0]
        memory[0x9B71], memory[0x9B74], memory[0x9B77], memory[0x9B82] = maximum, 0, 255, inhibit
        memory[0xBFFC:0xC000] = [0x34, 0x12, 255, 63]
        adjustment = (original[0x9900 + maximum // 4] >> 4) & 7
        chosen = 0 if max(0, high - adjustment) < 10 else next(
            (code for threshold, code in ((67, 1), (80, 2), (90, 4), (94, 5), (99, 6), (107, 7), (112, 8))
             if high < threshold), None)
        accepted = chosen is not None and not (chosen == 8 and inhibit)
        sim.registers[:] = get_registers({'PC': 0x7B78, 'SP': 0xBFFC}, None, False)
        for _ in range(180):
            if sim.registers[PC] in (0x7BDB, 0x3FFF):
                break
            sim.run()
        r = sim.registers
        context = (maximum, high, inhibit, chosen)
        assert r[PC] == (0x7BDB if accepted else 0x3FFF) and r[SP] == (0xBFFC if accepted else 0xC000), context
        if accepted:
            assert r[3] == chosen, context
        else:
            assert r[4:6] == [0x12, 0x34], context
        outcomes[str(chosen) if accepted else 'rejected'] += 1
    assert set(outcomes) == {'0', '1', '2', '4', '5', '6', '7', '8', 'rejected'}
    report = dict(passed=True, total_cases=outcomes.total(), outcomes=dict(outcomes),
                  all_random_high_and_folded_maximum_values=True, unreachable_class_three=True,
                  stopped_before_model_selection=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnClassSelectionVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

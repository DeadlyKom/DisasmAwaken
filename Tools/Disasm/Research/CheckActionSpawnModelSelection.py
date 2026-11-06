"""Выбор пары модели 7BDB, байтовые проверки и обе точки передачи."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers


def main():
    original = flat_action()
    memory = original.copy()
    sim = Simulator(memory)
    counts = Counter()
    for cls, seed, saved_high, adjust in product(range(9), range(8), range(256), (0, 1, 127, 128, 255)):
        table = original[0x7AC6 + 2 * cls] | original[0x7AC7 + 2 * cls] << 8
        offset = 2 * ((seed + 13) & 7)
        model, argument = original[table + offset:table + offset + 2]
        lhs = (((128 - saved_high) & 255) >> 1) + 25
        rhs = (128 - adjust) & 255
        target = 0x7C21 if cls in (6, 7) or (lhs >= rhs and cls != 8) else 0x7C78
        memory[0xBFFC:0xBFFE] = [0x7A, saved_high]
        sim.registers[:] = get_registers({'PC': 0x7BDB, 'SP': 0xBFFC, 'IX': 0xA100,
                                         'DE': adjust << 8, 'BC': cls}, None, False)
        sim.registers[15] = seed
        for _ in range(55):
            if sim.registers[PC] in (0x7C21, 0x7C78):
                break
            sim.run()
        r = sim.registers
        context = (cls, seed, saved_high, adjust, target, offset)
        assert r[PC] == target and r[SP] == 0xBFFE, context
        assert (memory[0xA106], memory[0xA10F], memory[0xA112]) == (model, argument, cls), context
        assert r[4:6] == [saved_high, 0x7A], context
        counts[f'{target:04X}'] += 1
    assert len(counts) == 2
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  all_nine_rows_and_eight_offsets=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnModelSelectionVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

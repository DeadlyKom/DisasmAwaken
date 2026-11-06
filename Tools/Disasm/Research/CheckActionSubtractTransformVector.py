"""Проверка 679B до ветки переполнения или вызова оценки вектора."""
from collections import Counter
import json

from CheckActionParameterActivation import flat_action
from CheckActionSubtractWorkVector import FIELDS, OPERANDS, evaluate, profiles
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def main():
    memory = Memory(flat_action())
    sim = Simulator(memory)
    outcomes = Counter()
    for values, deltas, af, _ in profiles():
        for address, value in zip(FIELDS, values):
            memory[address - 9:address - 6] = list(value.to_bytes(3, 'little'))
        for address, value in zip(OPERANDS, deltas):
            memory[address:address + 2] = list(value.to_bytes(2, 'little'))
        initial = get_registers({'PC': 0x679B, 'SP': 0xBFFE, 'AF': af, 'BC': 0x5A3C,
                                 'IX': 0xABCD, 'IY': 0x2468}, None, False)
        wanted, writes, stopped, fetches = evaluate(initial, values, deltas)
        wanted[PC] = 0x67F5 if stopped is None else 0x6727
        wanted[SP] = initial[SP]
        wanted[15] = refresh(initial[15], fetches - (stopped is None))
        sim.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(50):
            if sim.registers[PC] in (0x6727, 0x67F5):
                break
            sim.run()
        memory.recording = False
        compared = (*range(25), 26, 27)
        assert all(wanted[i] == sim.registers[i] for i in compared), (values, deltas, stopped,
            [(i, wanted[i], sim.registers[i]) for i in compared if wanted[i] != sim.registers[i]])
        assert memory.writes == [(address - 9, value) for address, value in writes], (values, deltas, stopped)
        outcomes['complete' if stopped is None else f'overflow_{stopped}'] += 1
    assert len(outcomes) == 4
    report = dict(passed=True, total_cases=outcomes.total(), outcomes=dict(outcomes),
                  exact_registers_and_write_order=True, stopped_at_branch_boundary=True,
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSubtractTransformVectorVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

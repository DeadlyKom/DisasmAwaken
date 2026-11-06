"""Фаза 7B58, проверка счётчика и выбор ветви по потоку 0."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory
from ReferenceActionFoldedRandom import step


def main():
    memory = Memory(flat_action())
    memory[0xBFFE:0xC000] = [255, 63]
    sim = Simulator(memory)
    outcomes = Counter()
    for phase, counter, limit in product(range(256), range(256), (0, 0xFD, 255)):
        seed = (phase * 109 + counter * 73 + limit * 281) & 65535
        fold = (phase ^ counter) & 255
        memory[0x7B59], memory[0x7B61], memory[0x7B6B] = phase, counter, limit
        memory[0xEBDE:0xEBE1] = [seed & 255, seed >> 8, fold]
        writes = [(0x7B59, (phase >> 1) | ((phase & 1) << 7))]
        target, stack, path = 0x3FFF, 0xC000, 'even_return'
        if phase & 1:
            stack = 0xBFFE
            if 1 <= counter <= 128:
                target, path = 0x79A8, 'countdown'
            else:
                value = step(seed, fold)
                target, path = (0x794B, 'fallback') if value['word'] & 255 < limit else (0x7B6F, 'allocate')
        sim.registers[:] = get_registers({'PC': 0x7B58, 'SP': 0xBFFE}, None, False)
        memory.writes = []
        memory.recording = True
        for _ in range(100):
            if sim.registers[PC] in (0x3FFF, 0x79A8, 0x794B, 0x7B6F):
                break
            sim.run()
        memory.recording = False
        context = (phase, counter, limit, path)
        assert sim.registers[PC] == target and sim.registers[SP] == stack, context
        if path in ('fallback', 'allocate'):
            assert memory[0xEBDE:0xEBE1] == [value['word'] & 255, value['word'] >> 8, value['fold']], context
            assert all(address in (0x7B59, 0xEBDE, 0xEBDF, 0xEBE0, 0xBFFA, 0xBFFB, 0xBFFC, 0xBFFD)
                       for address, _ in memory.writes), context
            assert memory.writes[:1] == writes
        else:
            assert memory.writes == writes, context
        outcomes[path] += 1
    report = dict(passed=True, total_cases=outcomes.total(), outcomes=dict(outcomes),
                  all_phase_and_countdown_bytes=True, stops_before_record_selection=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnScheduleVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

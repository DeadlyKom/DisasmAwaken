"""Развилки 794B и 79A8 до поиска свободной объектной записи."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionFoldedRandom import step
from ReferenceControlsPointRespawn import refresh


def main():
    memory = flat_action()
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    sim = Simulator(memory)
    outcomes = Counter()
    targets = (0x3FFF, 0x7859, 0x79CC)

    def run(entry, registers, refresh_seed):
        memory[0x7B61], memory[0x79DE], memory[0x7A6A] = 0xAA, 0xBB, 0xCC
        sim.registers[:] = get_registers({'PC': entry, 'SP': 0xBFFE, **registers}, None, False)
        sim.registers[15] = refresh_seed
        sample = None
        for _ in range(130):
            pc = sim.registers[PC]
            if pc in targets:
                break
            if memory[pc:pc + 2] == [0xED, 0x5F]:
                sample = refresh(sim.registers[15], 2) & 1
            sim.run()
        return sim.registers[PC], sample

    def verify(target, sample, counter, changed):
        assert sim.registers[PC] == target
        assert sim.registers[SP] == (0xC000 if target == 0x3FFF else 0xBFFE)
        assert memory[0x7B61] == counter
        assert (memory[0x79DE], memory[0x7A6A]) == ((32 * sample, 6 * sample) if changed else (0xBB, 0xCC))
        assert (sample is not None) == changed
        outcomes[f'{target:04X}'] += 1

    for counter, low, seed in product(range(256), range(4), (0, 1, 127, 128)):
        target, sample = run(0x79A8, {'A': counter, 'DE': low}, seed)
        changed = counter >= 128
        verify(0x79CC, sample, 5 + low if changed else counter, changed)

    def vector(words):
        for axis, word in enumerate(words):
            address = 0x9B79 + axis * 3
            memory[address:address + 2] = (word & 65535).to_bytes(2, 'little')

    rng = [next((word, 0) for word in range(65536)
                if ((result := step(word, 0)['word']) >> 8 == result & 255) == equal)
           for equal in (False, True)]
    vector((0, 112, 0))
    for word in range(65536):
        equal = bool(word & 1)
        seed, fold = rng[equal]
        memory[0xEC02:0xEC05] = [seed & 255, seed >> 8, fold]
        _, sample = run(0x794B, {'HL': word}, word & 255)
        accepted = equal and 0x23F2 <= word <= 0x23FF
        verify(0x79CC if accepted else 0x3FFF, sample, 5 + (word & 3) if accepted else 0xAA, accepted)
        assert memory[0x799C:0x799E] == list(word.to_bytes(2, 'little'))
        result = step(seed, fold)
        assert memory[0xEC02:0xEC05] == list(result['word'].to_bytes(2, 'little')) + [result['fold']]

    for words in product((-32768, -256, -112, -111, 0, 111, 112, 256, 32767), repeat=3):
        vector(words)
        seed, fold = rng[False]
        memory[0xEC02:0xEC05] = [seed & 255, seed >> 8, fold]
        _, sample = run(0x794B, {'HL': 0x23F7}, 0)
        nearby = max(map(abs, words)) < 112
        verify(0x7859 if nearby else 0x3FFF, sample, 0xAA, False)
        if nearby:
            assert memory[0xEC02:0xEC05] == [seed & 255, seed >> 8, fold]

    report = dict(passed=True, total_cases=outcomes.total(), outcomes=dict(outcomes),
                  ends_before_record_search=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnAlternateGateVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

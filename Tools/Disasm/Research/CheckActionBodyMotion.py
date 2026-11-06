"""Совместное исполнение фазового входа, смены режима и выхода 688A."""
import json
from collections import Counter
from itertools import product

from CheckActionParameterActivation import flat_action
from CheckActionSubtractWorkVector import evaluate
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionFoldedRandom import step


def main():
    baseline = flat_action()
    paths = Counter()
    fixtures = ((0, 0, 0), (0x7FFFFF, 0, 0), (0x400000, 0, 0), (0x123456, 0xFFFEED, 0xABCDEF))
    for mode, phase, vector, seed in product((0, 1, 2, 255), (0, 1, 0xC001), fixtures, ((0, 0), (0x6D55, 0x7B))):
        memory = baseline.copy()
        memory[0xBFFE:0xC000] = [255, 63]
        memory[0x9B81], memory[0x688B], memory[0x9C29] = mode, 0, 255
        memory[0x6781:0x6783] = list(phase.to_bytes(2, 'little'))
        memory[0xEBF6:0xEBF9] = list(seed[0].to_bytes(2, 'little')) + [seed[1]]
        deltas = (0xFFFF, 0, 0)
        for address, delta in zip((0xE5B3, 0xE5D2, 0xE5ED), deltas):
            memory[address:address + 2] = list(delta.to_bytes(2, 'little'))
        data = bytearray(b''.join(value.to_bytes(3, 'little') for value in vector))
        memory[0x9B6F:0x9B78] = data
        initial = get_registers({'PC': 0x6780, 'SP': 0xBFFE}, None, False)
        result_mode = mode
        outcome = 'wide_only'
        if phase & 1:
            reset = False
            if mode != 1:
                if mode == 2:
                    for offset in (1, 4, 7):
                        word = int.from_bytes(data[offset:offset + 2], 'little')
                        data[offset:offset + 2] = ((word - 48) & 65535).to_bytes(2, 'little')
                values = [int.from_bytes(data[offset:offset + 3], 'little') for offset in (0, 3, 6)]
                _, writes, overflow, _ = evaluate(initial, values, deltas)
                for address, value in writes:
                    data[address - 0x9B78] = value
                high = data[2::3]
                folded = max(min(value, 255 - value) for value in high)
                reset = mode != 2 and (overflow is not None or folded >= 64)
                outcome = 'overflow' if overflow is not None else 'panel'
            if reset or mode == 1:
                outcome = 'reset' if reset else 'random'
                result_mode = 1
                new = step(*( (0x1527, 0x13) if reset else seed ))
                if new['word'] == 0x8746:
                    outcome = 'random_hit'
                    result_mode = 2
                    for offset in (1, 4, 7):
                        data[offset:offset + 2] = b'\x00\x60'
        sim = Simulator(memory)
        sim.registers[:] = initial
        sim.run(0x6780, 0x3FFF)
        context = (mode, phase, vector, seed)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        assert bytes(memory[0x9B6F:0x9B78]) == data and memory[0x9B81] == result_mode, context
        paths[outcome] += 1
    assert len(paths) >= 5, paths
    report = dict(passed=True, total_cases=paths.total(), paths=dict(paths),
                  wide_count_zero=True, actual_mode_transition_executed=True,
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionBodyMotionVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

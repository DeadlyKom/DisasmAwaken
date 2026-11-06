"""Три входа 6727, 6742 и 6765 до границ общего обработчика 6780."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionFoldedRandom import step


def main():
    baseline = flat_action()
    baseline[0xBFFE:0xC000] = [255, 63]
    counts = Counter()

    def check(entry, mode, seed, fold, words):
        memory = baseline.copy()

        def word(buffer, address, value):
            buffer[address:address + 2] = [value & 255, (value >> 8) & 255]

        memory[0x9B81] = mode
        word(memory, 0xEBF6, seed)
        memory[0xEBF8] = fold
        for address, value in zip((0x9B70, 0x9B73, 0x9B76), words):
            word(memory, address, value)
        wanted = memory.copy()
        destination = 0x688A
        if entry == 0x6765:
            outcome = 'subtract'
            destination = 0x679B
            for address, value in zip((0x9B70, 0x9B73, 0x9B76), words):
                word(wanted, address, value - 48)
        elif entry == 0x6727 and mode == 2:
            outcome = 'mode_2_return'
            destination = 0x3FFF
        else:
            if entry == 0x6727:
                wanted[0x9B81] = 1
                wanted[0x7B6B] = 255
                seed, fold = 0x1527, 0x13
            value = step(seed, fold)
            word(wanted, 0xEBF6, value['word'])
            wanted[0xEBF8] = value['fold']
            word(wanted, 0xBFFA, value['word'])
            word(wanted, 0xBFFC, 0x6745)
            outcome = 'wait'
            if value['word'] == 0x8746:
                outcome = 'activate'
                wanted[0x9B81] = 2
                for address in (0x9B70, 0x9B73, 0x9B76):
                    word(wanted, address, 0x6000)
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': entry, 'SP': 0xBFFE, 'HL': 0x1234, 'BC': 0x5678}, None, False)
        for _ in range(150):
            if sim.registers[PC] in (0x688A, 0x679B, 0x3FFF):
                break
            sim.run()
        context = (entry, mode, seed, fold, words, outcome)
        assert sim.registers[PC] == destination, context
        assert sim.registers[SP] == (0xC000 if outcome == 'mode_2_return' else 0xBFFE), context
        assert memory == wanted, (context, [(i, a, b) for i, (a, b) in enumerate(zip(memory, wanted)) if a != b][:8])
        counts[outcome] += 1

    for mode in range(256):
        check(0x6727, mode, 0x5678, 0xA5, (0x1234, 0x8765, 0xFEDC))
    seed, fold = 0x1527, 0x13
    for number in range(1, 500001):
        next_state = step(seed, fold)
        if next_state['word'] == 0x8746:
            break
        seed, fold = next_state['word'], next_state['fold']
    assert (number, seed, fold) == (41862, 0x6D55, 0x7B)
    hit = seed
    for fold, seed in product(range(256), (0, 1, 0xFFFF, hit)):
        check(0x6742, 1, seed, fold, (0x1234, 0x8765, 0xFEDC))
    for word in range(65536):
        check(0x6765, 2, 0, 0, (word, word ^ 0x5555, word ^ 0xAAAA))
    assert set(counts) == {'subtract', 'mode_2_return', 'wait', 'activate'}
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  first_hit_from_reset_in_uninterrupted_stream=number,
                  stopped_at_common_continuation=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionBodyModeTransitionVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

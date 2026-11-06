"""Продолжение E14C после преобразования координат объекта."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory


def main():
    memory = Memory(flat_action())
    sim = Simulator(memory)
    counts = Counter()
    for depth, sample in product(range(256), range(256)):
        pointer = 0xA100 + 64 * (sample % 25)
        high = (sample, sample ^ 0xD3, depth)
        values = tuple(value << 8 | (sample * 71 + index * 53) & 255 for index, value in enumerate(high))
        overflow = (sample & 7) == 0
        initial_level, initial_model = (sample * 7) & 31, (sample * 73) & 255
        memory[0xED83], memory[0x9B8E] = initial_level, initial_model
        memory[0xE4A7:0xE4A9] = [0xFE, 0xBF]
        for address, value in zip((0xD9B6, 0xD7C4, 0xD7A2), values):
            memory[address:address + 2] = list(value.to_bytes(2, 'little'))
        writes = []
        target, stack = 0xE0E2, pointer + 10
        outcome = 'overflow'
        if not overflow:
            for address, value in zip((pointer + 30, pointer + 28, pointer + 26), reversed(values)):
                writes.extend(((address, value & 255), (address + 1, value >> 8)))
            level = max(0, 15 - max(min(value, 256 - value) for value in high) // 2)
            writes.append((0xED83, max(initial_level, level)))
            outcome, stack = 'negative_depth', pointer + 26
            if depth < 128:
                if depth < 31:
                    writes.append((0x9B8E, (initial_model + 2) & 255))
                writes.extend(((0xBFFC, 0xB9), (0xBFFD, 0xE1)))
                target, stack = 0xAACC, 0xBFFC
                outcome = 'near_depth' if depth < 31 else 'nonnegative_depth'
        sim.registers[:] = get_registers({'PC': 0xE14C, 'SP': pointer + 10,
                                         '^HL': pointer, 'F': 4 if overflow else 0}, None, False)
        memory.writes = []
        memory.recording = True
        for _ in range(90):
            if sim.registers[PC] in (0xE0E2, 0xAACC):
                break
            sim.run()
        memory.recording = False
        context = (depth, sample, outcome)
        assert sim.registers[PC] == target and sim.registers[SP] == stack, context
        assert memory.writes == writes, (context, memory.writes, writes)
        counts[outcome] += 1
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  exact_write_order=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionObjectProjectionResumeVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

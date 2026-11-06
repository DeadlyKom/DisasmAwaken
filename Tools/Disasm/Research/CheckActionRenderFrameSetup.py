"""Подготовка E020 до ADB7 и публикация девяти коэффициентов после него."""
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory


DESTINATIONS = (0xCB3E, 0xCB8B, 0xCBD8, 0xCB54, 0xCBA1, 0xCBEE, 0xCB6F, 0xCBBC, 0xCC09)


def main():
    memory = Memory(flat_action())
    sim = Simulator(memory)
    counts = dict(offsets=0, skipped_offsets=0, coefficients=0)

    def run(entry, stops, writes, stack):
        sim.registers[:] = get_registers({'PC': entry, 'SP': 0xBFFE}, None, False)
        memory.writes = []
        memory.recording = True
        for _ in range(85):
            if sim.registers[PC] in stops:
                break
            sim.run()
        memory.recording = False
        assert sim.registers[PC] in stops and sim.registers[SP] == stack
        assert memory.writes == writes, (entry, memory.writes, writes)

    def approach(value, target):
        delta = (target - value) & 255
        return (value + (1 if 0 < delta < 128 else -1 if delta else 0)) & 255

    def setup(x, y, inhibit):
        memory[0xE021] = inhibit
        memory[0x9B19:0x9B1B] = [x, y]
        triple = [x ^ 255, y ^ 128, inhibit ^ 37]
        memory[0x9B95:0x9B98] = triple
        writes = []
        if not inhibit:
            writes.extend(((0x9B19, approach(x, 0x77)), (0x9B1A, approach(y, 0x2B))))
        writes.extend(((0xE021, 0), (0xED83, 0), (0x9B12, triple[0]), (0x9B13, triple[1]),
                       (0x9B14, triple[2]), (0xBFFC, 0x5D), (0xBFFD, 0xE0)))
        run(0xE020, (0xADB7,), writes, 0xBFFC)
        counts['skipped_offsets' if inhibit else 'offsets'] += 1

    for x, y in product(range(256), repeat=2):
        setup(x, y, 0)
    for inhibit in range(1, 256):
        setup(inhibit, inhibit ^ 255, inhibit)
    for index, value, mode in product(range(9), range(256), (0, 1, 2, 255)):
        coefficients = [(position * 83 + value * 7) & 255 for position in range(9)]
        coefficients[index] = value
        for position, coefficient in enumerate(coefficients):
            memory[0x9B01 + position * 2] = coefficient
        memory[0x9B81] = mode
        writes = [(address, 0x81 if coefficient == 0x80 else coefficient)
                  for address, coefficient in zip(DESTINATIONS, coefficients)]
        target, return_low = (0x6B16, 0xCB) if mode == 1 else (0x6A6E, 0xC8)
        writes.extend(((0xBFFC, return_low), (0xBFFD, 0xE0)))
        run(0xE05D, (target,), writes, 0xBFFC)
        counts['coefficients'] += 1
    report = dict(passed=True, total_cases=sum(counts.values()), outcomes=counts,
                  actual_adb7_executed=False, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionRenderFrameSetupVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

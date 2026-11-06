"""Маски E97A, проекция ADC5 и XOR значков в линейном буфере."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionLogRatio import EXP, LOG, evaluate


def main():
    baseline = flat_action()
    baseline[0xC000:] = base_memory()[0xC000:]
    baseline[0x9100:0x9200] = [value & 255 for value in LOG]
    baseline[0x9200:0x9300] = [value >> 8 for value in LOG]
    baseline[0x9300:0x9400] = EXP
    baseline[0xBFFE:0xC000] = [255, 63]
    counts = Counter()
    for mode, selection, position, coordinates in product(
            (0, 1, 2, 255), (False, True), (0, 2, 24),
            ((0, 0, 2048), (8, 9, 2048), (16, 17, 2048), (24, 25, 2048),
             (32, 33, 2048), (40, 41, 2048), (48, 49, 2048), (56, 57, 2048),
             (0, 0, 1279), (0, 0, 0x8000), (0x7000, 0, 2048), (0, 0x8000, 2048))):
        memory = baseline.copy()
        pointer = 0xA100 + 64 * position
        x, y, depth = coordinates
        memory[pointer + 1] = 1
        memory[pointer + 0x12] = 0
        for index, value in enumerate(coordinates):
            memory[pointer + 26 + 2 * index:pointer + 28 + 2 * index] = list(value.to_bytes(2, 'little'))
        memory[0x9B1B:0x9B1E] = [position if selection else 255, 255, 255]
        expected = memory[0x8000:0x8C00]

        def toggle(address, mask):
            expected[address - 0x8000] ^= mask

        for address in (0x8431, 0x87F1, 0x842E, 0x87EE):
            toggle(address, 254)
        for left, right in ((0x844E, 0x8451), (0x870E, 0x8711)):
            for row in range(7):
                toggle(left + 32 * row, 128)
                toggle(right + 32 * row, 2)
        if mode != 1:
            for address in range(0x8109, 0x8117):
                toggle(address, 255)
            for row in range(87):
                toggle(0x8129 + 32 * row, 128)
                toggle(0x8136 + 32 * row, 1)
            if 1536 <= depth < 32768 and x >> 8 != 128:
                vertical = evaluate(y, depth)
                horizontal = evaluate(x, depth)
                px = (horizontal['hl'] + 128) & 65535
                py = (vertical['hl'] + 48) & 65535
                if not ((vertical['af'][1] | horizontal['af'][1]) & 1) and 80 <= px < 174 and 14 <= py < 90:
                    source = 0xEB0E + ((px - 4) & 7) * 16 + (128 if selection else 0)
                    target = 0x8000 + (py - 4) * 32 + ((px - 4) >> 3)
                    for row in range(8):
                        for byte in range(2):
                            toggle(target + 32 * row + byte, baseline[source + 2 * row + byte])
                    counts['highlight' if selection else 'icon'] += 1
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0xE97A, 'SP': 0xBFFE, 'A': mode}, None, False)
        for _ in range(6500):
            if sim.registers[PC] == 0x3FFF:
                break
            sim.run()
        context = (mode, selection, position, coordinates)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        actual = memory[0x8000:0x8C00]
        assert actual == expected, (context, [(i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b][:10])
        counts['cases'] += 1
    assert counts['highlight'] and counts['icon']
    report = dict(passed=True, total_cases=counts['cases'], outcomes=dict(counts),
                  actual_perspective_executed=True, whole_raster_compared=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ControlsTargetOverlayVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

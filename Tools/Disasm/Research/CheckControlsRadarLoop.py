"""Полный E291: фазовый фон, фильтр записей, линии и маски значков."""
from collections import Counter
from itertools import product
import json

from CheckControlsRasterBackground import pixel_address
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers


def signed(byte):
    return (byte ^ 128) - 128


def scale(value):
    quarter = value // 4
    return quarter + (quarter + 1) // 2


def main():
    baseline = base_memory()
    counts = Counter()
    fixtures = ((0, 0, 0), (7, 8, 4), (0x80, 0, 1), (1, 0x80, 2),
                (1, 0, 0x80), (127, 0, 0), (0x81, 0, 0),
                (0, 100, 0x81), (0, 0x9C, 127), (28, 70, 25), (0, 0, 32),
                (0, 127, 176), (0, 129, 96))
    for phase, (cx, height, cy), cls, force in product(range(16), fixtures, (0, 1, 12, 20, 21), (0, 255)):
        memory = list(baseline)
        memory[0xBFFE:0xC000] = [255, 63]
        memory[0xA78F:0xA791] = [0, 0]
        memory[0xE2B0], memory[0xE2BC] = 0, phase
        memory[0xA101], memory[0xA112], memory[0xA140], memory[0xA141] = 1, cls, 128, 128
        memory[0xA11B], memory[0xA11D], memory[0xA11F], memory[0x9C2B] = cx, height, cy, force
        expected = memory[0x4000:0x5800]
        rows = list(range(phase, 16)) + list(range(16)) * 4 + (list(range(16 - phase, 16)) if phase else [])
        for y, row in enumerate(rows, 104):
            address = pixel_address(64, y) - 0x4000
            expected[address:address + 10] = [85] * 10 if row == 15 else [128 if row % 2 == 0 else 0, 0] * 5

        def pixel(x, y):
            expected[pixel_address(x, y) - 0x4000] |= 128 >> (x & 7)

        for y, x in product((143, 144, 145), (103, 104, 105)):
            pixel(x, y)
        x, y = 104 + scale(signed(cx)), 144 + scale(-signed(cy))
        if cls not in (20, 21) and 128 not in (cx, height, cy) and 64 <= x < 141 and 107 <= y < 181:
            h = signed(height) // 4
            if h >= 0:
                for row in range(y, min(y + h, 181)):
                    pixel(x, row)
                glyph_y = y + h if y + h < 181 else None
            else:
                for row in range(y, max(y + h, 107), -1):
                    pixel(x, row)
                glyph_y = y + h - 2 if y + h >= 107 else y if y == 107 else None
            if glyph_y is not None:
                code = 1 if force else cls
                source = baseline[0xE65D + 2 * code] | baseline[0xE65E + 2 * code] << 8
                source += 6 * (x & 7)
                mask = ~(0xE000 >> (x & 7))
                for row in range(3):
                    address = pixel_address(x, glyph_y + row) - 0x4000
                    for byte, shift in ((0, 8), (1, 0)):
                        expected[address + byte] = (expected[address + byte] & ((mask >> shift) & 255)) | baseline[source + 2 * row + byte]
                counts['glyph'] += 1
            else:
                counts['clipped_stem'] += 1
        else:
            counts['skipped'] += 1
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0xE291, 'SP': 0xBFFE}, None, False)
        sim.run(0xE291, 0x3FFF)
        context = (phase, cx, height, cy, cls, force)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        actual = memory[0x4000:0x5800]
        assert actual == expected, (context, [(i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b][:12])
        counts['cases'] += 1
    assert counts['glyph'] and counts['skipped'] and counts['clipped_stem']
    report = dict(passed=True, total_cases=counts['cases'], outcomes=dict(counts),
                  whole_screen_bitmap_compared=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ControlsRadarLoopVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

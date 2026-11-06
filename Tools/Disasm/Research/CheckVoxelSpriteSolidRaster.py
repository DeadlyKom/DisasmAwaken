"""Скалярный эталон растра для одноцветного ресурса VOXAL."""
from collections import Counter
from itertools import product
import json

from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckVoxelEffectProjection import projection_memory


def main():
    baseline = projection_memory()
    counts = Counter()
    positions = ((-5, -3), (-1, -1), (0, 0), (1, 0), (6, 1), (7, 2),
                 (60, 21), (61, 22), (62, 23), (63, 23), (64, 24))
    for color, (x, y), width, height in product(range(16), positions, (1, 2, 3, 5, 12), (1, 2, 3, 6)):
        memory = baseline.copy()
        memory[0xD800:0xE400] = [color * 17] * 0xC00
        background = [(offset * 73 + color * 17) & 255 for offset in range(3072)]
        memory[0x8000:0x8C00] = background
        expected = background.copy()
        if color:
            for row in range(max(y, 0), min(y + height, 24)):
                for column in range(max(x, 0) // 2, (min(x + width, 64) + 1) // 2):
                    left = max(0, x) <= 2 * column < min(64, x + width)
                    right = max(0, x) <= 2 * column + 1 < min(64, x + width)
                    if not left and not right:
                        continue
                    index = color * (16 * left + right)
                    mask = (0 if left else 0xF0) | (0 if right else 0x0F)
                    for subrow, page in enumerate((0xC3, 0xC0, 0xC2, 0xC1)):
                        offset = row * 128 + subrow * 32 + column
                        expected[offset] = (expected[offset] & mask) | baseline[(page << 8) | index]
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0xEC7F, 'SP': 0xBFFE, 'HL': x & 65535,
                                         'DE': y & 65535, 'BC': height * 256 + width,
                                         '^HL': 0x0606, '^DE': 0xD800}, None, False)
        for _ in range(16000):
            if sim.registers[PC] == 0x3FFF:
                break
            sim.run()
        context = (color, x, y, width, height)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        actual = memory[0x8000:0x8C00]
        assert actual == expected, (context, [(i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b][:8])
        counts['transparent' if color == 0 else 'opaque'] += 1
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  uniform_source_only=True, all_3072_raster_bytes_compared=True,
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/VoxelSpriteSolidRasterVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

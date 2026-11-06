"""Выбор неоднородных кодов и растеризация VOXAL с шагом ресурса 16 или 32."""
import json
from itertools import product
from random import Random

from CheckEffects import run
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckVoxelEffectProjection import projection_memory


def divide_step(numerator, divisor):
    integer, remainder = divmod(numerator & 127, divisor)
    for _ in range(8):
        doubled = remainder * 2
        trial = (doubled & 255) - divisor - (doubled >> 8)
        restored = (trial & 255) + divisor if trial < 0 else trial
        integer = integer * 2 + (restored <= 255)
        remainder = restored & 255
    return integer


def raster(background, palette, resource, x, y, width, height, source_width, source_height):
    expected = background.copy()
    left, top = max(0, x), max(0, y)
    right, bottom = min(x + width, 64), min(y + height, 24)
    step_x, step_y = divide_step(source_width, width), divide_step(source_height, height)
    stride = 16 if source_width <= 16 else 32
    source_left = ((left - x) & 127) * step_x // 256
    source_top = ((top - y) & 127) * step_y // 256
    for row in range(top, bottom):
        source_row = source_top + (row - top) * step_y // 256
        for column in range(left // 2, (right + 1) // 2):
            codes = []
            for parity in (0, 1):
                pixel = 2 * column + parity
                if left <= pixel < right:
                    source_column = source_left + (pixel - left) * step_x // 256
                    code = resource[stride * source_row + source_column]
                    codes.append(code & 15 if parity else code >> 4)
                else:
                    codes.append(0)
            high, low = codes
            if not (high or low):
                continue
            mask = (0 if high else 240) | (0 if low else 15)
            for subrow, page in enumerate((0xC3, 0xC0, 0xC2, 0xC1)):
                offset = row * 128 + subrow * 32 + column
                expected[offset] = (expected[offset] & mask) | palette[(page << 8) | (16 * high + low)]
    return expected


def main():
    baseline = projection_memory()
    divider = Simulator(baseline.copy())
    for numerator, divisor in product(range(256), range(1, 256)):
        run(divider, {'PC': 0xF957, 'A': numerator, 'DE': divisor})
        assert divider.registers[4] * 256 + divider.registers[5] == divide_step(numerator, divisor)
    rng = Random(0xEC7F)
    positions = ((-5, -3), (-1, -1), (0, 0), (1, 0), (6, 1), (7, 2),
                 (60, 21), (61, 22), (62, 23), (63, 23), (64, 24))
    dimensions = (1, 2, 3, 4, 5, 6, 12, 17)
    total = 0
    source_sizes = ((6, 6), (10, 10), (5, 7), (16, 19), (17, 19), (20, 20))
    for (x, y), width, height, (source_width, source_height) in product(
            positions, dimensions, dimensions, source_sizes):
        memory = baseline.copy()
        resource = [rng.randrange(256) for _ in range(1024)]
        background = [rng.randrange(256) for _ in range(3072)]
        memory[0xD800:0xDC00] = resource
        memory[0x8000:0x8C00] = background
        expected = raster(background, baseline, resource, x, y, width, height, source_width, source_height)
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0xEC7F, 'SP': 0xBFFE, 'HL': x & 65535,
                                         'DE': y & 65535, 'BC': height * 256 + width,
                                         '^HL': source_height * 256 + source_width, '^DE': 0xD800}, None, False)
        for _ in range(20000):
            if sim.registers[PC] == 0x3FFF:
                break
            sim.run()
        context = (x, y, width, height, source_width, source_height)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        actual = memory[0x8000:0x8C00]
        assert actual == expected, (context, [(i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b][:8])
        total += 1
    report = dict(passed=True, total_cases=total, source_sizes=source_sizes, divider_pairs=65280,
                  all_3072_raster_bytes_compared=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/VoxelSpriteSampleRasterVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

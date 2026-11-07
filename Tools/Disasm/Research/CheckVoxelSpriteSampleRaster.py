"""Выбор неоднородных кодов и растеризация VOXAL с шагом ресурса 16 или 32."""
from collections import Counter
import json
from itertools import chain, product
from random import Random

from CheckEffects import run
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory
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


def raster(background, palette, resource, x, y, width, height, source_width, source_height, touched=None, edge_state=None):
    expected = background.copy()
    left, top = max(0, x), max(0, y)
    right, bottom = min(x + width, 64), min(y + height, 24)
    if right <= left or bottom <= top:
        return expected
    step_x, step_y = divide_step(source_width, width), divide_step(source_height, height)
    stride = 16 if source_width <= 16 else 32
    source_left = ((left - x) & 127) * step_x // 256
    source_top = ((top - y) & 127) * step_y // 256
    if edge_state is not None:
        edge_state['mask'] = (top * 128 + left // 2) & 255
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
            if edge_state is not None:
                edge_state['index'] = high * 16 + low
                if bool(high) != bool(low):
                    edge_state['mask'] = 15 if high else 240
            if not (high or low):
                continue
            mask = (0 if high else 240) | (0 if low else 15)
            for subrow, page in enumerate((0xC3, 0xC0, 0xC2, 0xC1)):
                offset = row * 128 + subrow * 32 + column
                if touched is not None:
                    touched.add(0x8000 + offset)
                expected[offset] = (expected[offset] & mask) | palette[(page << 8) | (16 * high + low)]
    return expected


def expected_patches(x, y, width, height, source_width, source_height):
    patches = []

    def byte(address, value):
        patches.append((address, value & 255))

    def word(address, value):
        byte(address, value)
        byte(address + 1, value >> 8)

    if not width or not height:
        return patches, None
    byte(0xED7E, 0)
    word(0xEC9D, x)
    word(0xECD2, y)
    left, top = max(0, x), max(0, y)
    right, bottom = min(64, x + width), min(24, y + height)
    if right <= left:
        return patches, None
    if x < 0:
        byte(0xED7E, -x)
    if bottom <= top:
        return patches, None
    parity = left & 1
    skip = 32 - ((right + 1) // 2 - left // 2)
    row_entry = 0xEE7A + 84 * skip
    stride = 16 if source_width <= 16 else 32
    step_y = divide_step(source_height, height)
    coarse_y = stride * (step_y >> 8)
    end_mask = 0 if right & 1 else 15
    byte(0xEE17, left)
    byte(0xEE4A, 0x38 if parity else 0x30)
    word(0xF92A, 0xBFFE)
    byte(0xF910, stride)
    byte(0xF918, coarse_y >> 8)
    byte(0xF8B5, end_mask)
    byte(0xF8DB, end_mask)
    word(0xF921, row_entry)
    if parity:
        byte(row_entry + 4, 0)
    word(0xEE78, row_entry + (3 if parity else 0))
    byte(0xF905, 0xA9 if skip & 1 else 0xE9)
    byte(0xF907, 0xC3 if skip & 1 else 0xC0)
    byte(row_entry + 4, 0xF0)

    rows = bottom - top
    source_left = ((left - x) & 127) * divide_step(source_width, width) // 256
    source_base = 0xD800 + source_left + stride * (((top - y) & 127) * step_y // 256)
    source_after = source_base + stride * (rows * step_y // 256)
    last_row = source_base + stride * ((rows - 1) * step_y // 256)
    last_sample = 2 * (32 - skip) - 1 - parity
    last_source = last_row + last_sample * divide_step(source_width, width) // 256
    next_destination = 0x8000 + bottom * 128 + left // 2
    if next_destination & 128:
        alternate_flags = next_destination & 0xA8
    else:
        next_high = next_destination >> 8
        alternate_flags = (next_high & 0xA8) | (16 if next_high & 15 == 0 else 0) | 1

    outputs = {
        0: rows * step_y & 255, 1: 0x42, 2: source_after & 255, 3: step_y & 255,
        4: source_after >> 8, 5: last_source & 255, 6: (row_entry + 4) >> 8, 7: (row_entry + 4) & 255,
        8: 0, 9: coarse_y & 255, 10: height, 11: next_destination & 255,
        16: next_destination & 255, 17: alternate_flags, 18: next_destination >> 8,
        19: (next_destination & 255) | (0 if skip & 1 else 32), 20: 15,
        22: 0xC3 if skip & 1 else 0xC0,
    }
    return patches, outputs


def main():
    baseline = projection_memory()
    divider = Simulator(baseline.copy())
    for numerator, divisor in product(range(256), range(1, 256)):
        run(divider, {'PC': 0xF957, 'A': numerator, 'DE': divisor})
        assert divider.registers[4] * 256 + divider.registers[5] == divide_step(numerator, divisor)
    rng = Random(0xEC7F)
    positions = ((-5, -3), (-1, -1), (0, 0), (1, 0), (6, 1), (7, 2),
                 (60, 21), (61, 22), (62, 23), (63, 23), (64, 24))
    dimensions = (0, 1, 2, 3, 4, 5, 6, 12, 17, 24, 64)
    total = 0
    patch_counts = Counter()
    stack_floor = 0xBFFE
    source_sizes = ((6, 6), (10, 10), (5, 7), (16, 19), (17, 19), (20, 20))
    general = product(positions, dimensions, dimensions, source_sizes)
    all_entries = (((x, 0), width, 1, (16, 6)) for x, width in product((0, 1), range(1, 65)))
    for (x, y), width, height, (source_width, source_height) in chain(general, all_entries):
        memory = Memory(baseline)
        resource = [rng.randrange(256) for _ in range(1024)]
        background = [rng.randrange(256) for _ in range(3072)]
        memory[0xD800:0xDC00] = resource
        memory[0x8000:0x8C00] = background
        touched = set()
        edge_state = {}
        expected = raster(background, baseline, resource, x, y, width, height, source_width, source_height,
                          touched, edge_state)
        memory.writes = []
        memory.recording = True
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0xEC7F, 'SP': 0xBFFE, 'HL': x & 65535,
                                         'DE': y & 65535, 'BC': height * 256 + width,
                                         '^HL': source_height * 256 + source_width, '^DE': 0xD800}, None, False)
        for _ in range(150000):
            if sim.registers[PC] == 0x3FFF:
                break
            sim.run()
        context = (x, y, width, height, source_width, source_height)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        actual = memory[0x8000:0x8C00]
        assert actual == expected, (context, [(i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b][:8])
        memory.recording = False
        writes = Counter(address for address, _ in memory.writes)
        assert {a: n for a, n in writes.items() if 0x8000 <= a < 0x8C00} == dict.fromkeys(touched, 1), context
        patches = {a: n for a, n in writes.items() if not 0x8000 <= a < 0x8C00 and not 0xBFF6 <= a < 0xBFFE}
        expected_code, outputs = expected_patches(*context)
        actual_code = [(address, value) for address, value in memory.writes if address in patches]
        assert actual_code == expected_code, (context, actual_code, expected_code)
        if outputs is not None:
            outputs[21], outputs[23] = edge_state['mask'], edge_state['index']
            assert all(sim.registers[i] == value for i, value in outputs.items()), (
                context, [(i, sim.registers[i], value) for i, value in outputs.items() if sim.registers[i] != value]
            )
        patch_counts.update(patches)
        stack_floor = min(stack_floor, *(a for a in writes if 0xBFF6 <= a < 0xBFFE), 0xBFFE)
        total += 1
    assert all(0xEE7E + 84 * group in patch_counts for group in range(32))
    report = dict(passed=True, total_cases=total, source_sizes=source_sizes, divider_pairs=65280,
                  all_3072_raster_bytes_compared=True, all_buffer_write_counts_compared=True,
                  observed_patch_write_counts={f'{a:04X}': n for a, n in sorted(patch_counts.items())},
                  observed_stack_floor=stack_floor, exact_code_write_order=True, all_32_raster_entries=True,
                  visible_primary_and_alternate_registers_checked=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/VoxelSpriteSampleRasterVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()

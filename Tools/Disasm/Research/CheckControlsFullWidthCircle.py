"""Полноширинные ветви D340/D34A и D38C/D396, полосы и остаточные половины."""
from collections import Counter
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks
from CheckControlsTextQueue import base_memory
from CheckControlsCircleDispatch import evaluate as dispatch, profiles as dispatch_profiles
from CheckControlsCircleSpan import add_flags
from CheckControlsClippedCircleHalf import pixel_oracle
from CheckControlsCornerCircleSlice import bit_flags
from CheckControlsVerticalCircleSlice import append_root_frame
from CheckControlsSixRowGauge import inc_flags
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsBcdExact import or_flags
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsCircleInteriorFull import evaluate_clipped_half

ENTRIES = (0xD340, 0xD34A, 0xD38C, 0xD396)


def reference(initial, radius, bits, center_y, mode, background):
    r = list(initial)
    entry, stack = r[24], r[12]
    work_x, work_y = r[2:4]
    whole = entry in (0xD340, 0xD34A)
    writes = []

    def word(address, value):
        writes.extend(((address, value & 255), (address + 1, value >> 8)))

    if entry in (0xD340, 0xD38C):
        work_x = (work_x + 120) & 255
        writes.append((0xD182, work_x))
        threshold, threshold_flags = 0, 0x44
    elif entry == 0xD34A:
        base = (136 + work_x) & 255
        threshold, threshold_flags = (base + 1) & 255, inc_flags(base) | int(136 + work_x > 255)
    else:
        threshold, threshold_flags = (work_x - 119) & 255, sub8_flags(work_x, 119)
    r[16:18] = [threshold, threshold_flags]
    root = append_root_frame(word, stack, 0xD355 if whole else 0xD3A4, (r[6] << 8) | r[7],
        (radius << 8) | bits, (work_x << 8) | work_y, (120 + work_x) & 255, add_flags(120, work_x))
    writes.append((0xD185, root))
    r[4:6] = [radius, bits]
    if whole:
        passes = ((-1, center_y, root, 0xD35F, 0xD362, 0xD365, 0xD36D, 0xD370),
                  (1, center_y, root, 0xD37A, 0xD37D, 0xD380, 0xD388, 0xD38B))
    elif bits & 2:
        passes = ((1, 0, (root - work_y) & 255, 0xD3B1, 0xD3B4, 0xD3B7, 0xD3BF, 0xD3C2),)
    else:
        passes = ((-1, 95, (root - work_y) & 255, 0xD3C8, 0xD3CB, 0xD3CE, 0xD3D6, 0xD3D9),)
    raster = [background] * 3072
    fill_rows = half_rows = skipped = 0
    for direction, row, count, fill_return, load_return, prep_return, left_return, right_return in passes:
        word(stack - 2, fill_return)
        word(0xD5B5, (direction * 32) & 65535)
        word(0xD600, 0x3880 if direction < 0 else 0x308C)
        word(stack - 4, (r[4] << 8) | r[5])
        word(stack - 6, (row << 8) | or_flags(mode) | 16)
        word(stack - 8, (count << 8) | row)
        lines = min(count, row + 1 if direction < 0 else 96 - row)
        for _ in range(lines):
            raster[32 * row + 1:32 * row + 31] = [r[9]] * 30
            r[9] ^= r[8]
            row += direction
        fill_rows += lines
        word(stack - 2, load_return)
        word(stack - 2, prep_return)
        row_address = 0x8000 + 32 * row
        r[2:4] = [0, 255]
        r[5:8] = [(row_address & 255) | 1, row_address >> 8, (row_address & 255) | 31]
        r[19], r[21] = (136 - work_x) & 255, root
        r[:2] = [bits, bit_flags(bits, 1)]
        side = 'right' if bits & 1 else 'left'
        word(stack - 2, right_return if side == 'right' else left_return)
        if not 0 <= row < 96:
            word(stack - 4, (r[0] << 8) | r[1])
            writes.append((0xD18B, int(direction > 0)))
            r[18], r[20], r[22], r[23] = 255, 0, 0, 0
            skipped += 1
            continue
        r[12] = stack - 2
        curve = 7 if side == 'right' else 248
        x = 120 + work_x
        pattern = (r[8] << 8) | r[9]
        result = evaluate_clipped_half(r, curve, row, x, root, direction, side, virtual_left=side == 'right')
        raster, fill, rows, reason, transitions = pixel_oracle(side, direction, x, root, curve, row, threshold, pattern, background, raster)
        r = result['registers']
        state = result['paths'][0]
        assert (r[9], state['rows'], state['reason'], state['transitions']) == (fill, rows, reason, transitions)
        writes.extend(result['writes'])
        half_rows += rows
    r[12], r[24] = stack + 2, 0x3FFF
    return r, writes, raster, fill_rows, half_rows, skipped


def main():
    flat = base_memory()
    banks = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    banks[5], banks[2], banks[1] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=banks, out7ffd=17)
    baseline = [bytearray(bank) for bank in memory.banks]
    simulator = Simulator(memory)
    counts = Counter()
    touched = set()
    total_fill = total_half = total_skipped = 0
    for x, y, radius, bits, _ in dispatch_profiles():
        if radius < 9:
            continue
        serial = counts.total()
        stack = (0x9008, 0xBFFE)[serial & 1]
        initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0, 'IY': 0x5C3A,
            'SP': stack, 'PC': 0xD236}, None, False)
        initial, setup, _ = dispatch(initial, x, y, radius, bits)
        if initial[24] not in ENTRIES:
            continue
        center_y = dict(setup)[0xD183]
        mode = (serial * 109) & 255
        initial[8:10] = [(serial * 73) & 255, (serial * 31) & 255]
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        background = serial & 255
        memory.banks[2][:3072] = bytes([background]) * 3072
        for address, value in setup + [(0xD17F, bits), (0xD180, radius), (0xD18C, mode), (stack, 255), (stack + 1, 63)]:
            memory[address] = value
        wanted, writes, raster, fill_rows, half_rows, skipped = reference(initial, radius, bits, center_y, mode, background)
        expected = [bytearray(bank) for bank in memory.banks]
        expected[2][:3072] = bytes(raster)
        expected_writes = []
        for address, value in writes:
            bank = 1 if address >= 0xC000 else 2
            offset = address & 0x3FFF
            expected[bank][offset] = value
            expected_writes.append((bank, offset, value))
        simulator.registers[:] = initial
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        simulator.run(start=initial[24], stop=0x3FFF)
        memory.recording = False
        compared = (*range(15), *range(16, 25), 26, 27)
        assert all(wanted[index] == simulator.registers[index] for index in compared), (serial, x, y, radius, bits, hex(initial[24]),
            [(index, wanted[index], simulator.registers[index]) for index in compared if wanted[index] != simulator.registers[index]])
        observed = [item for item in memory.writes if item[0] != 2 or item[1] >= 3072]
        assert Counter(expected_writes) == Counter(observed), (serial, 'nonpixel', Counter(expected_writes) - Counter(observed), Counter(observed) - Counter(expected_writes))
        assert all(a == b for a, b in zip(expected, memory.banks)), (serial, 'RAM')
        assert not trace.writes and memory.o7ffd == 17
        touched = {(bank, offset) for bank, offset, _ in memory.writes}
        counts[f'{initial[24]:04X}'] += 1
        total_fill += fill_rows
        total_half += half_rows
        total_skipped += skipped
    assert set(counts) == {f'{entry:04X}' for entry in ENTRIES} and total_skipped and total_half
    report = dict(passed=True, total_cases=counts.total(), cases_by_entry=dict(counts), full_rows=total_fill,
        clipped_rows=total_half, initial_outside_half_returns=total_skipped, exact_registers_except_R=True,
        all_physical_ram_bytes_proved=True, nonpixel_write_multiplicity_proved=True, all_real_children_without_stubs=True,
        profiles_from_verified_D236_boundary=True, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsFullWidthCircleVerification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

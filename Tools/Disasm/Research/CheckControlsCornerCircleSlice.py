"""Сечение с двумя видами отсечения, входы D404 и D40E из D236."""
from collections import Counter
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks
from CheckControlsTextQueue import base_memory
from CheckControlsCircleDispatch import evaluate as dispatch, profiles as dispatch_profiles
from CheckControlsClippedCircleHalf import pixel_oracle
from CheckControlsVerticalCircleSlice import append_root_frame
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsCircleInteriorFull import evaluate_clipped_half
from ReferenceControlsPointRespawn import cp_flags


def profiles():
    for work_y in range(9, 208):
        for side in range(4):
            yield 120, work_y + 48, work_y, 12 | side, 'zero_section_radius'
    for side in range(4):
        yield 0, 150, 170, 8 | side, 'exact_left_guard'
        yield 128, 48, 255, 12 | side, 'outer_columns'
    yield from dispatch_profiles()


def bit_flags(bits, mask, carry=0):
    return 16 | (bits & 0x28) | carry | (0 if bits & mask else 68)


def reference(initial, radius, bits, background):
    r = list(initial)
    stack = r[12]
    work_x, work_y = r[2:4]
    writes = []

    def word(address, value):
        writes.extend(((address, value & 255), (address + 1, value >> 8)))

    if r[24] == 0xD404:
        work_x = (work_x + 120) & 255
        writes.append((0xD182, work_x))
        threshold, threshold_flags = 0, 0x44
    else:
        threshold, threshold_flags = (work_x - 119) & 255, sub8_flags(work_x, 119)
    incoming_flags = r[17]
    r[16:18] = [threshold, threshold_flags]
    root = append_root_frame(word, stack, 0xD41A, (r[6] << 8) | r[7], (radius << 8) | bits,
                             (work_x << 8) | work_y, work_y, incoming_flags)
    writes.append((0xD185, root))
    r[2:6] = [work_x, work_y, radius, bits]
    r[19], r[21] = (-root) & 255, work_y
    direction = 1 if bits & 2 else -1
    row = 0 if direction > 0 else 95
    row_address = 0x8000 + 32 * row
    raster = [background] * 3072
    rows = 0

    if bits & 1:
        side = 'right'
        curve = (128 + work_x - root) & 255
        address = row_address + curve // 8
        mask = (255 << (7 - (curve & 7))) & 255
        word(stack - 2, 0xD43D)
        if curve // 8 == 31:
            r[:8] = [31, cp_flags(31, 31), mask, 31, radius, address & 255, address >> 8, address & 255]
            r[12], r[24] = stack + 2, 0x3FFF
            return r, writes, raster, rows, root, 'reject_right_column_31'
        r[2:8] = [mask, 255, radius, address & 255, address >> 8, (address & 255) | 31]
        return_address = 0xD455 if direction > 0 else 0xD458
    else:
        side = 'left'
        curve = (128 + root - work_x) & 255
        if curve < 8:
            r[:2] = [curve, cp_flags(curve, 8)]
            r[12], r[24] = stack + 2, 0x3FFF
            return r, writes, raster, rows, root, 'reject_left_before_pixel_8'
        address = row_address + curve // 8
        word(stack - 2, 0xD46D)
        word(stack - 4, (curve << 8) | bit_flags(bits, 2))
        writes.append((0xD18A, work_x))
        r[2:8] = [0, 255 >> (curve & 7), radius, (row_address & 255) | 1, address >> 8, address & 255]
        return_address = 0xD481 if direction > 0 else 0xD484

    r[:2] = [bits, bit_flags(bits, 2)]
    word(stack - 2, return_address)
    r[12] = stack - 2
    pattern = (r[8] << 8) | r[9]
    half = evaluate_clipped_half(r, curve, row, root, work_y, direction, side)
    raster, fill, rows, reason, transitions = pixel_oracle(side, direction, root, work_y, curve, row, threshold, pattern, background)
    r = half['registers']
    state = half['paths'][0]
    assert (r[9], state['rows'], state['reason'], state['transitions']) == (fill, rows, reason, transitions)
    writes.extend(half['writes'])
    r[12], r[24] = stack + 2, 0x3FFF
    path = side + ('_outer_column' if not 8 <= curve <= 247 else '_inside_columns')
    return r, writes, raster, rows, root, path


def main():
    flat = base_memory()
    banks = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    banks[5], banks[2], banks[1] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=banks, out7ffd=17)
    baseline = [bytearray(bank) for bank in memory.banks]
    simulator = Simulator(memory)
    paths, counts, entries = Counter(), Counter(), Counter()
    touched = set()
    total_rows = zero_roots = 0
    for x, y, radius, bits, kind in profiles():
        if radius < 9:
            continue
        serial = counts.total()
        stack = (0x9008, 0xBFFE)[serial & 1]
        initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0, 'IY': 0x5C3A,
            'SP': stack, 'PC': 0xD236}, None, False)
        initial, setup, _ = dispatch(initial, x, y, radius, bits)
        if initial[24] not in (0xD404, 0xD40E):
            continue
        initial[8:10] = [(serial * 73) & 255, (serial * 31) & 255]
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        background = serial & 255
        memory.banks[2][:3072] = bytes([background]) * 3072
        for address, value in setup + [(0xD17F, bits), (0xD180, radius), (0xD18C, (serial * 109) & 255), (stack, 255), (stack + 1, 63)]:
            memory[address] = value
        wanted, writes, raster, rows, root, path = reference(initial, radius, bits, background)
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
        assert all(wanted[index] == simulator.registers[index] for index in compared), (serial, x, y, radius, bits, root, path,
            [(index, wanted[index], simulator.registers[index]) for index in compared if wanted[index] != simulator.registers[index]])
        observed = [item for item in memory.writes if item[0] != 2 or item[1] >= 3072]
        assert Counter(expected_writes) == Counter(observed), (serial, 'nonpixel', Counter(expected_writes) - Counter(observed), Counter(observed) - Counter(expected_writes))
        assert all(a == b for a, b in zip(expected, memory.banks)), (serial, 'RAM')
        assert not trace.writes and memory.o7ffd == 17
        touched = {(bank, offset) for bank, offset, _ in memory.writes}
        paths[path] += 1
        counts[kind] += 1
        entries[f'{initial[24]:04X}'] += 1
        total_rows += rows
        zero_roots += int(root == 0)
    assert all(paths[path] for path in ('reject_right_column_31', 'reject_left_before_pixel_8', 'left_outer_column', 'right_outer_column'))
    report = dict(passed=True, total_cases=counts.total(), cases_by_kind=dict(counts), cases_by_entry=dict(entries), paths=dict(paths),
        modeled_rows=total_rows, zero_roots=zero_roots, exact_registers_except_R=True, all_physical_ram_bytes_proved=True,
        nonpixel_write_multiplicity_proved=True, all_real_children_without_stubs=True, maximum_additional_stack_bytes=14,
        profiles_from_verified_D236_boundary=True, full_D340_proved=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsCornerCircleSliceVerification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

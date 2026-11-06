"""D236 до внешнего RET, все десять рисующих выходов и отбрасывание до рисования."""
from collections import Counter
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks
from CheckControlsCircleDispatch import evaluate as dispatch, profiles as dispatch_profiles, BOUNDARIES
from CheckControlsCircleHalf import pixel_half
from CheckControlsCornerCircleSlice import reference as corner
from CheckControlsFullWidthCircle import reference as full_width, ENTRIES as FULL_WIDTH_ENTRIES
from CheckControlsHorizontalCircle import reference as horizontal
from CheckControlsTextQueue import base_memory
from CheckControlsVerticalCircleSlice import reference as vertical
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsCircleInteriorFull import evaluate as interior


def reference(initial, x, y, radius, bits, mode, background, pattern=0):
    registers, writes, path = dispatch(initial, x, y, radius, bits, pattern)
    target = registers[24]
    if target == 0x3FFF:
        return registers, writes, [background] * 3072, target, path
    center_y = 48 + (-y if bits & 2 else y)
    center_y &= 255
    center_x = (128 + (x if bits & 1 else -x)) & 255
    if target == 0xD314:
        result = interior(registers, center_x, center_y, radius)
        raster = [background] * 3072
        fill, _ = pixel_half(raster, center_x, center_y, radius, 0, -1, pattern & 255, pattern >> 8)
        pixel_half(raster, center_x, center_y, radius, 0, 1, fill, pattern >> 8)
        state, child_writes = result['registers'], result['writes']
    elif target == 0xD485:
        state, child_writes, raster, *_ = vertical(registers, registers[2], registers[3], radius, bits, center_x, background)
    elif target in (0xD404, 0xD40E):
        state, child_writes, raster, *_ = corner(registers, radius, bits, background)
    elif target in FULL_WIDTH_ENTRIES:
        state, child_writes, raster, *_ = full_width(registers, radius, bits, center_y, mode, background)
    else:
        assert target in (0xD3DA, 0xD3E4)
        state, child_writes, raster, *_ = horizontal(registers, target, registers[2], radius, center_y, bits, mode, background)
    return state, writes + child_writes, raster, target, path


def profiles():
    for work_y in (9, 64, 119, 207):
        for signs in range(4):
            yield 120, work_y + 48, work_y, 12 | signs
            yield 0, work_y + 48, work_y, 12 | signs
    for x, y, radius, bits, _ in dispatch_profiles():
        if radius >= 9:
            yield x, y, radius, bits


def main():
    flat = base_memory()
    banks = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    banks[5], banks[2], banks[1] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=banks, out7ffd=17)
    baseline = [bytearray(bank) for bank in memory.banks]
    simulator = Simulator(memory)
    targets, paths = Counter(), Counter()
    touched = set()
    maximum_stack = 0
    for index, (x, y, radius, bits) in enumerate(profiles()):
        serial = targets.total()
        stack = (0x9008, 0xBFFE)[serial & 1]
        initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x5C3A,
            'SP': stack, 'PC': 0xD236}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        boundary, _, path = dispatch(initial, x, y, radius, bits)
        if paths[path] >= 384 and index % 257:
            continue
        mode, background = (serial * 109) & 255, (serial * 73) & 255
        pattern = (serial * 307) & 65535
        wanted, writes, raster, target, path = reference(initial, x, y, radius, bits, mode, background, pattern)
        assert target == boundary[24]
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        memory.banks[2][:3072] = bytes([background]) * 3072
        for address, value in ((0xD17D, y), (0xD17E, x), (0xD17F, bits), (0xD180, radius),
                               (0xD18C, mode), (0xD240, pattern & 255), (0xD241, pattern >> 8),
                               (stack, 255), (stack + 1, 63)):
            memory[address] = value
        expected = [bytearray(bank) for bank in memory.banks]
        expected[2][:3072] = bytes(raster)
        expected_writes = []
        for address, value in writes:
            bank = 1 if address >= 0xC000 else 2
            offset = address & 0x3FFF
            expected[bank][offset] = value
            expected_writes.append((bank, offset, value))
            if bank == 2:
                maximum_stack = max(maximum_stack, stack - address)
        simulator.registers[:] = initial
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        simulator.run(start=0xD236, stop=0x3FFF)
        memory.recording = False
        compared = (*range(15), *range(16, 25), 26, 27)
        assert all(wanted[reg] == simulator.registers[reg] for reg in compared), (serial, x, y, radius, bits, path,
            [(reg, wanted[reg], simulator.registers[reg]) for reg in compared if wanted[reg] != simulator.registers[reg]])
        observed = [item for item in memory.writes if item[0] != 2 or item[1] >= 3072]
        assert Counter(expected_writes) == Counter(observed), (serial, 'nonpixel', path)
        assert all(a == b for a, b in zip(expected, memory.banks)), (serial, 'RAM', path)
        assert not trace.writes and memory.o7ffd == 17
        touched = {(bank, offset) for bank, offset, _ in memory.writes}
        paths[path] += 1
        targets[f'{target:04X}'] += 1
    assert set(targets) == {f'{address:04X}' for address in BOUNDARIES} and maximum_stack == 14
    report = dict(passed=True, total_cases=targets.total(), cases_by_destination=dict(targets), paths=dict(paths),
        every_original_destination=True, actual_original_children_without_stubs=True, exact_registers_except_R=True,
        all_physical_ram_bytes_proved=True, nonpixel_write_multiplicity_proved=True, maximum_additional_stack_bytes=maximum_stack,
        initial_projection_record_required=True, original_self_modified_pattern_exercised=True,
        radius_minimum=9, full_input_product_exhausted=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsLargeCircleVerification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

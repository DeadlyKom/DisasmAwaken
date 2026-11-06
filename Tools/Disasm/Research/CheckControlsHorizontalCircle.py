"""Входы D3DA и D3E4, две реальные половины с одним горизонтальным отсечением."""
from collections import Counter
import json
import random

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks
from CheckControlsTextQueue import base_memory
from CheckControlsClippedCircleHalf import pixel_oracle
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsBcdExact import or_flags
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsCircleInteriorFull import evaluate_clipped_half


def profiles():
    for radius in range(9, 256):
        for work_x in range(256):
            if 0 < radius - work_x < 240:
                yield 0xD3DA, work_x, radius, (radius + work_x) % 96, (radius ^ work_x) & 1, 'outside_pairs'
            if work_x < 120 and work_x + radius >= 120 and radius - work_x < 120:
                yield 0xD3E4, work_x, radius, (radius * 73 + work_x) % 96, (radius ^ work_x) & 1, 'inside_pairs'
    randomizer = random.Random(0xD3DA)
    for _ in range(4096):
        radius = randomizer.randrange(9, 256)
        work_x = randomizer.randrange(max(0, radius - 239), radius)
        yield 0xD3DA, work_x, radius, randomizer.randrange(96), randomizer.randrange(256), 'mixed_outside'


def reference(initial, entry, work_x, radius, row, flags, mode, background):
    registers = list(initial)
    stack = registers[12]
    writes = []

    def word(address, value):
        writes.extend(((address, value & 255), (address + 1, value >> 8)))

    if entry == 0xD3DA:
        work_x = (work_x + 120) & 255
        writes.append((0xD182, work_x))
        threshold, threshold_flags = 0, 0x44
    else:
        threshold, threshold_flags = (work_x - 119) & 255, sub8_flags(work_x, 119)
    registers[16:18] = [threshold, threshold_flags]
    side = 'right' if flags & 1 else 'left'
    raster = [background] * 3072
    row_count = 0
    transitions = 0
    if side == 'right':
        curve = (128 + work_x - radius) & 255
        left, right = curve, 248
        masks = [(255 << (7 - (curve & 7))) & 255, 255]
        prep_returns = (0xD3EF, 0xD3F5)
        down_return = 0xD3F2
    else:
        curve = (128 + radius - work_x) & 255
        left, right = 8, curve
        masks = [0, 255 >> (curve & 7)]
        prep_returns = (0xD3FB, 0xD401)
        down_return = 0xD3FE
    assert 8 <= curve <= 247
    left_address = 0x8000 + 32 * row + left // 8
    right_address = 0x8000 + 32 * row + right // 8
    for direction, prep_return in zip((1, -1), prep_returns):
        word(stack - 2, prep_return)
        if side == 'right':
            word(stack - 4, 0xD4CE)
            word(stack - 4, 0xD4D9)
            a = right_address & 255
            f = or_flags(a)
        else:
            word(stack - 4, 0xD4E7)
            word(stack - 4, 0xD4F2)
            word(stack - 6, (curve << 8) | sub8_flags((128 + radius) & 255, work_x))
            writes.append((0xD18A, work_x))
            a = left_address & 255
            f = or_flags(mode) | 16
        registers[0:8] = [a, f, *masks, radius, left_address & 255, right_address >> 8, right_address & 255]
        registers[19], registers[21] = (-radius) & 255, 0
        registers[12] = stack
        if direction > 0:
            word(stack - 2, down_return)
            registers[12] -= 2
        pattern = (registers[8] << 8) | registers[9]
        half = evaluate_clipped_half(registers, curve, row, radius, 0, direction, side)
        raster, fill, rows, reason, changed = pixel_oracle(side, direction, radius, 0, curve, row, threshold, pattern, background, raster)
        state = half['paths'][0]
        registers = half['registers']
        assert (registers[9], state['rows'], state['reason'], state['transitions']) == (fill, rows, reason, changed)
        writes.extend(half['writes'])
        row_count += rows
        transitions += changed
    return registers, writes, raster, row_count, transitions


def main():
    flat = base_memory()
    banks = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    banks[5], banks[2], banks[1] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=banks, out7ffd=17)
    baseline = [bytearray(bank) for bank in memory.banks]
    simulator = Simulator(memory)
    counts, sides = Counter(), Counter()
    touched = set()
    total_rows = total_transitions = 0
    for entry, work_x, radius, row, flags, kind in profiles():
        serial = counts.total()
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        stack = (0x9008, 0xBFFE)[serial & 1]
        mode = (serial * 73) & 255
        background = (serial * 109) & 255
        memory.banks[2][:3072] = bytes([background]) * 3072
        for address, value in ((0xD17F, flags), (0xD180, radius), (0xD181, 48), (0xD182, work_x),
                               (0xD183, row), (0xD18C, mode), (stack, 255), (stack + 1, 63)):
            memory[address] = value
        initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': (radius << 8) | flags,
            'BC': (work_x << 8) | 48, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0,
            'IX': (serial * 307) & 65535, 'IY': 0x5C3A, 'SP': stack, 'PC': entry}, None, False)
        wanted, writes, raster, rows, transitions = reference(initial, entry, work_x, radius, row, flags, mode, background)
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
        simulator.run(start=entry, stop=0x3FFF)
        memory.recording = False
        compared = (*range(15), *range(16, 25), 26, 27)
        assert all(wanted[index] == simulator.registers[index] for index in compared), (serial, hex(entry), work_x, radius, row, flags,
            [(index, wanted[index], simulator.registers[index]) for index in compared if wanted[index] != simulator.registers[index]])
        observed_writes = [item for item in memory.writes if item[0] != 2 or item[1] >= 3072]
        assert Counter(expected_writes) == Counter(observed_writes), (serial, 'nonpixel', Counter(expected_writes) - Counter(observed_writes), Counter(observed_writes) - Counter(expected_writes))
        assert all(a == b for a, b in zip(expected, memory.banks)), (serial, 'RAM')
        assert not trace.writes and memory.o7ffd == 17
        touched = {(bank, offset) for bank, offset, _ in memory.writes}
        counts[kind] += 1
        sides[f'{entry:04X}_' + ('right' if flags & 1 else 'left')] += 1
        total_rows += rows
        total_transitions += transitions
        if counts.total() % 8192 == 0:
            print(f'{counts.total()} cases passed', flush=True)
    report = dict(passed=True, total_cases=counts.total(), cases_by_kind=dict(counts), cases_by_entry_and_side=dict(sides),
        modeled_rows=total_rows, transitions_to_unclipped_kernel=total_transitions, exact_registers_except_R=True,
        all_physical_ram_bytes_proved=True, nonpixel_write_multiplicity_proved=True, two_real_preparations_and_halves=True,
        upward_half_tail_jump=True, full_D340_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsHorizontalCircleVerification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

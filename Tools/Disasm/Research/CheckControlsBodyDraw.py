"""D21A/D232, реальный выбор малого или большого рисователя после CP 09."""
from collections import Counter
import json
import random

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks
from CheckControlsCircleDispatch import evaluate as dispatch, profiles as dispatch_profiles
from CheckControlsLargeCircle import reference as large
from CheckControlsSmallBodies import reference as small
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import cp_flags


def reference(banks, initial, x, y, radius, flags, small_mode, large_mode, pattern, background):
    r = list(initial)
    stack = r[12]
    writes = []
    if r[24] in (0xD21A, 0xD227):
        primary = r[24] == 0xD227
        flat = bytearray(0x4000) + banks[5] + banks[2] + banks[1]
        writes.extend(((stack - 2, 0x2A if primary else 0x1D), (stack - 1, 0xD2)))
        child = list(r)
        child[12] -= 2
        r, _, local_writes, path = small(flat, radius, small_mode, x, y, flags, pattern, child, primary=primary)
        for address, value in local_writes:
            if 0xBFF8 <= address <= 0xBFFD:
                address += stack - 0xBFFE - 2
            writes.append((address, value))
        r[1] = cp_flags(r[0], 9)
        if r[0] < 9:
            r[12], r[24] = stack + 2, 0x3FFF
            return r, writes, flat[0x8000:0x8C00], 'small_'+path
        large_mode = int(primary)
        r[:2] = [large_mode, r[1] if primary else 0x44]
        writes.append((0xD18C, large_mode))
    writes.extend(((stack - 2, 0x35), (stack - 1, 0xD2)))
    r[12], r[24] = stack - 2, 0xD236
    state, local_writes, raster, _, path = large(r, x, y, radius, flags, large_mode, background, pattern)
    state[12], state[24] = stack + 2, 0x3FFF
    return state, writes + local_writes, raster, 'large_'+path


def profiles():
    for mode in (0, 1, 2, 3, 4, 255):
        for radius in range(9):
            for x in (0, 1, 119, 120, 127, 128, 255):
                for y in (0, 1, 47, 48, 72, 73, 255):
                    for flags in range(16):
                        yield 0xD21A, x, y, radius, flags, mode
    selected = Counter()
    dummy = get_registers({'SP': 0xBFFE, 'PC': 0xD236}, None, False)
    for x, y, radius, flags, _ in dispatch_profiles():
        if radius < 9:
            continue
        _, _, path = dispatch(dummy, x, y, radius, flags)
        if selected[path] < 64:
            selected[path] += 1
            yield 0xD21A, x, y, radius, flags, selected[path] & 255
            yield 0xD232, x, y, radius, flags, selected[path] & 255
    generator = random.Random(0xD21A)
    for _ in range(2048):
        yield 0xD21A, *(generator.randrange(256) for _ in range(5))


def main():
    flat = base_memory()
    banks = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    banks[5], banks[2], banks[1] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=banks, out7ffd=17)
    baseline = [bytearray(bank) for bank in memory.banks]
    simulator = Simulator(memory)
    counts, entries = Counter(), Counter()
    touched = set()
    standard = list(profiles())
    primary_profiles = [(0xD227, *case[1:]) for case in standard if case[0] == 0xD21A]
    for entry, x, y, radius, flags, mode in standard + primary_profiles:
        serial = counts.total()
        stack = (0x9008, 0xBFFE)[serial & 1]
        pattern, background = (serial * 307) & 65535, (serial * 73) & 255
        large_mode = (serial * 109) & 255
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        memory.banks[2][:3072] = bytes([background]) * 3072
        for address, value in ((0xD17D, y), (0xD17E, x), (0xD17F, flags), (0xD180, radius),
                               (0xD18C, large_mode), (0xCEF9, mode), (0xD240, pattern & 255), (0xD241, pattern >> 8),
                               (stack, 255), (stack + 1, 63)):
            memory[address] = value
        initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x5C3A,
            'SP': stack, 'PC': entry}, None, False)
        wanted, writes, raster, path = reference(memory.banks, initial, x, y, radius, flags, mode, large_mode, pattern, background)
        expected = [bytearray(bank) for bank in memory.banks]
        expected[2][:3072] = bytes(raster)
        nonpixel = []
        for address, value in writes:
            bank = 1 if address >= 0xC000 else 2 if address >= 0x8000 else 5
            offset = address & 0x3FFF
            expected[bank][offset] = value
            if bank != 2 or offset >= 3072:
                nonpixel.append((bank, offset, value))
        simulator.registers[:] = initial
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        simulator.run(start=entry, stop=0x3FFF)
        memory.recording = False
        compared = (*range(15), *range(16, 25), 26, 27)
        assert all(wanted[reg] == simulator.registers[reg] for reg in compared), (serial, hex(entry), radius, x, y, flags, mode, path,
            [(reg, wanted[reg], simulator.registers[reg]) for reg in compared if wanted[reg] != simulator.registers[reg]])
        observed = [item for item in memory.writes if item[0] != 2 or item[1] >= 3072]
        assert Counter(nonpixel) == Counter(observed), (serial, 'nonpixel', path)
        assert all(a == b for a, b in zip(expected, memory.banks)), (serial, 'RAM', path)
        assert not trace.writes and memory.o7ffd == 17
        touched = {(bank, offset) for bank, offset, _ in memory.writes}
        counts[path] += 1
        entries[f'{entry:04X}'] += 1
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), cases_by_entry=dict(entries),
        original_small_and_large_children_without_stubs=True, exact_registers_except_R=True,
        all_physical_ram_bytes_proved=True, nonpixel_write_multiplicity_proved=True,
        large_fallback_mode_by_entry={'D21A': 0, 'D227': 1}, alternate_small_entry_at_operand=True,
        actual_large_call_frame_preserved=True,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsBodyDrawVerification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

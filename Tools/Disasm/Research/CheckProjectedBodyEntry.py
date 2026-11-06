"""CEFA и банковая обёртка 6C7E, проекция, выбор профиля и реальные записи в 7FFD."""
from collections import Counter
import json
import sys

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionPatchedVector import OUTPUTS
from CheckControlsBodyDraw import reference as draw
from CheckControlsBodyProjection import profiles as projection_profiles
from CheckControlsProjectionGate import evaluate as gate
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsBcdExact import or_flags


def profiles():
    for mode, signs, components, kind in projection_profiles():
        if mode != 0:
            continue
        if kind == 'all_radius_depth_words' and (components[2] >> 8) % 61:
            continue
        yield signs, components, kind


def physical(address):
    return (1 if address >= 0xC000 else 2 if address >= 0x8000 else 5, address & 0x3FFF)


def main(transformed=False):
    flat = flat_action()
    baseline = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    baseline[1] = bytearray(base_memory()[0xC000:])
    memory = RecordedBanks(banks=[bytearray(bank) for bank in baseline], out7ffd=17)
    simulator = Simulator(memory)
    counts, paths, modes = Counter(), Counter(), Counter()
    max_stack = 0
    compared = (*range(15), *range(16, 25), 26, 27)
    for signs, components, kind in profiles():
        for banked in ((True,) if transformed else (False, True)):
            serial = counts.total()
            stack = (0x9008, 0xBFFE)[(serial >> 1) & 1]
            entry = 0x6AB0 if transformed else 0x6C7E if banked else 0xCEFA
            old_page = (serial & 3) << 3 if transformed else (serial >> 1) & 31 if banked else 17
            initial_pattern = (serial * 307) & 65535
            mode_code = (serial * 73) & 255
            pattern = (255 if mode_code == 2 else 0) if transformed else 0xFFAA if banked else initial_pattern
            background = serial & 255
            memory.recording = False
            for bank in (1, 2, 5):
                memory.banks[bank][:] = baseline[bank]
            memory.out7ffd(old_page)
            memory.banks[2][:3072] = bytes([background]) * 3072
            for index, component in enumerate(components):
                encoded = (component | (((signs >> index) & 1) << 23)) & 0xFFFFFF
                for offset, value in enumerate(encoded.to_bytes(3, 'little')):
                    memory[0x9B1E + 3 * index + offset] = value
            transform_writes = []
            if transformed:
                memory[0x9B81] = mode_code
                for index, address in enumerate(OUTPUTS):
                    encoded = ((components[index] >> 8) & 0x7FFF) | (((signs >> index) & 1) << 15)
                    memory[address], memory[address + 1] = encoded & 255, encoded >> 8
                    memory[0x9B1E + 3 * index] = 0
                    transform_writes.append((0x9B8A + index, encoded >> 8))
                    if index == 1:
                        encoded = (-encoded) & 65535
                    if encoded & 0x8000:
                        encoded = ((-encoded) & 65535) | 0x8000
                    component_address = 0x9B1F + 3 * index
                    transform_writes.extend(((component_address, encoded & 255), (component_address + 1, encoded >> 8)))
            for address, value in ((stack, 255), (stack + 1, 63), (0xCEF9, serial & 255), (0xD18C, (serial * 73) & 255)):
                memory[address] = value
            initial = get_registers({'AF': (serial & 65535) & (~4 if transformed else 65535), 'HL': 0x1357, 'DE': initial_pattern, 'BC': 0x369C,
                '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x5C3A,
                'SP': stack, 'PC': entry}, None, False)
            initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
            cefa_sp = stack - 2 if banked else stack
            gate_sp = cefa_sp - 2
            prefix = list(transform_writes)

            def word(log, address, value):
                log.extend(((address, value & 255), (address + 1, value >> 8)))

            if banked:
                word(prefix, stack - 2, 0x6B0D if transformed else 0x6C86)
                word(prefix, stack - 4, (initial[2] << 8) | initial[3])
                word(prefix, stack - 2, 0x6B10 if transformed else 0x6C89)
            word(prefix, 0xD240, pattern)
            prefix.append((0xCEF9, 0))
            word(prefix, gate_sp, 0xCF05)
            input_banks = [bytearray(bank) for bank in memory.banks]
            for address, value in prefix:
                bank, offset = physical(address)
                input_banks[bank][offset] = value
            gate_initial = list(initial)
            gate_initial[:2] = [0, 0x44]
            gate_initial[4:6] = [pattern >> 8, pattern & 255]
            if transformed:
                gate_initial[6:8] = [transform_writes[-1][1], transform_writes[-2][1]]
            gate_initial[12], gate_initial[24] = gate_sp, 0xD95F
            projected, _, gate_path = gate(input_banks, gate_initial)
            projected.r[24] = 0xCF05
            simulator.registers[:] = initial
            trace = PortTrace(simulator)
            simulator.set_tracer(trace)
            memory.writes = []
            memory.recording = True
            simulator.run(start=entry, stop=0xCF05)
            memory.recording = False
            assert all(projected.r[reg] == simulator.registers[reg] for reg in compared), (serial, gate_path, 'gate_registers')
            scratch = {physical(address) for address in range(gate_sp - 8, gate_sp)}
            prefix_writes = [(*physical(address), value) for address, value in prefix] + projected.writes
            assert Counter(item for item in memory.writes if item[:2] not in scratch) == Counter(prefix_writes), (serial, 'gate_writes')
            for bank, offset in scratch:
                projected.banks[bank][offset] = memory.banks[bank][offset]
            assert all(a == b for a, b in zip(projected.banks, memory.banks)), (serial, 'gate_RAM')
            assert trace.writes == ([(0x7FFD, 0x11)] if banked else [])

            expected = projected.banks
            r = projected.r
            r[1] = or_flags(r[0]) | 16
            suffix = []
            if r[0]:
                word(suffix, cefa_sp - 2, 0xCF0A)
                r[12], r[24] = cefa_sp - 2, 0xD21A
                y, x, flags, radius = (projected.read(address) for address in range(0xD17D, 0xD181))
                r, writes, raster, draw_path = draw(expected, r, x, y, radius, flags, 0, projected.read(0xD18C), pattern, background)
                expected[2][:3072] = bytes(raster)
                suffix.extend(writes)
                paths[draw_path] += 1
            else:
                paths[gate_path] += 1
            if banked:
                word(suffix, stack - 2, 0x6B15 if transformed else 0x6C8E)
                word(suffix, stack - 4, (r[2] << 8) | r[3])
                r[0] = 0x10
            r[12], r[24] = stack + 2, 0x3FFF
            suffix_writes = []
            for address, value in suffix:
                bank, offset = physical(address)
                expected[bank][offset] = value
                if bank != 2 or offset >= 3072:
                    suffix_writes.append((bank, offset, value))
                if 0x8C00 <= address < stack:
                    max_stack = max(max_stack, stack - address)
            memory.writes = []
            memory.recording = True
            simulator.run(start=0xCF05, stop=0x3FFF)
            memory.recording = False
            assert all(r[reg] == simulator.registers[reg] for reg in compared), (serial, 'final_registers',
                [(reg, r[reg], simulator.registers[reg]) for reg in compared if r[reg] != simulator.registers[reg]])
            observed = [item for item in memory.writes if item[0] != 2 or item[1] >= 3072]
            assert Counter(observed) == Counter(suffix_writes), (serial, 'draw_writes')
            assert all(a == b for a, b in zip(expected, memory.banks)), (serial, 'final_RAM')
            assert trace.writes == ([(0x7FFD, 0x11), (0x7FFD, 0x10)] if banked else [])
            assert memory.o7ffd == (16 if banked else 17)
            counts[f'{entry:04X}'] += 1
            modes[kind] += 1
    assert max_stack == 20 and any(path.startswith('small_') for path in paths) and any(path.startswith('large_') for path in paths)
    overflow_returns = 0
    if transformed:
        memory.recording = False
        memory.out7ffd(16)
        memory[0xBFFE], memory[0xBFFF] = 255, 63
        before = [bytearray(bank) for bank in memory.banks]
        for af in range(65536):
            if not af & 4:
                continue
            initial = get_registers({'AF': af, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
                '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x6AAD,
                'SP': 0xBFFE, 'PC': 0x6AB0}, None, False)
            expected = list(initial)
            expected[12], expected[24] = 0xC000, 0x3FFF
            simulator.registers[:] = initial
            trace = PortTrace(simulator)
            simulator.set_tracer(trace)
            memory.writes = []
            memory.recording = True
            simulator.run(start=0x6AB0, stop=0x3FFF)
            memory.recording = False
            assert all(expected[reg] == simulator.registers[reg] for reg in compared)
            assert not trace.writes and not memory.writes and memory.o7ffd == 16
            overflow_returns += 1
        assert all(a == b for a, b in zip(before, memory.banks))
    report = dict(passed=True, total_cases=counts.total() + overflow_returns, cases_by_entry=dict(counts), paths=dict(paths), cases_by_profile=dict(modes),
        exact_registers_except_R=True, actual_children_without_stubs=True, all_RAM_except_projection_scratch=True,
        projection_scratch_values_not_proved=True, complete_nonpixel_write_multiplicity_after_projection=True,
        mode_forced_zero=True, banked_pattern_FFAA=not transformed, actual_out_sequence=[17, 16], maximum_banked_stack_bytes=max_stack,
        assembly_executed=False, irq_executed=False, native_execution=False)
    name = 'ActionPublishBodyTransform' if transformed else 'ProjectedBodyEntry'
    if transformed:
        report.update(overflow_returns=overflow_returns, signed_high_bytes_saved_before_conversion=True,
                      second_component_negated=True, pattern_FF_only_for_mode_two=True)
    (ROOT / ('Tools/Disasm/Reports/' + name + 'Verification.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main('--transformed' in sys.argv)

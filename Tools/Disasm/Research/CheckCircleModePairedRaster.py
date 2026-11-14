"""Парные запуски исходного D236 с одинаковой геометрией и разным Mode."""
from collections import Counter
from array import array
from hashlib import sha256
import json

from CheckControlsLargeCircle import profiles, dispatch, BOUNDARIES
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from CheckIntro import ROOT
from CheckStationFlightCycle import payload


def mode_flags(mode):
    # Флаги AND A для полного байта Mode, включая недокументированные биты.
    return (mode & 0xA8) | 0x10 | (0x40 if mode == 0 else 0) | (4 if mode.bit_count() % 2 == 0 else 0)


class LocatedWrites(RecordedBanks):
    def __getitem__(self, index):
        value = super().__getitem__(index)
        if self.recording:
            assert isinstance(index, int)
            self.read_trace.append((self.cpu.registers[24] << 16) | index)
            self.read_values.append(value)
        return value

    def __setitem__(self, index, value):
        if self.recording:
            # PC снимается до обновления этой инструкции в используемом симуляторе.
            self.write_sites.append((self.cpu.registers[24], self.cpu.registers[12]))
        super().__setitem__(index, value)


def main():
    flat = base_memory()
    banks = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    banks[5] = bytearray(flat[0x4000:0x8000])
    banks[2] = bytearray(flat[0x8000:0xC000])
    banks[1] = bytearray(flat[0xC000:])
    memory = LocatedWrites(banks=banks, out7ffd=17)
    baseline = [bytearray(bank) for bank in memory.banks]
    simulator = Simulator(memory)
    memory.cpu = simulator
    initial = get_registers({'AF': 0x1357, 'HL': 0x1357, 'DE': 0x2468,
        'BC': 0x369C, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
        '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE,
        'PC': 0xD236}, None, False)
    selected = {target: [] for target in BOUNDARIES}
    seen = set()
    # Подбор разных геометрий для каждого исходного назначения диспетчера.
    for profile in profiles():
        if profile in seen:
            continue
        seen.add(profile)
        target = dispatch(initial, *profile)[0][24]
        if len(selected[target]) < 8:
            selected[target].append(profile)
        if all(len(items) == 8 for items in selected.values()):
            break
    assert all(len(items) == 8 for items in selected.values())
    destinations, differing_registers, flag_differences = Counter(), Counter(), Counter()
    raster_digest = sha256()
    flag_write_sites, final_flag_addresses = Counter(), Counter()
    permitted_flag_pushes = {0xD1B6, 0xD1CB, 0xD5A2}
    original = payload(22)
    restore_tails = {0xD606: bytes.fromhex('F1D1C9'), 0xD7C0: bytes.fromhex('F1C9'),
                     0xD93E: bytes.fromhex('F1C9'), 0xD959: bytes.fromhex('F1C9')}
    # После снятия зависимого F каждый известный хвост сразу возвращается, POP DE флаги не меняет.
    assert all(original[site - 0xC000:site - 0xC000 + len(raw)] == raw
               for site, raw in restore_tails.items())
    # Проверка физических PUSH AF, которым разрешено сохранять флаги AND Mode.
    assert all(original[site - 0xC000] == 0xF5 for site in permitted_flag_pushes)
    all_mode_groups = 0
    all_mode_profiles = []
    compared_write_events = 0
    compared_read_events = 0
    compared_instruction_events = 0
    differing_read_sites = Counter()
    runs = 0
    # Стек и фон меняются между парами, внутри пары меняется только Mode.
    for target, geometries in sorted(selected.items()):
        for index, (x, y, radius, bits) in enumerate(geometries):
            for pattern in (0x0000, 0xFFFF, 0x55AA, 0x1234):
                background = (index * 73 + pattern) & 255
                stack = (0x9008, 0xBFFE)[index & 1]
                results = []
                modes = tuple(range(256)) if index == 0 and pattern == 0 else (0, 1, 0x80, 0xFF)
                all_mode_groups += len(modes) == 256
                if len(modes) == 256:
                    all_mode_profiles.append(dict(target=target, x=x, y=y, radius=radius,
                        bits=bits, pattern=pattern, stack=stack, background=background))
                for mode in modes:
                    memory.recording = False
                    for bank in range(8):
                        memory.banks[bank][:] = baseline[bank]
                    memory.banks[2][:3072] = bytes([background]) * 3072
                    for address, value in ((0xD17D, y), (0xD17E, x),
                            (0xD17F, bits), (0xD180, radius), (0xD18C, mode),
                            (0xD240, pattern & 255), (0xD241, pattern >> 8),
                            (stack, 255), (stack + 1, 63)):
                        memory[address] = value
                    simulator.registers[:] = initial
                    simulator.registers[12] = stack
                    trace = PortTrace(simulator)
                    simulator.set_tracer(trace)
                    memory.writes = []
                    memory.write_sites = []
                    memory.read_trace = array('I')
                    memory.read_values = bytearray()
                    commands = array('H')
                    memory.recording = True
                    # Трассы хранятся компактно в RAM, исходный код выполняется до полного возврата.
                    for _ in range(100000):
                        pc = simulator.registers[24]
                        if pc == 0x3FFF:
                            break
                        commands.append(pc)
                        simulator.run()
                    else:
                        raise AssertionError(('нет возврата', target, mode, simulator.registers[24]))
                    memory.recording = False
                    assert not trace.writes and memory.o7ffd == 17
                    assert simulator.registers[12] == stack + 2
                    pixels = [item for item in memory.writes
                              if item[0] == 2 and item[1] < 3072]
                    results.append((bytes(memory.banks[2][:3072]), pixels,
                                    list(simulator.registers),
                                    [bytes(bank) for bank in memory.banks],
                                    list(zip(memory.write_sites, memory.writes)),
                                    commands, memory.read_trace, memory.read_values))
                    runs += 1
                first_raster, first_writes, first_registers, first_banks, first_events, first_commands, first_reads, first_values = results[0]
                # Сверка конечных пикселей и полного порядка пиксельных записей.
                for mode, (raster, writes, registers, banks, events, commands, reads, values) in zip(modes[1:], results[1:]):
                    # Одинаковые пиксели не заменяют проверку полного управления и последовательности чтений.
                    assert commands == first_commands, (target, mode, 'instruction_trace')
                    assert reads == first_reads, (target, mode, 'read_site_address_trace')
                    compared_instruction_events += len(commands)
                    compared_read_events += len(reads)
                    for token, before, after in zip(reads, first_values, values, strict=True):
                        if before == after:
                            continue
                        site, address = token >> 16, token & 65535
                        if address == 0xD18C:
                            assert before == 0 and after == mode
                            assert original[site - 0xC000:site - 0xC000 + 3] == bytes.fromhex('3A8CD1')
                            kind = 'Mode'
                        else:
                            # Отличающееся слово рамки возвращается именно через POP AF.
                            assert stack - 14 <= address < stack
                            assert before == mode_flags(0) and after == mode_flags(mode)
                            assert site in restore_tails, (target, mode, site, address)
                            kind = 'SavedF'
                        differing_read_sites[f'{site:04X}:{kind}'] += 1
                    # Все события обязаны совпадать по числу, PC, физическому банку и адресу.
                    assert len(events) == len(first_events), (target, mode, 'event_count')
                    final_values = {}
                    for ((site0, sp0), event0), ((site, sp), event) in zip(first_events, events):
                        compared_write_events += 1
                        assert (site, sp) == (site0, sp0) and event[:2] == event0[:2], (target, mode, 'write_path')
                        if event != event0:
                            assert site in permitted_flag_pushes, (target, mode, hex(site), event0, event)
                            assert event0[2] == mode_flags(0) and event[2] == mode_flags(mode), (site, event0, event, mode)
                            assert event[0] == 2 and event[1] + 0x8000 == sp, (site, sp, event)
                            assert stack - 14 <= sp < stack, (site, sp, stack)
                            flag_write_sites[f'{site:04X}'] += 1
                        final_values[event[:2]] = event[2]
                    # Эталон RAM переносит только явные различия Mode и последних присваиваний F.
                    expected = [bytearray(bank) for bank in first_banks]
                    expected[1][0x118C] = mode
                    for (bank, offset), value in final_values.items():
                        expected[bank][offset] = value
                        if value != first_banks[bank][offset]:
                            final_flag_addresses[f'{bank}:{offset:04X}'] += 1
                    assert all(bytes(a) == b for a, b in zip(expected, banks)), (target, mode, 'all_banks')
                    assert all(registers[i] == first_registers[i] for i in range(len(registers)) if i != 1), (target, mode, 'registers_except_F')
                    if registers[1] != first_registers[1]:
                        assert first_registers[1] == mode_flags(0) and registers[1] == mode_flags(mode), (target, mode, 'final_F')
                    assert raster == first_raster, (target, x, y, radius, bits, pattern)
                    assert writes == first_writes, (target, 'pixel_write_trace')
                    differing_registers.update(reg for reg in range(len(registers))
                                               if registers[reg] != first_registers[reg])
                    if registers[1] != first_registers[1]:
                        flag_differences[f'{target:04X}'] += 1
                raster_digest.update(first_raster)
                destinations[f'{target:04X}'] += 1
    assert {int(key.split(':')[0], 16) for key in differing_read_sites if key.endswith(':SavedF')} == set(restore_tails)
    report = dict(passed=True, original_z80_runs=runs,
        geometry_pattern_groups=sum(destinations.values()), modes_in_broad_geometry_groups=[0, 1, 128, 255],
        all_256_modes_per_selected_destination=True, all_mode_groups=all_mode_groups,
        all_mode_profiles=all_mode_profiles,
        groups_by_destination=dict(destinations), geometries_per_destination=8,
        patterns=[0, 65535, 21930, 4660],
        compared_raster_bytes_per_run=3072,
        final_pixels_and_ordered_pixel_writes_equal_within_groups=True,
        differing_register_array_indices=dict(differing_registers),
        differing_final_F_comparisons_by_destination=dict(flag_differences),
        source_control0_sha256=sha256(payload(22)).hexdigest(),
        compared_rasters_sha256=raster_digest.hexdigest(),
        no_raster_or_trdos_stubs=True, irq_executed=False,
        full_input_product_exhausted=False, all_ram_equal_claimed=False,
        all_physical_banks_compared=True,
        exact_ordered_write_sites_and_addresses_compared=True,
        differing_write_values_only_AND_mode_F_at_verified_PUSH_AF=True,
        differing_write_sites=dict(flag_write_sites),
        differing_final_stack_addresses=dict(final_flag_addresses),
        compared_paired_write_events=compared_write_events,
        compared_paired_instruction_events=compared_instruction_events,
        compared_paired_read_events=compared_read_events,
        exact_instruction_sequences_equal_within_groups=True,
        exact_ordered_read_sites_and_addresses_equal_within_groups=True,
        differing_read_values_only_Mode_and_POP_AF_flags=True,
        differing_read_sites=dict(differing_read_sites),
        flag_restore_tails_checked={f'{site:04X}': raw.hex() for site, raw in restore_tails.items()},
        changed_saved_F_reads_followed_only_by_POP_DE_or_RET=True,
        full_traces_saved_to_disk=False,
        all_registers_except_F_equal_including_R_and_T=True,
        mode_graphical_intent_proved=False, external_return_flag_consumers_proved=False,
        assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/CircleModePairedRasterVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()

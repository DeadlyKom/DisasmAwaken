"""Сквозной путь от запуска Awaken до перезагрузки станции после шумовых кадров."""
import argparse
from collections import Counter
from functools import partial
from hashlib import sha256
import json
from pathlib import Path

from CheckActionNoiseExit import ACTION_TAIL, COPY_SEED, NOISE_ENTRY, PERIOD, NoiseMatrix, irq_noise_frame
from CheckAwakenBasicRun import BasicReadPorts
from CheckBootBankFileReads import STATION_TAIL, check_intro_transition, check_loaded_tail, watch_addresses, watch_station_tail
from CheckControlsLegacySectorRead import run_with_rom
from CheckStationFlightCycle import DISK, ENTRIES, ROOT, payload, put, run_to
from TraceFlight import IFF, PC, SP, Simulator
from skoolkit import ROM128
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import F, IM, R, T


def check_missing_station(cpu, basic, dos):
    memory = SliceableMemory(banks=[bank.copy() for bank in cpu.memory.banks], out7ffd=0x18)
    memory.roms = (basic, basic)
    model = Simulator(memory, config={'fast_ldir': False, 'fast_djnz': True})
    model.registers[:] = cpu.registers
    ports = BasicReadPorts(memory)
    disk = bytearray(DISK)
    disk[4 * 16] = ord('X')
    ports.disk = disk
    model.set_tracer(ports)

    def set_rom(image):
        memory.memory[0] = image

    set_rom(basic)
    original_action = bytes(memory[0x6000:0x10000])
    run_with_rom(model, basic, dos, set_rom, 0x6300, step_limit=1_500_000)
    assert model.registers[SP] == 0x5FFF and memory[0x5D0F] == 1
    assert ports.attempts == [(0, 1), (0, 2), (0, 3)]
    assert bytes(memory[0x6000:0x10000]) == original_action
    assert original_action[0x300:0x308] == payload(17)[0x53D:0x545]
    return dict(renamed_catalogue_slot=4, dos_status=memory[0x5D0F],
                catalogue_reads=ports.attempts, data_sectors=0,
                return_pc=model.registers[PC], action_bytes_preserved=True,
                action_bytes_at_return=original_action[0x300:0x308].hex())


def follow_noise_return(cpu, ports, basic, dos, set_rom, *, mark_context, alias_seed=None):
    assert not mark_context
    memory, registers = cpu.memory, cpu.registers
    cpu.frame_duration, cpu.int_active = PERIOD, 36
    registers[PC] = 0x7E5A
    run_with_rom(cpu, basic, dos, set_rom, 0xA82D, step_limit=5000000)
    set_rom(basic)
    cpu.run(0xA82D, 0xA85E, interrupts=True)
    assert memory.o7ffd == 0x10 and registers[SP] == 0xBFFC

    # Порог и отличимое значение счёта задают условия ветви и различают два контекста.
    memory[0x6693] = 0x2E
    put(memory, 0x9BD0, b'\x34\x12')
    flight_context = bytes(memory[0x9BBD:0x9DBD])
    run_to(cpu, NOISE_ENTRY)
    assert registers[IM] == 1 and not registers[IFF]
    if alias_seed is not None:
        run_to(cpu, COPY_SEED)
        # LD A,R читает R после двух выборок кода команды ED 5F.
        registers[R] = (alias_seed & 0x80) | ((alias_seed - 2) & 0x7F)
        put(memory, 0x5C78, b'\xFE\xFF')
        assert bytes(memory[0x5CC2:0x5CC4]) == b'\xF1\xC9'
    tracer = NoiseMatrix(cpu, 100)
    cpu.set_tracer(tracer)
    memory.registers = registers
    memory.watched_addresses = frozenset(range(ACTION_TAIL, 0x10000))
    memory.watched_upper_bank = 0
    memory.watched_accesses.clear()
    initial_ticks = registers[T]
    iy, minimum_sp = 0x5C3A, registers[SP]
    increments = []
    key_decode = []
    for frame in range(1, 101):
        access_start = len(memory.watched_accesses)
        previous_iy = iy
        seed, iy, low_sp, increment = irq_noise_frame(cpu, iy)
        if alias_seed is not None and frame == 1:
            assert seed == alias_seed and iy == 0x5C82
        minimum_sp = min(minimum_sp, low_sp)
        if increment is not None:
            increments.append(dict(frame=frame, **increment))
        decode_accesses = [access for access in memory.watched_accesses[access_start:]
                           if access[2] in (0x02FC, 0x02FF, 0x030B)]
        if decode_accesses:
            key_decode.append(dict(frame=frame, iy=previous_iy, accesses=decode_accesses))
    run_to(cpu, 0xAAC4)
    assert tracer.reads == [255] * 99 + [254]
    assert registers[SP] == 0xBFFC and not registers[IFF]
    assert bytes(memory[0x9BBD:0x9DBD]) == flight_context
    if alias_seed is not None:
        assert increments == [dict(frame=2, address=0x5CC2, old=0xF1, new=0xF2, bank0=False)]
    action_accesses = Counter(memory.watched_accesses)
    assert action_accesses
    ordinary_accesses = {access for access in action_accesses if access[0] == 'read' and access[2] == 0x3870}
    if alias_seed is None:
        assert set(action_accesses) == ordinary_accesses and not key_decode
    else:
        expected_decode = [('read', 0xFD82, 0x02FC), ('read', 0xFD7C, 0x02FF),
                           ('read', 0xFD7C, 0x030B), ('write', 0xFD7C, 0x030B)]
        assert key_decode == [dict(frame=100, iy=0xFD7B, accesses=expected_decode)], key_decode
        assert set(action_accesses) - ordinary_accesses == set(expected_decode)
        assert memory.banks[0][0x3D82] == 0 and memory.banks[0][0x3D7C] == 0x20
    memory.watched_addresses = frozenset()
    memory.watched_upper_bank = None
    memory.watched_accesses.clear()
    memory.registers = None
    noise_ticks = registers[T] - initial_ticks

    relay = bytes(memory.banks[1][0x1CA9:0x1DA9])
    run_to(cpu, 0x4000)
    assert memory.o7ffd == 0x11 and registers[SP] == 0xBFFC
    assert bytes(memory[0x4000:0x4100]) == relay
    run_to(cpu, 0x3D13)
    assert bytes(memory[0x5CDD:0x5CE6]) == b'STATIONFC' and memory[0x5CF9] == 0
    assert registers[SP] == 0x5FFD and bytes(memory[0x5FFD:0x5FFF]) == b'\x00\x63'
    assert memory.o7ffd == 0x18
    cpu.set_tracer(ports)
    cursor = len(ports.attempts)
    set_rom(basic)
    hook_before = bytes(memory[0x5CC2:0x5CC4])
    if alias_seed is not None:
        assert hook_before == b'\xF2\xC9'
        with watch_addresses(cpu, range(0x5CC2, 0x5CC5), None) as hook_accesses:
            run_with_rom(cpu, basic, dos, set_rom, 0x5CC2, step_limit=550000)
            set_rom(basic)
            code = bytes(memory[0x5CC2:0x5CC5])
            assert code[:2] == hook_before
            flags, stack = registers[F], registers[SP]
            cpu.run()
            target = int.from_bytes(code[1:], 'little') if not flags & 0x80 else 0x5CC5
            assert (registers[PC], registers[SP]) == (target, stack)
        return dict(prepared_alias_seed=alias_seed, frames_increments=increments, tail_key_decode=key_decode,
                    hook_bytes_at_execution=code.hex(), hook_flags=flags, hook_sp=stack,
                    hook_next_pc=target, hook_stack_word=bytes(memory[stack:stack + 2]).hex(),
                    hook_accesses=hook_accesses, catalogue_reads_before_hook=ports.attempts[cursor:],
                    stopped_after_changed_instruction=True, station_reload_completion_checked=False)
    missing_station = check_missing_station(cpu, basic, dos)
    with watch_addresses(cpu, range(0x5CC2, 0x5CC4), None) as hook_accesses:
        run_with_rom(cpu, basic, dos, set_rom, 0x6300, step_limit=5500000)
    hook = dict(bytes_before_dos=hook_before.hex(), bytes_after_dos=bytes(memory[0x5CC2:0x5CC4]).hex(),
                access_runs=[dict(mode=mode, address=address, pc=pc, count=count)
                             for (mode, address, pc), count in Counter(hook_accesses).items()])
    first_sector = ENTRIES[4]['offset'] // 256
    expected_sectors = [(index // 16, index % 16 + 1) for index in range(first_sector, first_sector + 160)]
    actual_sectors = [sector for sector in ports.attempts[cursor:] if sector[0]]
    next_sector = first_sector + 160
    assert actual_sectors == expected_sectors + [(next_sector // 16, next_sector % 16 + 1)]
    fresh = payload(4)
    assert registers[SP] == 0x5FFF and bytes(memory[0x6000:0x10000]) == fresh
    station_context = bytes(memory[0x983B:0x9A3B])
    assert station_context == fresh[0x383B:0x3A3B] and station_context[0x13:0x15] != flight_context[0x13:0x15]
    loaded_tail = check_loaded_tail(memory, 4, STATION_TAIL)
    set_rom(basic)
    with watch_station_tail(cpu) as station_tail:
        run_with_rom(cpu, basic, dos, set_rom, 0x9A59, step_limit=5500000)
        cpu.run(0x9A59, 0x9A81, interrupts=True)
    assert registers[PC] == 0x9A81 and registers[SP] == 0x5FFF and memory.o7ffd == 0x10
    return dict(action_frames_before_damage=1, noise_irq_frames=100,
                noise_tstates=noise_ticks, minimum_irq_sp=minimum_sp, frames_increments=increments,
                action_tail_accesses=[dict(mode=mode, pc=pc, address=address, count=count)
                                      for (mode, address, pc), count in sorted(action_accesses.items())],
                tail_key_decode=key_decode,
                relay_entry=0x4000, relay_bytes=len(relay), dos_dispatch=0x3D13,
                station_sectors_loaded=len(expected_sectors), read_ahead_sectors=1,
                station_entry=0x6300, station_context_from_disk_bytes=len(station_context),
                prepared_flight_credits=0x1234, credits_on_station_entry=int.from_bytes(station_context[0x13:0x15], 'little'),
                loaded_tail=loaded_tail, restarted_station_tail=station_tail, station_frame_entry=registers[PC],
                missing_station=missing_station, dos_keyboard_hook=hook,
                threshold_and_flight_credits_prepared=True, direct_departure_entry_prepared=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    basic, dos = Path(ROM128[1]).read_bytes(), parser.parse_args().dos_rom.read_bytes()
    profile = check_intro_transition(basic, dos, 2, mark_context=False, flight_check=follow_noise_return)
    aliased = check_intro_transition(basic, dos, 2, mark_context=False,
                                     flight_check=partial(follow_noise_return, alias_seed=0x3B))
    result = dict(passed=True, original_disk_sha256=sha256(DISK).hexdigest(),
                  dos_rom_sha256=sha256(dos).hexdigest(), profile=profile, aliased_hook_profile=aliased,
                  original_rom_irq_and_disk_code_executed=True, modeled_fdc=True,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionNoiseStationCycleVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', 'utf-8')
    print('После 100 кадров с IRQ ПЗУ исходный TR-DOS загрузил станцию, выполнен первый кадр интерфейса.')


if __name__ == '__main__':
    main()

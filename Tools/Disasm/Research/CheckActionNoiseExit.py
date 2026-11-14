"""Цикл 6054 с ROM, настоящим выводом и явным пробуждением HALT."""
from itertools import product
import json
from pathlib import Path

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh
from CheckStationFlightCycle import payload as disk_payload, put, run_to
from TraceFlight import main as trace_flight
from skoolkit import ROM48, ROM128
from skoolkit.simutils import F, H, IFF, IM, L, R, T


NOISE_ENTRY, COPY_SEED, NOISE_HALT, NOISE_DI = 0x6054, 0x6070, 0x607B, 0x607C
ACTION_TAIL = 0xF866
PERIOD = 70908


class InputTrace(PortTrace):
    def __init__(self, simulator, keys):
        super().__init__(simulator)
        self.keys = iter(keys)
        self.reads = []

    def read_port(self, registers, port):
        if port == 0x00FE:
            value = next(self.keys)
            self.reads.append(value)
            return value
        if port == 0xFFFD:
            return self.ay[self.outfffd]
        return 255


class NoiseIrqMemory(RecordedBanks):
    watch_tail = False

    def __init__(self):
        super().__init__(out7ffd=16)
        self.tail_accesses = []

    def observe_tail(self, mode, address, value):
        if self.watch_tail and isinstance(address, int) and address >= ACTION_TAIL and self.o7ffd & 7 == 0:
            self.tail_accesses.append((mode, self.registers[PC], address, value))

    def __getitem__(self, address):
        value = super().__getitem__(address)
        self.observe_tail('read', address, value)
        return value

    def __setitem__(self, address, value):
        self.observe_tail('write', address, value)
        super().__setitem__(address, value)


class NoiseMatrix(InputTrace):
    def __init__(self, simulator, exit_frame):
        super().__init__(simulator, [255] * (exit_frame - 1) + [254])
        self.exit_frame = exit_frame
        self.space_reads = 0

    def read_port(self, registers, port):
        if port == 0x7FFE and len(self.reads) + 1 == self.exit_frame:
            self.space_reads += 1
            return 254
        return super().read_port(registers, port)


def irq_noise_frame(cpu, previous_iy, *, observe_irq=None):
    memory, registers = cpu.memory, cpu.registers
    run_to(cpu, COPY_SEED)
    seed = refresh(registers[R], 2)
    rom_start = 0x500 + seed
    run_to(cpu, NOISE_HALT)
    assert bytes(memory[0x8000:0x8C00]) == bytes(memory.roms[1][rom_start:rom_start + 3072])
    assert registers[10] * 256 + registers[11] == previous_iy and registers[IM] == 1
    assert memory.o7ffd == 16 and registers[IFF]
    saved = registers.copy()
    counter = int.from_bytes(memory[0x5C78:0x5C7A], 'little')
    for _ in range(PERIOD // 4 + 1):
        cpu.run()
        if registers[PC] == NOISE_DI:
            break
    else:
        raise AssertionError('Шумовой HALT не дождался периода IRQ')
    assert registers[T] % PERIOD < 36
    assert cpu.accept_interrupt(registers, memory, NOISE_HALT) and registers[PC] == 0x0038
    low_sp = registers[SP]
    increment = None
    for _ in range(1024):
        pc = registers[PC]
        if pc == NOISE_DI:
            break
        if observe_irq is not None:
            observe_irq(pc)
        low_sp = min(low_sp, registers[SP])
        if pc == 0x0045:
            assert increment is None and memory.o7ffd == 16
            address = (previous_iy + 0x40) & 65535
            increment = dict(address=address, old=memory[address:address + 1][0], bank0=address >= 0xC000)
        cpu.run()
    else:
        raise AssertionError(('ROM не вернула управление к DI', registers[PC]))
    assert registers[:15] == saved[:15] and registers[16:24] == saved[16:24]
    assert registers[IM] == 1 and registers[IFF] and memory.o7ffd == 16
    assert (increment is not None) == (counter == 65535)
    expected_counter = (counter + 1) & 65535
    if increment:
        address = increment['address']
        increment['new'] = memory[address:address + 1][0]
        assert increment['new'] == ((increment['old'] + (address >= 0x4000)) & 255)
        # После оборачивания HL уже записан в FRAMES, косвенный INC может попасть в то же слово.
        if 0x5C78 <= address < 0x5C7A:
            assert increment['old'] == 0
            expected_counter += 1 << (8 * (address - 0x5C78))
    assert int.from_bytes(memory[0x5C78:0x5C7A], 'little') == expected_counter
    cpu.run()
    assert not registers[IFF]
    next_iy = int.from_bytes(memory[0x8BFE:0x8C00], 'little')
    return seed, next_iy, low_sp, increment


def check_noise_ay_alias(cpu, reset, entry_to_read):
    memory, registers = cpu.memory, cpu.registers
    cases = []
    seed = 0xD3
    # Два одинаковых входных R, переполнение младшего FRAMES только во втором опыте.
    for counter in (0, 0xFFFE):
        ports = reset(counter)
        registers[R] = (seed & 128) | ((seed - entry_to_read) & 127)
        observed, iy, _, increment = irq_noise_frame(cpu, 0x5C3A)
        assert (observed, iy, increment) == (0xD3, 0xED3F, None)
        _, _, _, increment = irq_noise_frame(cpu, iy)
        assert increment == (dict(address=0xED7F, old=0x79, bank0=True, new=0x7A) if counter else None)
        run_to(cpu, 0xED7E)
        assert memory.o7ffd == 16 and bytes(memory[0xED7E:0xED80]) == (b'\xED\x7A' if counter else b'\xED\x79')
        volume = max(4, memory[0xED83] >> 1)
        original_volume_register = ports.ay[10]
        assert ports.outfffd == 6 and ports.ay[6] == 5
        writes_start = len(ports.writes)
        hl_before = registers[H] * 256 + registers[L]
        wanted_hl = (hl_before + registers[SP] + (registers[F] & 1)) & 65535 if counter else hl_before
        cpu.run()
        assert registers[H] * 256 + registers[L] == wanted_hl
        run_to(cpu, 0x6090)
        writes = ports.writes[writes_start:]
        assert writes == ([] if counter else [(0xFFFD, 10)]) + [(0xBFFD, volume)]
        assert ports.ay[6] == (volume if counter else 5)
        assert ports.ay[10] == (original_volume_register if counter else volume)
        cases.append(dict(initial_frames=counter, first_copy_seed=seed, second_irq_increment=increment,
                          ay_select_address=0xED7E, hl_after_instruction=wanted_hl,
                          volume=volume, ay_writes=writes, final_ay_noise_period=ports.ay[6],
                          final_ay_channel_c_volume=ports.ay[10]))
    return cases


def check_fixed_irq_aliases(cpu, reset, entry_to_read):
    memory, registers = cpu.memory, cpu.registers
    targets = {0x3B: 0x5CC2, 0x6B: 0x5F3D, 0x8B: 0x5CC2, 0xC7: 0x5C78, 0xF9: 0x5C78}
    cases = []
    for seed, address in targets.items():
        reset(0x52FFFE)
        previous = memory[address]
        registers[R] = (seed & 128) | ((seed - entry_to_read) & 127)
        observed, iy, _, first = irq_noise_frame(cpu, 0x5C3A)
        assert observed == seed and first is None and iy == address - 0x40
        assert int.from_bytes(memory[0x5C78:0x5C7B], 'little') == 0x52FFFF
        _, _, _, second = irq_noise_frame(cpu, iy)
        assert second is not None and second['address'] == address and not second['bank0']
        assert second['old'] == (0 if address == 0x5C78 else previous)
        final_frames = int.from_bytes(memory[0x5C78:0x5C7B], 'little')
        assert final_frames == 0x520000 + (address == 0x5C78)
        cases.append(dict(first_copy_seed=seed, second_irq_iy=iy, increment=second,
                          initial_frames=0x52FFFE, final_frames=final_frames))
    return cases


def check_pressed_key_tail(cpu, reset, entry_to_read, rom):
    memory, registers = cpu.memory, cpu.registers
    cases = []
    has_rom128_flag_gate = rom[0x3870:0x3874] == b'\xFD\xCB\x01\x66'
    for seed in range(256):
        ports = reset(0, exit_frame=2)
        registers[R] = (seed & 128) | ((seed - entry_to_read) & 127)
        observed, iy, _, first_increment = irq_noise_frame(cpu, 0x5C3A)
        assert observed == seed and iy == int.from_bytes(rom[0x10FE + seed:0x1100 + seed], 'little')
        assert first_increment is None and not ports.space_reads and not memory.tail_accesses
        _, _, _, second_increment = irq_noise_frame(cpu, iy)
        assert second_increment is None and ports.space_reads
        flags_address = (iy + 1) & 65535
        mode_address = (iy + 7) & 65535
        expected = []
        if has_rom128_flag_gate and flags_address >= ACTION_TAIL:
            expected.append(('read', 0x3870, flags_address, 0))
        if mode_address >= ACTION_TAIL:
            expected.append(('read', 0x02FC, mode_address, 0))
        if flags_address >= ACTION_TAIL:
            expected.extend((('read', 0x02FF, flags_address, 0),
                             ('read', 0x030B, flags_address, 0),
                             ('write', 0x030B, flags_address, 0x20)))
        assert memory.tail_accesses == expected, (seed, iy, memory.tail_accesses, expected)
        if memory.tail_accesses:
            cases.append(dict(first_copy_seed=seed, second_irq_iy=iy,
                              accesses=[dict(mode=mode, pc=pc, address=address, value=value)
                                        for mode, pc, address, value in memory.tail_accesses]))
    return dict(seeds_checked=256, space_pressed_at_second_irq=True, no_frames_wrap=True,
                cases_with_tail_accesses=cases)


def check_real_noise_irq():
    profiles = []
    for rom_path in (ROM128[1], ROM48):
        memory = NoiseIrqMemory()
        rom = Path(rom_path).read_bytes()
        rom_uses_indexed_keyboard_flag = rom[0x3870:0x3874] == b'\xFD\xCB\x01\x66'
        memory.roms = (memory.roms[0], list(rom))
        memory.out7ffd(16)
        put(memory, 0x6000, disk_payload(17))
        memory[0x5C00] = memory[0x5C04] = 255
        memory[0x5C3B] = 8
        cpu = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A}, {'im': 1},
                        config={'frame_duration': PERIOD, 'int_active': 36})
        memory.registers = registers = cpu.registers
        flight = trace_flight(['--frames', '2', '--verify-flight-cycle'], boot_simulator=cpu, save_reports=False)
        assert flight['complete_frame_returns'] == 1 and registers[PC] == 0xA85E
        memory[0x6693] = 0x2E
        run_to(cpu, NOISE_ENTRY)
        assert registers[SP] == 0xBFFC and not registers[IFF] and registers[IM] == 1
        initial = registers.copy()
        banks = [bank.copy() for bank in memory.banks]
        memory.watch_tail = True

        def reset(counter, exit_frame=100):
            for bank, saved in zip(memory.banks, banks):
                bank[:] = saved
            memory.out7ffd(16)
            registers[:] = initial
            put(memory, 0x5C78, counter.to_bytes(3, 'little'))
            memory.tail_accesses.clear()
            ports = NoiseMatrix(cpu, exit_frame)
            cpu.set_tracer(ports)
            return ports

        ports = reset(0)
        iy, sp = 0x5C3A, 0xBFFC
        targets = {}
        for frame in range(1, 101):
            target = (iy + 0x40) & 65535
            if target >= ACTION_TAIL:
                targets.setdefault(target, frame)
            _, iy, low_sp, increment = irq_noise_frame(cpu, iy)
            sp = min(sp, low_sp)
            assert increment is None
        run_to(cpu, 0xAAC4)
        assert registers[SP] == 0xBFFC and memory.o7ffd == 16 and not registers[IFF]
        assert ports.reads == [255] * 99 + [254]
        assert bytes(memory[0x5C78:0x5C7B]) == b'\x64\x00\x00'
        original_tail_reads = memory.tail_accesses.copy()
        assert all(mode == 'read' and pc == 0x3870 and value == 0
                   for mode, pc, _, value in original_tail_reads), original_tail_reads

        reset(0xFFFFFF)
        _, _, _, first_increment = irq_noise_frame(cpu, 0x5C3A)
        assert first_increment == dict(address=0x5C7A, old=255, bank0=False, new=0)

        natural_aliases = []
        for target, frame in sorted(targets.items()):
            reset(0x10000 - frame)
            iy = 0x5C3A
            for _ in range(frame):
                _, iy, _, increment = irq_noise_frame(cpu, iy)
            assert increment == dict(address=target, old=0, bank0=True, new=1)
            natural_aliases.append(dict(frame=frame, **increment))

        reset(0)
        run_to(cpu, COPY_SEED)
        entry_to_read = (refresh(registers[R], 2) - initial[R]) & 127
        write_aliases, read_aliases = [], []
        for seed in range(256):
            iy = int.from_bytes(rom[0x10FE + seed:0x1100 + seed], 'little')
            write_target = (iy + 0x40) & 65535
            read_target = (iy + 1) & 65535
            tail_write = write_target >= ACTION_TAIL
            tail_read = rom_uses_indexed_keyboard_flag and read_target >= ACTION_TAIL
            if not (tail_write or tail_read):
                continue
            reset(0x00FFFE if tail_write else 0)
            registers[R] = (seed & 128) | ((seed - entry_to_read) & 127)
            observed, next_iy, _, increment = irq_noise_frame(cpu, 0x5C3A)
            assert (observed, next_iy, increment) == (seed, iy, None)
            _, _, _, increment = irq_noise_frame(cpu, iy)
            expected = []
            if tail_write:
                assert increment == dict(address=write_target, old=0, bank0=True, new=1)
                expected.extend((('read', 0x0045, write_target, 0), ('write', 0x0045, write_target, 1)))
                assert bytes(memory[0x5C78:0x5C7B]) == b'\x00\x00\x00'
                write_aliases.append(dict(seed=seed, iy=iy, **increment))
            else:
                assert increment is None
            if tail_read:
                expected.append(('read', 0x3870, read_target, 0))
                read_aliases.append(dict(seed=seed, iy=iy, address=read_target, value=0))
            assert memory.tail_accesses == expected, memory.tail_accesses
        assert len(write_aliases) == 15 and len({row['address'] for row in write_aliases}) == 14
        profiles.append(dict(rom=Path(rom_path).name, full_noise_frames=100,
                             minimum_irq_sp=sp, initial_rom_counter=0,
                             first_frame_counter_high_byte_increment=first_increment,
                             original_tail_reads=original_tail_reads,
                             tail_aliases_with_original_refresh_and_prepared_frames=natural_aliases,
                             tail_aliases_with_prepared_refresh_and_frames=write_aliases,
                             keyboard_flag_aliases_with_prepared_refresh=read_aliases,
                             fixed_ram_aliases=check_fixed_irq_aliases(cpu, reset, entry_to_read),
                             pressed_key_tail=check_pressed_key_tail(cpu, reset, entry_to_read, rom),
                             ay_select_opcode_alias=check_noise_ay_alias(cpu, reset, entry_to_read)))
    return dict(actual_rom_irq_executed=True, irq_period_tstates=PERIOD, profiles=profiles,
                action_initialization_trdos_substituted=True, damage_threshold_prepared=True,
                native_reachability_of_ram_aliases_proved=False)


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[1][:] = bytes(base_memory()[0xC000:])
    total_frames = 0
    for ignored_key, wait in product((0, 255), (0, 2)):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
        sim = Simulator(memory)
        keys = [ignored_key] * 99 + [255] * wait + [254]
        trace = InputTrace(sim, keys)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0x6054, 'SP': 0xBFFE, 'DE': 0x2468,
                                         'BC': 0x369C, 'IY': 0xA789}, None, False)
        frames = 0
        rom_start = None
        for _ in range(1800000):
            r = sim.registers
            pc = r[PC]
            if pc == 0xAAC4:
                break
            if pc == 0x6070:
                rom_start = 0x500 + refresh(r[15], 2)
            if pc == 0x607B:
                assert bytes(memory[0x8000:0x8C00]) == bytes(memory.roms[1][rom_start:rom_start + 3072])
                assert memory[pc] == 0x76
                assert r[14] == 0x3F
                r[PC] += 1
                frames += 1
                continue
            sim.run()
        assert sim.registers[PC] == 0xAAC4 and sim.registers[SP] == 0xBFFE
        assert frames == 100 + wait and trace.reads == keys
        paging = [value for port, value in trace.writes if port == 0x7FFD]
        assert paging == [17, 16] * (frames + 1)
        assert memory.o7ffd == 16
        expected = bytes(memory.banks[1][0x1CA9:0x1DA9])
        sim.run(0xAAC4, 0x4000)
        assert sim.registers[PC] == 0x4000 and sim.registers[SP] == 0xBFFE
        assert memory.o7ffd == 17 and trace.writes[-1] == (0x7FFD, 17)
        assert bytes(memory.banks[5][:256]) == expected
        total_frames += frames
    report = dict(passed=True, total_cases=4, frames=total_frames,
                  actual_rom_copy_and_output_executed=True, halt_wakeup_injected=True,
                  station_loader_relocated_without_call=True, hardware_irq_executed=False,
                  timed_rom_irq=check_real_noise_irq(), assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionNoiseExitVerification.json').write_text(payload, encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'timed_rom_irq'}, indent=2))


if __name__ == '__main__':
    main()

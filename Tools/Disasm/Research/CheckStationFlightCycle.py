"""Исполнение оригинальных переходов STATIONF и ACTION через границы TR-DOS."""
import hashlib
import json
from collections import Counter

from CheckFlightKeyPaths import KeyProbe
from CheckIntroStationTransition import IntroInput
from CheckScreenUpdate import PortTrace, put
from TraceFlight import A, B, C, D, E, F, H, L, PC, SP, ROOT, Simulator, main as trace
from skoolkit.pagingtracer import SliceableMemory


DISK_DIR = ROOT / 'Tools/Disasm/Disk'
DISK = (DISK_DIR / 'original.trd').read_bytes()
ENTRIES = {row['slot']: row for row in json.loads(
    (DISK_DIR / 'Manifest.json').read_text(encoding='utf-8'))['entries']}
LEGACY_CONTEXT_OFFSET = 0x13B
LEGACY_CONTEXT_END = 0x1BD
LEGACY_CONTEXT_FIXED = 0x5DA0 + LEGACY_CONTEXT_OFFSET
LEGACY_CONTEXT_BANKED = 0xDADE + LEGACY_CONTEXT_OFFSET
LEGACY_CONTEXT_SIZE = LEGACY_CONTEXT_END - LEGACY_CONTEXT_OFFSET


def payload(slot):
    row = ENTRIES[slot]
    return DISK[row['offset']:row['offset'] + row['length']]


def run_to(cpu, target, observer=None):
    for _ in range(300000):
        pc = cpu.registers[PC]
        if pc == target:
            return
        assert pc >= 0x4000, hex(pc)
        if observer is not None:
            observer(pc)
        cpu.run()
    raise AssertionError(f'Не достигнут адрес {target:04X}')


def resume_dos(cpu):
    registers = cpu.registers
    sp = registers[SP]
    registers[PC] = int.from_bytes(cpu.memory[sp:sp + 2], 'little')
    registers[SP] += 2


def load_boot_sectors(cpu, slot, skip, sectors, destination, continuation):
    memory, registers = cpu.memory, cpu.registers
    entry = ENTRIES[slot]
    first = entry['first_track'] * 16 + entry['first_sector'] + skip
    assert registers[PC] == 0x3D13 and registers[C] == 0x05 and registers[B] == sectors
    assert registers[H] * 256 + registers[L] == destination
    assert registers[D] * 16 + registers[E] == first
    size = sectors * 256
    start = first * 256
    assert len(DISK[start:start + size]) == size
    ram_size = min(size, 0x10000 - destination)
    # После оборачивания HL оставшиеся байты попадают в окно ПЗУ, запись игнорируется.
    assert size - ram_size <= 0x4000
    put(memory, destination, DISK[start:start + ram_size])
    resume_dos(cpu)
    assert registers[PC] == continuation
    return dict(slot=slot, first_sector_index=first, sectors=sectors, destination=destination,
                bytes_written_to_ram=ram_size, bytes_addressed_to_rom=size - ram_size)


class LegacyWindowMemory(SliceableMemory):
    watch_legacy = False

    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.legacy_writes = []
        self.context_accesses = Counter()
        self.banked_context_load = []

    def observe_context(self, mode, address, value):
        if not self.watch_legacy or not isinstance(address, int):
            return
        pc = self.legacy_registers[PC]
        if LEGACY_CONTEXT_FIXED <= address < LEGACY_CONTEXT_FIXED + LEGACY_CONTEXT_SIZE:
            self.context_accesses['fixed', mode, pc, address] += 1
        elif self.o7ffd & 7 == 1 and LEGACY_CONTEXT_BANKED <= address < LEGACY_CONTEXT_BANKED + LEGACY_CONTEXT_SIZE:
            if mode == 'write' and pc == 0x3D13:
                self.banked_context_load.append((address, value))
            else:
                self.context_accesses['bank1', mode, pc, address] += 1

    def __getitem__(self, address):
        value = super().__getitem__(address)
        self.observe_context('read', address, value)
        return value

    def __setitem__(self, address, value):
        if self.watch_legacy and 0x5DA0 <= address < 0x5EDB:
            self.legacy_writes.append((address, value))
        self.observe_context('write', address, value)
        super().__setitem__(address, value)

    def report_context(self, fixed_before, original):
        fixed_after = bytes(self[LEGACY_CONTEXT_FIXED:LEGACY_CONTEXT_FIXED + LEGACY_CONTEXT_SIZE])
        offset = LEGACY_CONTEXT_BANKED - 0xC000
        banked_after = bytes(self.banks[1][offset:offset + LEGACY_CONTEXT_SIZE])
        assert self.banked_context_load == list(enumerate(original, LEGACY_CONTEXT_BANKED))
        assert banked_after == original
        accesses = [dict(window=window, mode=mode, pc=pc, address=address, count=count)
                    for (window, mode, pc, address), count in sorted(self.context_accesses.items())]
        assert not accesses, accesses
        assert fixed_after == fixed_before and fixed_after != original
        self.context_accesses.clear()
        self.banked_context_load.clear()
        return dict(file_offset=LEGACY_CONTEXT_OFFSET, length=LEGACY_CONTEXT_SIZE,
                    fixed_address=LEGACY_CONTEXT_FIXED, bank1_address=LEGACY_CONTEXT_BANKED,
                    original_bytes_loaded_once=True, original_bank1_bytes_preserved=True,
                    fixed_bytes_equal_to_original=fixed_after == original,
                    fixed_bytes_preserved_since_entry=fixed_before == fixed_after,
                    cpu_accesses_excluding_dos_model_load=accesses)


def boot_from_basic():
    memory = LegacyWindowMemory()
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    memory.roms = (list(rom), list(rom))
    memory.out7ffd(0x10)
    program = payload(3)
    put(memory, 0x5D3B, program)
    entry = int.from_bytes(program[115:117], 'little')
    assert entry == int(program[107:112]) == 0x5D41
    # Системное слово после первого каталожного сектора BASIC задаётся дисковой моделью.
    intro_first = ENTRIES[3]['offset'] // 256 + 1
    track, sector = divmod(intro_first, 16)
    put(memory, 0x5CF4, (sector, track))
    memory[0x5C00] = memory[0x5C04] = 0xFF
    cpu = Simulator(memory, {'PC': entry, 'SP': 0x5FFF, 'IY': 0x5C3A}, state={'im': 1},
                    config={'fast_ldir': False, 'fast_djnz': True})
    registers = cpu.registers
    run_to(cpu, 0x3D13)
    intro = load_boot_sectors(cpu, 3, 1, 44, 0x6400, 0x6500)
    inputs = IntroInput(cpu, 2)
    cpu.set_tracer(inputs)
    cpu.run(0x6500, 0x5D3B, interrupts=True)
    assert inputs.polls == 3
    cpu.run(0x5D3B, 0x3D13, interrupts=True)
    assert registers[C] == 0x0A and bytes(memory[0x5CDD:0x5CE6]) == b'STATIONFC'
    registers[C] = 4
    resume_dos(cpu)
    run_to(cpu, 0x3D13)
    assert (registers[A], registers[C]) == (4, 0x08)
    put(memory, 0x5CDD, DISK[64:80])
    resume_dos(cpu)
    run_to(cpu, 0x3D13)
    assert memory.o7ffd == 0x18
    station = load_boot_sectors(cpu, 4, 0, 192, 0x6000, 0x6300)
    assert bytes(memory[0x6000:0x10000]) == payload(4)
    assert bytes(memory[0:0x4000]) == rom
    return cpu, dict(usr_entry=entry, basic_rom_interpreter_executed=False,
                     initial_sector_load=intro, station_sector_load=station,
                     intro_keyboard_polls=inputs.polls)


def substitute_file_read(cpu, slot, name, return_pc, *, stack=0x5FFD):
    memory, registers = cpu.memory, cpu.registers
    assert registers[PC] == 0x3D13 and (registers[A], registers[C]) == (0, 0x0E)
    assert bytes(memory[0x5CDD:0x5CE6]) == name == DISK[16 * slot:16 * slot + 9]
    assert memory.o7ffd == 0x18 and registers[SP] == stack
    assert int.from_bytes(memory[stack:stack + 2], 'little') == return_pc
    assert ENTRIES[slot]['parameter'] == 0x6000
    data = payload(slot)
    put(memory, 0x5CDD, DISK[16 * slot:16 * (slot + 1)])
    put(memory, 0x6000, data)
    registers[F] &= 0xFE
    resume_dos(cpu)
    return dict(slot=slot, name=name.decode('ascii'), destination=0x6000, size=len(data),
                return_address=return_pc)


def purchase_equipment(cpu, row):
    memory, registers = cpu.memory, cpu.registers
    page = memory.o7ffd
    memory.out7ffd(0x16)
    memory[0x6306] = 0x16
    memory[0x983A] = 5
    memory[0x7217] = row
    memory[0x71B9] = 0
    cpu.set_tracer(PortTrace(cpu))
    entry_sp = registers[SP]
    registers[SP] -= 2
    put(memory, registers[SP], (0xFF, 0x3F))
    registers[PC] = 0xC000
    messages = []

    def observe(pc):
        if pc == 0xA85F:
            messages.append(registers[A])

    run_to(cpu, 0x3FFF, observe)
    remaining = int.from_bytes(memory[0x984E:0x9850], 'little')
    assert registers[SP] == entry_sp
    assert memory.o7ffd == memory[0x6306] == 0x16
    memory.out7ffd(page)
    memory[0x6306] = page
    return messages, remaining


def purchase_return_system(cpu, eligible):
    memory = cpu.memory
    if eligible:
        # Подготовка допустимого корабля и суммы из исходной строки цены.
        memory[0x9849] = 0
        put(memory, 0x984E, memory[0x95C0:0x95C2])
    ship = memory[0x9849]
    credits = int.from_bytes(memory[0x984E:0x9850], 'little')
    messages, remaining = purchase_equipment(cpu, 23)
    assert memory[0x98A5] == (0xFE if eligible else 0xFF)
    assert (messages, remaining) == (([], 0) if eligible else ([6], credits))
    assert memory[0x9849] == ship
    return dict(event=5, equipment_row=23, eligible_fixture=eligible, ship=ship,
                starting_credits=credits, remaining_credits=remaining,
                equipment_byte=memory[0x98A5], queued_messages=messages)


def prepare_hyperjump(cpu, observer=None, *, fuel_additive=0xFE):
    memory, registers = cpu.memory, cpu.registers
    key = KeyProbe(memory, tuple(memory[0x9D7A:0x9D7C]))
    assert key.key == (0xFD, 0x10)
    cpu.set_tracer(key)
    run_to(cpu, 0x6F1D)
    key.observe(1, memory, registers)
    run_to(cpu, 0x70F6, lambda _: key.observe(1, memory, registers))
    key.observe(1, memory, registers)
    assert key.handlers == [(0x17, 0, 0x70F6)]
    # Допуск команды и отличающийся контекст задаются на входе найденного обработчика.
    memory[0xA85F] = 0
    memory[0x9C26] = 0xFE
    if fuel_additive is not None:
        memory[0x9C2A] = fuel_additive
    memory[0x9C10], memory[0x9C8A] = 100, 7
    memory[0x9BCA] = memory[0x9BC5] ^ 1
    destination_context = bytes(memory[0x9BC6:0x9BCB])
    assert memory[0x7104] == 0
    run_to(cpu, 0x3D13, (lambda _: observer(0, memory, registers)) if observer else None)
    assert memory[0x9C10] == 86 and bytes(memory[0x9BC1:0x9BC6]) == destination_context
    saved = bytes(memory[0x9BBD:0x9D9E])
    assert bytes(memory[0x4000:0x41E1]) == saved
    return key, saved


def exercise_hyperjump(cpu, observer):
    memory, registers = cpu.memory, cpu.registers
    key, saved = prepare_hyperjump(cpu, observer)
    request = substitute_file_read(cpu, 17, b'ACTION  C', 0x4234, stack=0x4FFE)
    run_to(cpu, 0x6000, lambda _: observer(0, memory, registers))
    assert bytes(memory[0x9BBD:0x9D9E]) == saved and registers[SP] == 0x5FFF
    flight = trace(['--verify-flight-cycle', '--frames', '3'], boot_simulator=cpu,
                   save_reports=False, instruction_observer=observer)
    assert flight['complete_frame_returns'] == 2
    return dict(key=list(key.key), handler=0x70F6, preferred_spent=14,
                context_bytes_restored=len(saved), reload_file=request,
                complete_frames_after_reload=flight['complete_frame_returns'],
                gate_fixture_applied_at_handler=True)


def exercise(equipped, transfer_trailer=None, *, start_from_basic=False):
    intro_boot = None
    if start_from_basic:
        cpu, intro_boot = boot_from_basic()
        memory = cpu.memory
    else:
        memory = SliceableMemory(out7ffd=0x10)
        put(memory, 0x6000, payload(4))
        cpu = Simulator(memory, {'PC': 0x6300, 'SP': 0x5FFF, 'IY': 0x5C3A},
                        config={'fast_ldir': False, 'fast_djnz': False})
    registers = cpu.registers
    station = trace(['--region', 'station', '--frames', '8'], boot_simulator=cpu, save_reports=False)
    assert station['reason'] == 'requested_frame_entries' and station['frame_entries'] == 8
    assert registers[PC] == 0x9A81 and registers[SP] == 0x5FFF and memory.o7ffd == 0x10
    assert memory[0x9849] == 6 and memory[0x98AA] == memory[0x98A5] == 0xFF
    purchase = purchase_return_system(cpu, equipped)
    if transfer_trailer is not None:
        assert equipped and len(transfer_trailer) == 29
        put(memory, 0x9A1E, transfer_trailer)
    departure = PortTrace(cpu)
    cpu.set_tracer(departure)
    registers[PC] = 0x7E5A
    run_to(cpu, 0x3D13)
    assert [value for port, value in departure.writes if port == 0x7FFD] == [0x1F, 0x13, 0x10, 0x18]
    assert bytes(memory[0x4000:0x4200]) == bytes(memory[0x983B:0x9A3B])
    outbound = bytes(memory[0x4000:0x4200])
    map_context = slice(0xCE, 0x18F)
    outbound_map_context = outbound[map_context]
    to_action = substitute_file_read(cpu, 17, b'ACTION  C', 0x4236)
    run_to(cpu, 0x6000)
    assert registers[SP] == 0x6000 and bytes(memory[0x9BBD:0x9DBD]) == outbound
    if transfer_trailer is not None:
        assert bytes(memory[0x9DA0:0x9DBD]) == transfer_trailer
    before_flight = bytes(memory[0x5DA0:0x5EDB]) if intro_boot is not None else None
    if intro_boot is not None:
        context_before_flight = bytes(memory[LEGACY_CONTEXT_FIXED:LEGACY_CONTEXT_FIXED + LEGACY_CONTEXT_SIZE])
        original_context = payload(23)[LEGACY_CONTEXT_OFFSET:LEGACY_CONTEXT_END]
    legacy_execution = []

    def observe_legacy(_, memory, registers):
        pc = registers[PC]
        bank = memory.o7ffd & 7
        if 0x5DA0 <= pc < 0x5DA0 + LEGACY_CONTEXT_END or (bank == 1 and 0xDADE <= pc < 0xDADE + LEGACY_CONTEXT_END):
            legacy_execution.append((pc, bank))

    if intro_boot is not None:
        memory.legacy_registers = registers
        memory.watch_legacy = True
    flight = trace(['--verify-flight-cycle', '--frames', '65'],
                   boot_simulator=cpu, save_reports=False,
                   instruction_observer=observe_legacy if intro_boot is not None else None)
    assert flight['complete_frame_returns'] == 64
    assert bytes(memory[0x9C8B:0x9D4C]) == outbound_map_context
    if transfer_trailer is not None:
        assert bytes(memory[0x9DA0:0x9DBD]) == transfer_trailer

    if intro_boot is not None:
        after_flight = bytes(memory[0x5DA0:0x5EDB])
        original_control = payload(23)[:0x13B]
        assert before_flight[:18] == after_flight[:18] == bytes.fromhex(
            '46 43 3E 16 11 FF FF 21 2C 66 01 32 66 C3 A3 66 00 80')
        assert before_flight[0x7F:0x84] == bytes.fromhex('28 28 28 29 29')
        assert after_flight[0x7F:0x84] == bytes.fromhex('28 05 4B 29 1B')
        assert after_flight != original_control
        assert bytes(memory.banks[1][0x1ADE:0x1ADE + 0x13B]) == original_control
        expected_writes = [(0x5E20, 0x05), (0x5E21, 0x4B), (0x5E23, 0x1B)]
        assert not legacy_execution and memory.legacy_writes == expected_writes
        intro_boot.update(fixed_entry_prefix=after_flight[:18].hex(),
            before_legacy_operands=before_flight[0x7F:0x84].hex(),
            after_legacy_operands=after_flight[0x7F:0x84].hex(),
            fixed_legacy_window_writes=memory.legacy_writes.copy(),
            control_prefix_still_in_bank_1=True, control_fixed_copy_seen=False,
            control_execution_seen=False,
            adjacent_legacy_context=memory.report_context(context_before_flight, original_context))
        if transfer_trailer is None:
            memory.legacy_writes.clear()
            context_before_reload = bytes(memory[LEGACY_CONTEXT_FIXED:LEGACY_CONTEXT_FIXED + LEGACY_CONTEXT_SIZE])
            intro_boot['hyperjump'] = exercise_hyperjump(cpu, observe_legacy)
            assert not legacy_execution and memory.legacy_writes == expected_writes
            assert bytes(memory[0x5DA0:0x5EDB]) == after_flight
            assert bytes(memory.banks[1][0x1ADE:0x1ADE + 0x13B]) == original_control
            assert bytes(memory[0x9C8B:0x9D4C]) == outbound_map_context
            intro_boot['hyperjump']['fixed_legacy_window_writes'] = memory.legacy_writes.copy()
            intro_boot['hyperjump']['adjacent_legacy_context'] = memory.report_context(context_before_reload, original_context)
        memory.watch_legacy = False

    key = KeyProbe(memory, (0xFB, 0x08))
    cpu.set_tracer(key)
    run_to(cpu, 0x6F1D)
    assert memory[0x9C27] == (0xFE if equipped else 0xFF) and memory[0xA85F] == 0
    key.observe(1, memory, registers)
    run_to(cpu, 0x7606, lambda _: key.observe(1, memory, registers))
    assert key.handlers == [(0x12, 0, 0x7606)] and key.pending_target == 0x7606
    key.observe(1, memory, registers)
    result = dict(purchase=purchase, station_start_loads=station['loads'],
                  departure_file=to_action, outgoing_context_bytes=len(outbound),
                  flight_start_loads=flight['loads'], complete_flight_frames=flight['complete_frame_returns'],
                  key_row=key.key[0], key_mask=key.key[1], key_index=key.handlers[0][0],
                  handler=registers[PC], map_context_bytes=len(outbound_map_context),
                  map_context_preserved_after_64_frames=True)
    if intro_boot is not None:
        result['intro_boot'] = intro_boot
    if not equipped:
        run_to(cpu, 0x6F55, lambda _: key.observe(1, memory, registers))
        key.observe(1, memory, registers)
        assert key.finished and key.returns == 1 and memory[0x9C27] == 0xFF
        run_to(cpu, 0xA85E)
        result.update(return_requested=False, next_flight_frame=registers[PC])
        return result

    inbound = bytearray(memory[0x9BBD:0x9DBD])
    inbound[2], inbound[3] = inbound[3], inbound[2]
    inbound[0x6A] = 0xFF
    run_to(cpu, 0x3D13)
    assert bytes(memory[0x4000:0x4200]) == inbound
    to_station = substitute_file_read(cpu, 4, b'STATIONFC', 0x421F)
    station_tail = bytes(memory[0x9A1C:0x9A3B])
    run_to(cpu, 0x6300)
    assert registers[SP] == 0x5FFF and bytes(memory[0x983B:0x9A1C]) == inbound[:481]
    assert inbound[map_context] == outbound_map_context == bytes(memory[0x9909:0x99CA])
    assert bytes(memory[0x9A1C:0x9A3B]) == station_tail
    if transfer_trailer is not None:
        assert inbound[-29:] == transfer_trailer
        assert station_tail[-29:] == bytes(29)
    returned = trace(['--region', 'station', '--frames', '8'], boot_simulator=cpu, save_reports=False)
    assert returned['reason'] == 'requested_frame_entries' and returned['frame_entries'] == 8
    assert registers[PC] == 0x9A81 and registers[SP] == 0x5FFF and memory[0x98A5] == 0xFF
    result.update(return_requested=True, return_file=to_station, incoming_context_bytes=481,
                  map_context_restored_on_station_entry=True,
                  untouched_station_tail_bytes=len(station_tail), station_restart_loads=returned['loads'],
                  station_frame_entries=returned['frame_entries'])
    if transfer_trailer is not None:
        result.update(trailer_forward=transfer_trailer.hex(), trailer_after_64_frames=inbound[-29:].hex(),
                      trailer_in_fresh_station=station_tail[-29:].hex())
    return result


def main():
    cases = [exercise(False), exercise(True, start_from_basic=True)]
    result = dict(passed=True, total_cases=len(cases), original_sha256=hashlib.sha256(DISK).hexdigest(),
                  method='original_z80_with_substituted_trdos_and_key_ports', cases=cases,
                  native_execution=False, assembly_executed=False)
    report = ROOT / 'Tools/Disasm/Reports/StationFlightCycleVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('2 профиля: вылет, 64 полётных кадра, гиперпереход после запуска из BASIC и возврат к станции')


if __name__ == '__main__':
    main()

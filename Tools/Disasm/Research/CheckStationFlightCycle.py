"""Исполнение оригинальных переходов STATIONF и ACTION через границы TR-DOS."""
import hashlib
import json

from CheckFlightKeyPaths import KeyProbe
from CheckScreenUpdate import PortTrace, put
from TraceFlight import A, C, F, PC, SP, ROOT, Simulator, main as trace
from skoolkit.pagingtracer import SliceableMemory


DISK_DIR = ROOT / 'Tools/Disasm/Disk'
DISK = (DISK_DIR / 'original.trd').read_bytes()
ENTRIES = {row['slot']: row for row in json.loads(
    (DISK_DIR / 'Manifest.json').read_text(encoding='utf-8'))['entries']}


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


def substitute_file_read(cpu, slot, name, return_pc):
    memory, registers = cpu.memory, cpu.registers
    assert registers[PC] == 0x3D13 and (registers[A], registers[C]) == (0, 0x0E)
    assert bytes(memory[0x5CDD:0x5CE6]) == name == DISK[16 * slot:16 * slot + 9]
    assert memory.o7ffd == 0x18 and registers[SP] == 0x5FFD
    assert int.from_bytes(memory[0x5FFD:0x5FFF], 'little') == return_pc
    assert ENTRIES[slot]['parameter'] == 0x6000
    data = payload(slot)
    put(memory, 0x5CDD, DISK[16 * slot:16 * (slot + 1)])
    put(memory, 0x6000, data)
    registers[F] &= 0xFE
    registers[SP] += 2
    registers[PC] = return_pc
    return dict(slot=slot, name=name.decode('ascii'), destination=0x6000, size=len(data),
                return_address=return_pc)


def purchase_return_system(cpu, eligible):
    memory, registers = cpu.memory, cpu.registers
    if eligible:
        # Подготовка допустимого корабля и суммы из исходной строки цены.
        memory[0x9849] = 0
        put(memory, 0x984E, memory[0x95C0:0x95C2])
    ship = memory[0x9849]
    credits = int.from_bytes(memory[0x984E:0x9850], 'little')
    page = memory.o7ffd
    memory.out7ffd(0x16)
    memory[0x6306] = 0x16
    memory[0x983A] = 5
    memory[0x7217] = 23
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
    assert memory[0x98A5] == (0xFE if eligible else 0xFF)
    assert (messages, remaining) == (([], 0) if eligible else ([6], credits))
    assert memory[0x9849] == ship and registers[SP] == entry_sp
    assert memory.o7ffd == memory[0x6306] == 0x16
    memory.out7ffd(page)
    memory[0x6306] = page
    return dict(event=5, equipment_row=23, eligible_fixture=eligible, ship=ship,
                starting_credits=credits, remaining_credits=remaining,
                equipment_byte=memory[0x98A5], queued_messages=messages)


def exercise(equipped, transfer_trailer=None):
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
    to_action = substitute_file_read(cpu, 17, b'ACTION  C', 0x4236)
    run_to(cpu, 0x6000)
    assert registers[SP] == 0x6000 and bytes(memory[0x9BBD:0x9DBD]) == outbound
    if transfer_trailer is not None:
        assert bytes(memory[0x9DA0:0x9DBD]) == transfer_trailer
    flight = trace(['--verify-flight-cycle', '--frames', '65'],
                   boot_simulator=cpu, save_reports=False)
    assert flight['complete_frame_returns'] == 64
    if transfer_trailer is not None:
        assert bytes(memory[0x9DA0:0x9DBD]) == transfer_trailer

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
                  handler=registers[PC])
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
    assert bytes(memory[0x9A1C:0x9A3B]) == station_tail
    if transfer_trailer is not None:
        assert inbound[-29:] == transfer_trailer
        assert station_tail[-29:] == bytes(29)
    returned = trace(['--region', 'station', '--frames', '8'], boot_simulator=cpu, save_reports=False)
    assert returned['reason'] == 'requested_frame_entries' and returned['frame_entries'] == 8
    assert registers[PC] == 0x9A81 and registers[SP] == 0x5FFF and memory[0x98A5] == 0xFF
    result.update(return_requested=True, return_file=to_station, incoming_context_bytes=481,
                  untouched_station_tail_bytes=len(station_tail), station_restart_loads=returned['loads'],
                  station_frame_entries=returned['frame_entries'])
    if transfer_trailer is not None:
        result.update(trailer_forward=transfer_trailer.hex(), trailer_after_64_frames=inbound[-29:].hex(),
                      trailer_in_fresh_station=station_tail[-29:].hex())
    return result


def main():
    cases = [exercise(False), exercise(True)]
    result = dict(passed=True, total_cases=len(cases), original_sha256=hashlib.sha256(DISK).hexdigest(),
                  method='original_z80_with_substituted_trdos_and_key_ports', cases=cases,
                  native_execution=False, assembly_executed=False)
    report = ROOT / 'Tools/Disasm/Reports/StationFlightCycleVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('2 профиля: отказ и покупка в LANG, 64 полётных кадра и возврат к станции')


if __name__ == '__main__':
    main()

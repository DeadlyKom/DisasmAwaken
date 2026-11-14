"""Сверяет авторские списки карты и измеритель расстояния с кодом Awakenv02."""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckCoordinateDistance import reference
from CheckStationFlightCycle import ROOT, payload
from skoolkit.simulator import Simulator
from skoolkit.simutils import A, B, C, D, E, R, T, xB, xC, xD, xE, get_registers


def check_layout(author, flight):
    _, labels, _ = read_entry(author, b'LABELS  a')
    names = (b'MSTARS', b'WAY', b'WAYMASK')
    addresses = {
        name.decode(): int(next(line.split(b'\x04f')[1] for line in labels.split(b'\r')
                                if line.startswith(name + b'\x06')))
        for name in names
    }
    assert list(addresses.values()) == [0x9C8A, 0x9CBD, 0x9CF0]
    one_list = bytes((0xFF,)) * 50 + bytes((0x80,))
    layout = one_list * 2 + bytes((0x22,)) + bytes(10)
    data_origin, data, _ = read_entry(author, b'DATAS   C')
    flight_origin, old_flight, _ = read_entry(flight, b'SP      C')
    copies = (
        ('awk1.trd:DATAS.C', data_origin, data, addresses['MSTARS']),
        ('awk5.trd:SP.C', flight_origin, old_flight, 0x9C88),
        ('Awakenv02:ACTION', 0x6000, payload(17), 0x9C8C),
        ('Awakenv02:STATIONF', 0x6000, payload(4), 0x990A),
    )
    evidence = []
    for source, origin, data, start in copies:
        offset = start - origin
        assert data[offset:offset + len(layout)] == layout
        evidence.append(dict(source=source, saved_points=start, route_points=start + len(one_list),
                             route_order=start + 2 * len(one_list)))
    return dict(exact_bytes_per_copy=len(layout), copies=evidence)


def check_consumers(station):
    _, source, _ = read_entry(station, b'KARTA   a')
    origin, code, _ = read_entry(station, b'KARTA   C')
    assert origin == 0xC000
    assert b'MSTARS-5\r' in source and b'WAY-5\r' in source
    route_start = source.index('ПОКАЗАТЬ МАРШРУТ ЛИНИИ'.encode('cp866'))
    route_lines = source[route_start:].split(b'\r')[:5]
    assert route_lines[1].endswith(b',WAY') and route_lines[2].endswith(b',WAYMASK')
    assert route_lines[4].endswith(b',OUTLINE')

    current = payload(7)
    assert code[0x40F:0x44A].startswith(bytes.fromhex('DD 21 03 99 01 05 00 ED 5B 46 98 DD 09 DD 7E 00'))
    assert current[0x40F:0x44A] == code[0x40F:0x411] + b'\x05' + code[0x412:0x44A]
    assert code[0x140:0x14B] == bytes.fromhex('21 3B 99 11 6E 99 CB 7E CC AC D1')
    assert current[0x140:0x14B] == bytes.fromhex('21 3D 99 11 70 99 CB 7E CC AC D1')
    first_points = [int.from_bytes(raw[0x411:0x413], 'little') + 5 for raw in (code, current)]
    assert first_points == [0x9908, 0x990A]
    return dict(source='awk6.trd:KARTA.a', saved_lookup=0xC40F, saved_lookup_bytes=0x3B,
                route_dispatch=0xC140, route_consumer=0xD1AC,
                saved_lookup_base_before_record=[0x9903, 0x9905], first_saved_points=first_points,
                route_points=[0x993B, 0x993D], route_order=[0x996E, 0x9970])


def check_distance(station):
    origin, archived, _ = read_entry(station, b'KARTA   C')
    current = payload(7)
    assert origin == 0xC000 and len(archived) == len(current) == 0x2E00
    entry, exit_point, result_address = 0xE7BA, 0x3FFF, 0x9908
    old_end = 0xE835
    template = bytearray(archived[entry - origin:old_end - origin])
    for address, old, new in ((0xE801, 0x2F, 0x32), (0xE80E, 0x22, 0x25), (0xE811, 0x1F, 0x22),
                              (0xE822, 0x35, 0x38), (0xE834, 0xF3, 0xF0)):
        assert template[address - entry] == old
        template[address - entry] = new
    insertion = 0xE830 - entry
    assert template[insertion] == 0xC9
    template[insertion:insertion] = b'\x32\x08\x99'
    assert template == current[entry - origin:0xE838 - origin]
    assert archived[0x2835:0x28BB] == current[0x2838:0x28BE]
    assert archived[0x2B00:0x2E00] == current[0x2B00:0x2E00]

    cpus = []
    for source in (archived, current):
        memory = bytearray(65536)
        memory[origin:origin + len(source)] = source
        cpus.append(Simulator(memory))
    initial = get_registers({'SP': 0x7FFE, 'HL': 0x1357, 'IX': 0x2468, 'IY': 0x5C3A,
                             '^HL': 0x369C, '^AF': 0x69CF, 'R': 0xFD}, None, False)
    deltas = (0, 1, 2, 3, 47, 48, 127, 181, 255, 256, 257, 32767, 32768, 32769, 65535)
    cases = 0
    for x0, y0, sign in ((0xFFF0, 0x1234, 1), (0x00F0, 0xFEDC, -1)):
        for dx, dy in product(deltas, repeat=2):
            x1, y1 = (x0 + dx * sign) & 65535, (y0 + dy * sign) & 65535
            expected = reference(current, x0, y0, x1, y1, initial[17] & 1)[0]
            sentinel = expected ^ 0xFF
            before_context = bytes((0x50, 0xFF, 0x64, 0xA7, sentinel, 0xA9, 0xFF))
            for cpu in cpus:
                memory, registers = cpu.memory, cpu.registers
                registers[:] = initial
                registers[B], registers[C], registers[D], registers[E] = y0 & 255, x0 & 255, y0 >> 8, x0 >> 8
                registers[xB], registers[xC], registers[xD], registers[xE] = y1 & 255, x1 & 255, y1 >> 8, x1 >> 8
                memory[0x7FFE:0x8000] = exit_point.to_bytes(2, 'little')
                memory[0x9904:0x990B] = before_context
                cpu.run(entry, exit_point)
            old, new = cpus
            assert old.registers[A] == new.registers[A] == expected
            assert old.memory[0x9904:0x990B] == before_context
            assert new.memory[0x9904:0x990B] == before_context[:4] + bytes((expected,)) + before_context[5:]
            assert old.memory[:result_address] == new.memory[:result_address]
            assert old.memory[result_address + 1:origin] == new.memory[result_address + 1:origin]
            assert all(before == after for index, (before, after) in
                       enumerate(zip(old.registers, new.registers)) if index not in (R, T))
            assert new.registers[T] == old.registers[T] + 13
            assert new.registers[R] == (((old.registers[R] + 1) & 0x7F) | (old.registers[R] & 0x80))
            cases += 1
    return dict(entry=entry, archived_return=0xE830, current_write=0xE830, current_return=0xE833,
                destination=result_address, archived_root_entry=0xE835, current_root_entry=0xE838,
                profiles=cases, extra_tstates=13, other_fixed_ram_preserved_relative_to_archive=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_archive', type=Path)
    args = parser.parse_args()
    with ZipFile(args.source_archive) as archive:
        station = archive.read('awk6.trd')
        result = dict(passed=True, archive_sha256=sha256(args.source_archive.read_bytes()).hexdigest(),
                      layout=check_layout(archive.read('awk1.trd'), archive.read('awk5.trd')),
                      consumers=check_consumers(station), distance=check_distance(station),
                      assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ArchivedMapPointRolesVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print('Сверены четыре копии списков, два входа KARTA и обе версии измерителя расстояния.')


if __name__ == '__main__':
    main()

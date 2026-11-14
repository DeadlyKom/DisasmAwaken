"""Архивные границы второго списка оснащения и их отличие от Awakenv02."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from ProbeShipPreviewCallbacks import Fixture, ROOT, make_context, payload, put
from skoolkit.simutils import H, L


QUANTITIES = 0x98F6
NAMES = 0xF066
QUANTITY_READ = 0x729D


def section(source, first, last):
    lines = source.split(b'\r')
    start = lines.index(first)
    return lines[start + 1:lines.index(last, start + 1)]


def read_declarations(disk):
    _, data, _ = read_entry(disk, b'DATA_M  a')
    _, text, _ = read_entry(disk, b'DATAT   a')
    _, lang, _ = read_entry(disk, b'LANG    a')
    _, scenario, _ = read_entry(disk, b'C_SCENARt')
    quantity_lines = section(data, b'WSKMI', b'ORDER')
    values = [int(match[1].replace(b'#', b'0x'), 0) for line in quantity_lines
              if (match := re.fullmatch(rb'\x06\x8c\x05g\x06\x83(#?[A-F0-9]+)(?:;.*)?', line))]
    assert values[:15] == [0, 0, 0] + [255] * 11 + [128]
    names = [match[1] for line in section(text, b'TWSKM1', b'TMISS1')
             if (match := re.fullmatch(rb' \x05gCR,"([^"]+)"(?:,ET)?', line))]
    assert len(names) == 14 and names[0] == 'Топливо СМРП'.encode('cp866')
    assert b'WSKMI' in b'\r'.join(section(lang, b'U_WSKM', b'U_SHIP'))
    assert b'\r?X=7:{\r' in scenario and b'\r?X=8:{\r' in scenario
    assert b'\r=i+1,=c-I.c,T,^\r' in scenario and b'\r=i-1,=c+I.c,T,^\r' in scenario
    return bytes(values[:15]), names


def check_lang_reader(disk):
    origin, archived, _ = read_entry(disk, b'LANG    C')
    current = payload(5)
    assert origin == 0xC000
    assert archived[0x1EC:0x1FD] == current[0x1EC:0x1FD] and current[0x1FC] == 0x11
    assert archived[0x1FF:0x201] == current[0x1FF:0x201] == b'\x18\xDA'
    assert int.from_bytes(archived[0x1FD:0x1FF], 'little') == 0x98AE
    assert int.from_bytes(current[0x1FD:0x1FF], 'little') == QUANTITIES
    return dict(entry=0xC1EC, load_base=0xC1FC, archived_base=0x98AE,
                current_base=QUANTITIES, instructions_match_except_base=True)


def check_marker(archived):
    _, _, base = make_context()
    station = payload(4)
    assert station[0x38F6:0x3905] == bytes([255]) * 14 + b'\x50'
    profiles = []
    for top in range(14):
        for restored_marker in (False, True):
            fixture = Fixture(base)
            memory, registers = fixture.memory, fixture.sim.registers
            assert bytes(memory[NAMES:0xF0B1]) == station[0x9066:0x90B1]
            if restored_marker:
                put(memory, QUANTITIES, archived)
            put(memory, 0x737D, (top, 0))
            reads = []

            def observe(_, pc):
                if pc == QUANTITY_READ:
                    address = registers[H] * 256 + registers[L]
                    reads.append((address, memory[address]))

            fixture.run(0x73DE, observe)
            assert fixture.wakes == 1 and (memory[0xAEB3], memory[0xAEAB]) == (252, 245)
            count = 15 - top if restored_marker else 21
            assert len(reads) == memory[0x73D9] == count
            assert [address for address, _ in reads] == list(range(QUANTITIES + top, QUANTITIES + top + count))
            if restored_marker:
                assert reads[-1] == (0x9904, 0x80)
            else:
                assert (0x9904, 0x50) in reads and (0x9905, 0xFF) in reads
            profiles.append(dict(top_row=top, archived_quantity_bytes_restored=restored_marker,
                                 read_count=count, last_read=reads[-1]))
    return profiles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_archive', type=Path)
    args = parser.parse_args()
    with ZipFile(args.source_archive) as archive:
        disk = archive.read('awk6.trd')
    quantities, names = read_declarations(disk)
    station = payload(4)
    fuel = b'\r' + names[0] + b'\n'
    delivery = 'Доставка грузов ко времени'.encode('cp866')
    assert station[0x9066:0x90B1].startswith(fuel + delivery + b'\r')
    assert not any(name in station[0x9066:0x90B1] for name in names[1:])
    report = dict(passed=True, archive_sha256=sha256(args.source_archive.read_bytes()).hexdigest(),
                  member='awk6.trd', authored_count='DATA_M.a:WSKMI', authored_text='DATAT.a:TWSKM1',
                  authored_quantities=quantities.hex(), authored_names=[name.decode('cp866') for name in names],
                  original_text_address=NAMES, original_quantity_address=QUANTITIES,
                  original_marker_byte=station[0x3904], original_text_names_present=1,
                  original_has_delivery_after_fuel=True, authored_trade_events=[7, 8],
                  lang_reader=check_lang_reader(disk),
                  profiles=check_marker(quantities), native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/SecondaryEquipmentArchiveLayoutVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Сверены WSKMI, TWSKM1 и 28 исполнений исходного печатателя.')


if __name__ == '__main__':
    main()

"""Сопоставляет резервы D3D в Awakenv02 с исходниками DATA3D, DOS и XR2."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from ClassifyPreviewArchivedStorage import ROWS, SCENE_GAPS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk6.trd')
    archive_origin, old, _ = read_entry(disk, b'D3D     C')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    origin, current, _ = read_entry(original, b'D3D     C')
    assert archive_origin == origin == 0xC000
    assert current[:0x20D6] == old[:0x20D6]
    _, source, _ = read_entry(disk, b'DATA3D  a')
    _, dos, _ = read_entry(disk, b'DOS     a')
    _, macros, _ = read_entry(disk, b'MACRO   a')
    _, equs, _ = read_entry(disk, b'EQUS    a')
    _, xr2, _ = read_entry(disk, b'XR2     a')
    _, first_table, _ = read_entry(disk, b'D9000   d')
    _, second_table, _ = read_entry(disk, b'D9200   d')

    # Два INCBIN и четыре явных резерва страницы L90 и страниц L9C..L9E.
    reserve_page = b'\x06\x8c\x05i\x06\x83#0100\r'
    assert source.count(reserve_page) == 4
    assert b'\x05m"D9000.dat"\r' in source
    assert b'L90\x06\x89\x05f\x06\x82#C200\r\r' + reserve_page in source
    assert b'\x05m"D9200.dat"\r' in source
    for name in (b'L9c', b'L9d', b'L9e'):
        assert name + b'\x06\x89\x05f\x06\x82$.h\r' + reserve_page in source
    assert current[:0x900] == first_table + bytes(0x100) + second_table + bytes(0x300)
    assert all(0x200 <= first < last <= 0x300 for first, last, _ in SCENE_GAPS)

    # Carsb содержит две записи по Olen, первая начинается с десяти явных байтов.
    assert b'Olen\x06\x88\x05f\x06\x82#40\r' in equs
    assert b'\rCarsb\r' in source
    assert b'\x05i\x06\x83Olen-10\r\x06\x8c\x05h\x06\x83#8080\r\x06\x8c\x05i\x06\x83Olen-2\r' in source
    assert current[0xDC0:0xDC7] == bytes.fromhex('00 00 00 00 DC 05 00')
    assert current[0xE00:0xE02] == b'\x80\x80'
    assert current[0xE40:0xE43] == bytes.fromhex('0D 84 AE')

    # DATA3D выравнивает L97, DOS выравнивает начало XR2.
    align_page = b'\x06\x8cADRXX00\r'
    assert b'ADRXX00\x06\x85\x03\xa2\r\x06\x8c\x05i\x06\x83(($-1).h).e-$+256\r' in macros
    assert align_page + b'\rL97\x06\x89\x05f\x06\x82$.h\r' in source
    assert b'\x05n"DATA3D"\r' + align_page + b'\x06\x8c\x05n"XR2"\r' in dos
    table = source.split(b'\rL97', 1)[1].split(b'\r')
    pointers = [line for line in table[1:] if line]
    assert len(pointers) == 11 and all(line.startswith(b'\x06\x8c\x05h\x06\x83') for line in pointers)
    assert b'\x05i\x06\x83(($.h).e)+#C0-$\r' in xr2
    assert current[0x1100:0x110A] == bytes.fromhex('FF 00 77 AA 55 FF 11 55 00 00')

    for first, last, *_ in ROWS:
        assert current[first:last] == bytes(last - first)
    report = dict(passed=True, archive_sha256=digest, source_disk='awk6.trd',
                  common_binary_prefix_bytes=0x20D6,
                  matched_ranges=[list(row[:2]) for row in ROWS],
                  matched_bytes=sum(last - first for first, last, *_ in ROWS),
                  authored_scene_page=[0xC200, 0xC300], authored_queue_page=[0xC700, 0xC800],
                  authored_object_slots=[0xCDC0, 0xCE40], object_slot_stride=0x40,
                  authored_fill_reserve=[0xD10A, 0xD1C0], published_fill_reserve=[0xD110, 0xD1C0],
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/PreviewArchivedStorageVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'matched_ranges'}, indent=2))


if __name__ == '__main__':
    main()

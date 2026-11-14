"""Сверяет заполнение KARTA с авторскими директивами DRAWLIN и CIRCMATH."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from ClassifyMapArchivedAlignment import RESOURCES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk6.trd')
    old_origin, old, _ = read_entry(disk, b'KARTA   C')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    origin, current, _ = read_entry(original, b'KARTA   C')
    assert old_origin == origin == 0xC000
    _, draw, _ = read_entry(disk, b'DRAWLIN a')
    _, circle, _ = read_entry(disk, b'CIRCMATHa')
    _, macros, _ = read_entry(disk, b'MACRO   a')
    _, squares, _ = read_entry(disk, b'CIRCL_TBd')
    _, roots, _ = read_entry(disk, b'korni   d')

    lines = draw.split(b'\r')
    masks_index = lines.index(b'ld1l')
    assert lines[masks_index - 1] == b'\x06\x8c\x05i\x06\x83$-1/16*16-$+16'
    words = [re.fullmatch(rb'\x06\x8c\x05h\x06\x83#([0-9A-F]{4})', line)
             for line in lines[masks_index + 1:masks_index + 9]]
    assert all(words)
    masks = b''.join(int(word[1], 16).to_bytes(2, 'little') for word in words)
    assert current[0x1420:0x1430] == old[0x1420:0x1430] == masks
    assert current[0x1404:0x1418] == old[0x1404:0x1418] and current[0x1417] == 0xC9

    alignment = b'\x06\x8cADRXX00\r'
    assert b'ADRXX00\x06\x85\x03\xa2\r\x06\x8c\x05i\x06\x83(($-1).h).e-$+256\r' in macros
    assert alignment + b'\rl95\r' in draw
    assert alignment + b'LBE00\r\x06\x8c\x05m"CIRCL_TB.dat"' in circle
    assert current[0x1D9C:0x1DB0] == old[0x1D9C:0x1DB0] and current[0x1DAF] == 0xC9
    assert current[0x1E00:0x1E0B] == old[0x1E00:0x1E0B]
    assert current[0x28BD] == old[0x28BA] == 0xC9
    assert old[0x28BB:0x2900] == bytes(0x45)
    assert current[0x2900:0x2E00] == old[0x2900:0x2E00] == squares + roots
    for first, last, *_ in RESOURCES:
        boundary = 16 if first == 0x1418 else 256
        assert ((first - 1) // boundary + 1) * boundary == last
        assert current[first:last] == old[first:last] == bytes(last - first)
    report = dict(passed=True, archive_sha256=digest, source_disk='awk6.trd',
                  published_ranges=[list(row[:2]) for row in RESOURCES],
                  published_bytes=sum(last - first for first, last, *_ in RESOURCES),
                  source_mask_alignment=16, source_page_alignment=256,
                  archived_sqrt_return=origin + 0x28BA, current_sqrt_return=origin + 0x28BD,
                  square_and_root_tables_equal_bytes=0x500, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/MapArchivedAlignmentVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

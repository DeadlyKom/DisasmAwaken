"""Проверяет исходный VOXAL0 по авторскому архиву и данным Awakenv02."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
    disk_origin, archived, _ = read_entry(disk, b'VOXAL0  C')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    current_origin, current, _ = read_entry(original, b'VOXAL0  C')
    assert disk_origin == current_origin == 0xC000
    assert current == archived and len(current) == 0x2C00

    _, space, _ = read_entry(disk, b'SPACE   a')
    _, voxel, _ = read_entry(disk, b'VOXEL   a')
    _, matrix, _ = read_entry(disk, b'GMATRX  a')
    _, macros, _ = read_entry(disk, b'MACRO   a')
    _, labels, _ = read_entry(disk, b'LABELS  a')
    _, palette, _ = read_entry(disk, b'VOX     d')
    _, explosion, _ = read_entry(disk, b'EXPLOSIOv')
    _, teleport, _ = read_entry(disk, b'HIPERJMPv')
    _, cosine, _ = read_entry(disk, b'CSTB    d')

    includes = (b'm"VOX.dat"', b'm"EXPLOSIO.van"', b'm"HIPERJMP.van"', b'n"GMATRX"')
    assert [space.index(line) for line in includes] == sorted(space.index(line) for line in includes)
    assert b'VSPR2:\r' in space and b'VSPR2\x06\x8a\x04f55296\r' in labels
    assert b'GMATRX\x06\x89\x04f58624\r' in labels
    assert len(palette) == 0x400 and len(explosion) == 0x1400 and len(teleport) == 0xD00
    assert current[:0x2500] == palette + explosion + teleport
    setup = voxel[voxel.index(b'\rNWTEL\r'):voxel.index(b'\rNWVOS\r')]
    assert b',VSPR2\r' in setup and b',#00C0\r' in setup and b',#0D\r' in setup
    assert current[0x21C0:0x2500] == teleport[13 * 0xC0:] == bytes(0x340)

    # Проверка границы ADRXX00 в байтах текущей страницы и в авторском исходнике.
    end_of_code = 0xE965
    aligned = ((end_of_code - 1) & 0xFF00) + 256
    assert b'\x06\x8cADRXX00\r' in matrix and b'm"CSTB.dat"' in matrix
    assert b'ADRXX00\x06\x85\x03\xa2\r\x06\x8c\x05i\x06\x83(($-1).h).e-$+256\r' in macros
    alignment = current[end_of_code - current_origin:aligned - current_origin]
    assert current[end_of_code - current_origin - 1] == 0xC9
    assert aligned == 0xEA00 and alignment == bytes(155)
    assert current[0x2A00:0x2C00] == cosine

    report = dict(passed=True, archive_sha256=digest, source_disk='awk1.trd',
                  file_sha256=sha256(current).hexdigest(), full_file_match_bytes=len(current),
                  teleport=dict(file='HIPERJMP.van', source_label='VSPR2', source_setup='NWTEL',
                                start=0xD800, total_bytes=len(teleport), frame_stride=0xC0,
                                frame_count=13, tail_offset=0x21C0, tail_bytes=0x340),
                  alignment=dict(source_macro='ADRXX00', code_end=end_of_code,
                                 table='CSTB.dat', table_start=aligned,
                                 offset=end_of_code - current_origin, bytes=len(alignment)),
                  all_runtime_consumers_proved=False, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/VoxelArchivedLayoutVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

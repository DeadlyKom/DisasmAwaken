"""Сверяет всю исходную страницу DOTB в CONTROL0 с авторским резервом."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


RESOURCES = (
    (0x0546, 0x0600, 'Source/Controls/Resources/DotBufferPageTail.bin', 'CONTROL0_AUTHORED_DOT_BUFFER_TAIL',
     'Конец исходной страницы DOTB после 35 пар Y и X'),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
    _, previous, _ = read_entry(disk, b'CONTROL0C')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    origin, current, _ = read_entry(original, b'CONTROL0C')
    assert origin == 0xC000
    _, source, _ = read_entry(disk, b'SPACE   a')
    _, stars, _ = read_entry(disk, b'STARHSUNa')
    _, labels, _ = read_entry(disk, b'LABELS  a')
    _, root_cache, _ = read_entry(disk, b'KORNI   d')
    _, squares, _ = read_entry(disk, b'#0E#0200d')
    assert len(root_cache) == 0x300 and len(squares) == 0x200
    assert previous[:0x600] == current[:0x600] == root_cache + squares + bytes(0x100)
    assert b'\x05m"#0E#0200.dat"\rDOTB:\r\x06\x8c\x05i\x06\x83#100\r' in source
    assert b'DOTB\x06\x8b\x04f50432\r' in labels
    assert b',DOTB\r' in stars and b',DOTB+1\r' in stars
    result = dict(passed=True, archive_sha256=digest, source='awk1.trd:SPACE.a',
                  authored_label='DOTB', dot_buffer_origin=0xC500, dot_buffer_bytes=0x100,
                  current_known_point_bytes=70, tail_origin=0xC546, tail_bytes=186,
                  matched_control0_prefix=0x600, tail_game_reader_proved=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ControlsArchivedDotBufferVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))
    if args.publish:
        from ClassifyStationWorkspaceResources import publish

        publish(slot=22, origin=origin, ranges=((0x0546, 0x0600),), resources=RESOURCES,
                tag='ControlsArchivedDotBuffer', resource_module='CheckControlsArchivedDotBuffer',
                resource_name='CONTROLS_ARCHIVED_DOT_BUFFER', proof=dict(archive_proof=path.name))


if __name__ == '__main__':
    main()

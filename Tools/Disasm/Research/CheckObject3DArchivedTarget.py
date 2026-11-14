"""Сверяет исходный пакет TARGET и его четыре хвостовых байта с OBJECTS2.a."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


RESOURCES = (
    (0x18B6, 0x18BA, 'Source/Action/Resources/TargetModelTail.bin', 'OBJECT3D_AUTHORED_TARGET_TAIL',
     'Четыре исходных байта TARGET после обоих ограничителей потока'),
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
    _, old, _ = read_entry(disk, b'OBJECT3DC')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    origin, current, _ = read_entry(original, b'OBJECT3DC')
    assert origin == 0xC000 and current == old and len(current) == 10580
    _, src, _ = read_entry(disk, b'OBJECTS2a')
    _, labels, _ = read_entry(disk, b'LABELS  a')
    assert b'TARGET\x06\x89\x04f55474\r' in labels and b'TRASH\x06\x8a\x04f55482\r' in labels
    lines = src.split(b'\r')
    begin, end = lines.index(b'TARGET:'), lines.index(b'TRASH:')
    directives = [re.fullmatch(rb'\x06\x8a\x05g(#[A-F0-9]{2}(?:,#[A-F0-9]{2})*)', line)
                  for line in lines[begin + 1:end] if line]
    assert len(directives) == 3 and all(directives)
    packet = bytes(int(value[1:], 16) for row in directives for value in row[1].split(b','))
    assert packet == current[0x18B2:0x18BA] == b'\x01\x01' + bytes(6)
    result = dict(passed=True, archive_sha256=digest, original_object3d_sha256=sha256(current).hexdigest(),
                  archive_file_match_bytes=len(current), source='awk1.trd:OBJECTS2.a',
                  authored_label='TARGET', packet_start=0xD8B2, authored_bytes=8, parsed_bytes=4,
                  tail_start=0xD8B6, tail_bytes=4, following_label='TRASH', following_start=0xD8BA,
                  tail_game_reader_proved=False, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/Object3DArchivedTargetVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))
    if args.publish:
        from ClassifyStationWorkspaceResources import publish

        publish(slot=24, origin=origin, ranges=((0x18B6, 0x18BA),), resources=RESOURCES,
                tag='Object3DArchivedTarget', resource_module='CheckObject3DArchivedTarget',
                resource_name='OBJECT3D_ARCHIVED_TARGET', proof=dict(archive_proof=path.name))


if __name__ == '__main__':
    main()

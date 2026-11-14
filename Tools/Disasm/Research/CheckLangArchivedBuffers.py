"""Сверяет конец резерва ARGD с авторским LANG.a и байтами Awakenv02."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


RESOURCES = (
    (0x0A85, 0x0A8F, 'Source/Text/Resources/AssignmentBufferTail.bin', 'LANG_AUTHORED_ASSIGNMENT_BUFFER_TAIL',
     'Последние десять байтов дополнительного буфера ARGD перед сценарием'),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk6.trd')
    origin, old, _ = read_entry(disk, b'LANG    C')
    _, author, _ = read_entry(disk, b'LANG    a')
    _, script, _ = read_entry(disk, b'C_SCENARt')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    current_origin, current, _ = read_entry(original, b'LANG    C')
    assert origin == current_origin == 0xC000
    assert b'ARG\x06\x89\x05i20\r' in author and b'ARGD\x06\x88\x05i20\r' in author
    assert b'CHECK_SCENARY\r\x06\x8c\x05m"C_SCENAR.txt"\r' in author
    assert current[0x0A50:0x0A67] == old[0x0A50:0x0A67] == bytes.fromhex(
        '6E C6 74 0E C1 70 77 C1 76 81 C1 6D 89 C1 65 91 C1 4B 99 C1 52 A7 C1')
    assert current[0x0A67:0x0A8F] == old[0x0A67:0x0A8F] == bytes(40)
    assert current[0x0A8F:0x0AA5] == old[0x0A8F:0x0AA5] == script[:22]
    result = dict(passed=True, archive_sha256=digest, source='awk6.trd:LANG.a',
                  argument_buffer=[0xCA67, 0xCA7B], additional_buffer=[0xCA7B, 0xCA8F],
                  known_assignment_words_bytes=10, published_tail=[0xCA85, 0xCA8F],
                  script_start=0xCA8F, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/LangArchivedBuffersVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))
    if args.publish:
        from ClassifyStationWorkspaceResources import publish

        publish(slot=5, origin=origin, ranges=((0x0A85, 0x0A8F),), resources=RESOURCES,
                tag='LangArchivedBuffers', resource_module='CheckLangArchivedBuffers',
                resource_name='LANG_ARCHIVED_BUFFERS', proof=dict(archive_proof=path.name))


if __name__ == '__main__':
    main()

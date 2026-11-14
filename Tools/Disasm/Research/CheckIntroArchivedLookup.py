"""Сверяет 64 байта таблицы вступления с авторским IM_IT и двумя машинными копиями."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from PackedResourceCodec import decode


def source_table(source):
    lines = source.split(b'\r')
    start = lines.index(b'IM_IT')
    values = bytearray()
    for line in lines[start + 1:]:
        if not line:
            continue
        match = re.fullmatch(rb'(?:\x06\x8c\x05g\x06\x83| \x05g)(#[A-F0-9]{2}(?:,#[A-F0-9]{2}){7})', line)
        assert match, line
        values.extend(int(value[1:], 16) for value in match[1].split(b','))
        if len(values) == 64:
            return bytes(values)
    raise AssertionError('неполная таблица IM_IT')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
    original = ROOT / 'Tools/Disasm/Extracted/Active/03_AWAKEN.B.sectors.bin'
    intro = original.read_bytes()
    table = intro[0x363:0x3A3]
    assert table[-1] == 0x29
    sources = {}
    for entry in (b'TUNEL   a', b'HIPER   a', b'DOOM    a'):
        _, source, _ = read_entry(disk, entry)
        assert source_table(source) == table
        sources[entry[:8].decode().strip() + '.a'] = sha256(source).hexdigest()
    effects = {}
    for entry, offset in ((b'EFF     c', 0x74F), (b'EFF1    c', 0x1CC)):
        _, packed, tail = read_entry(disk, entry)
        unpacked = decode(packed, tail)['data']
        assert unpacked.count(table) == 1 and unpacked.find(table) == offset
        effects[entry[:8].decode().strip() + '.c'] = offset
        if entry == b'EFF1    c':
            # До таблицы и после неё меняются абсолютные операнды, последовательность команд совпадает.
            assert unpacked[offset - 20:offset - 6] == intro[0x363 - 20:0x363 - 6]
            after = offset + len(table)
            assert all(unpacked[after + i] == intro[0x3A3 + i] for i in (0, 3, 4, 7, 10, 11, 12, 13))
    assert intro[0x482:0x484] == bytes.fromhex('06 3F')
    result = dict(passed=True, archive_sha256=digest, archive_disk='awk1.trd', source_tables=sources,
                  unpacked_table_offsets=effects, table_sha256=sha256(table).hexdigest(),
                  intro_file_offsets=[0x363, 0x3A3], intro_address=0x6663,
                  parameters_read_by_current_builder=63, last_index=63, last_value=table[-1],
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/IntroArchivedLookupVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

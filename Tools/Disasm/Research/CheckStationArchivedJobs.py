"""Устанавливает происхождение JLIST между SETSI/SETGI и CNKR."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from StationArchivedJobs import START, END, ORIGIN


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk6.trd')
    _, source, _ = read_entry(disk, b'DATA_M  a')
    _, jobs, _ = read_entry(disk, b'BLOCK2  a')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    _, station, _ = read_entry(original, b'STATIONFC')

    lines = source.split(b'\r')
    start, end = lines.index(b'JLIST'), lines.index(b'CNKR')
    declarations = [line for line in lines[start:end] if b'\x05i' in line]
    assert declarations == [b' \x05i160']
    settings = bytearray()
    for line in lines[lines.index(b'SETSI') + 1:start]:
        if b'\x05g' not in line:
            continue
        item = re.search(rb'\x05g(?:"([^"]*)"|(\d+))', line)
        assert item
        settings.extend(item[1] if item[1] is not None else bytes([int(item[2])]))
    assert len(settings) == 58 and settings == station[START - len(settings):START]
    trade = bytearray()
    for line in lines[end + 3:end + 6]:
        row = re.fullmatch(rb' \x05g(\d+):\x05h(\d+):\x05g(\d+),(\d+)', line)
        assert row
        capacity, price, speed, status = map(int, row.groups())
        trade.extend(bytes([capacity]) + price.to_bytes(2, 'little') + bytes([speed, status]))
    assert len(trade) == 15 and trade == station[END:END + len(trade)]
    assert station[START:END] == bytes(160)

    assert jobs.count(b'\x03\x8d,JLIST\r') == 2
    assert jobs.count(b'\x03w,10\r') >= 2 and b'\x03\x8a,16\r' in jobs
    instructions = jobs.split(b'\rNEWJ\r', 1)[1]
    for displacement in (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15):
        store = b'\x06\x8c\x05 \x06\x83\x03\x83+' + str(displacement).encode() + b'),'
        assert store in instructions
    assert b'\x03\x83+6)' in jobs
    assert 'БИТ 7=1'.encode('cp866') in jobs
    immediate_matches = original.count(ORIGIN.to_bytes(2, 'little'))
    assert immediate_matches == 1 and original.find(ORIGIN.to_bytes(2, 'little')) == 0x35552
    result = dict(passed=True, archive_sha256=digest, source='awk6.trd:DATA_M.a',
                  archived_jobs_code='awk6.trd:BLOCK2.a', before_exact_bytes=58, after_exact_bytes=15,
                  start=ORIGIN, end_exclusive=ORIGIN + 160, record_count=10, record_bytes=16,
                  original_file_offsets=[START, END], original_literal_hits=[0x35552],
                  current_game_consumer_proved=False, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/StationArchivedJobsVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

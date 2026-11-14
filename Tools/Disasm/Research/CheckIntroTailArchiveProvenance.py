"""Сравнение хвоста экранного потока с исходным TRD и авторскими архивами."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckStationFlightCycle import DISK, ENTRIES, ROOT


MEMBERS = {*(f'awk{i}.trd' for i in range(1, 7)), 'AWAKEN_D.SCL', 'AWAK_SDC.SCL', 'SPACE.SCL'}
SPANS = dict(preceding_unknown_bytes=(0x2C6B, 0x2C94), final_12_unknown_bytes=(0x2C88, 0x2C94),
             scan_entry=(0x2C94, 0x2CA6), sector_tail=(0x2C6B, 0x2D00), unpacker_entry=(0x2631, 0x264B))


def find_offsets(data, pattern):
    offsets = []
    offset = data.find(pattern)
    while offset != -1:
        offsets.append(offset)
        offset = data.find(pattern, offset + 1)
    return offsets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archives', type=Path, nargs='+')
    args = parser.parse_args()
    entry = ENTRIES[3]
    start = entry['offset']
    source = DISK[start:start + entry['allocated_length']]
    patterns = {name: source[begin:end] for name, (begin, end) in SPANS.items()}
    original_matches = {name: find_offsets(DISK, pattern) for name, pattern in patterns.items()}
    assert original_matches == {name: [start + begin] for name, (begin, _) in SPANS.items()}

    rows = {}
    for path in args.archives:
        with ZipFile(path) as archive:
            for member in sorted(MEMBERS.intersection(archive.namelist())):
                assert member not in rows
                data = archive.read(member)
                matches = {name: find_offsets(data, pattern) for name, pattern in patterns.items()}
                if member == 'AWAK_SDC.SCL':
                    assert data[:8] == b'SINCLAIR' and int.from_bytes(data[-4:], 'little') == sum(data[:-4])
                    assert data[9:18] == b'_awaken_B'
                    allocation = 9 + 14 * data[8]
                    assert source == data[allocation:allocation + len(source)]
                    assert matches == {name: [allocation + begin] for name, (begin, _) in SPANS.items()}
                else:
                    assert not any(matches.values()), (member, matches)
                rows[member] = dict(bytes=len(data), sha256=sha256(data).hexdigest(), matches=matches)
    assert set(rows) == MEMBERS
    result = dict(passed=True, physical_awaken_bytes=len(source), original_matches=original_matches,
                  archive_members=rows, release_allocation_identical=True,
                  algorithmic_or_relocated_copies_excluded=False, unknown_byte_purpose_proved=False,
                  assembly_executed=False)
    encoded = json.dumps(result, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/IntroTailArchiveProvenanceVerification.json').write_text(encoded, encoding='utf-8')
    print('Сверены девять образов. Полная копия выделенной области AWAKEN найдена в AWAK_SDC.SCL.')


if __name__ == '__main__':
    main()

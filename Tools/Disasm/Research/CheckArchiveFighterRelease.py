"""Сверка архивных секторов MK-II с опубликованным демо 0.2."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckArchiveMenuHandoff import ARCHIVE_ROWS
from CheckStationFlightCycle import DISK, ROOT


KEY_ROWS = {
    0xFEFE: ('Caps Shift', 'Z', 'X', 'C', 'V'),
    0xFDFE: tuple('ASDFG'),
    0xFBFE: tuple('QWERT'),
    0xF7FE: tuple('12345'),
    0xEFFE: tuple('09876'),
    0xDFFE: tuple('POIUY'),
    0xBFFE: ('En', 'L', 'K', 'J', 'H'),
    0x7FFE: ('Space', 'Symbol Shift', 'M', 'N', 'B'),
}


def check_controls(engine, readme):
    text = readme.decode('ascii')
    assert 'Mortal Kombat - II' in text and 'demo 0.2' in text and 'Looker\'2004' in text
    pairs = []
    for line in text.splitlines():
        body = re.sub(r'^F[12]\s*-\s*', '', line.strip())
        if match := re.fullmatch(r'([A-Z7]|En)\s*-\s*([a-z]+(?: [a-z]+)*)', body):
            pairs.append(match.groups())
    assert len(pairs) == len(dict(pairs)) == 18
    labels = dict(pairs)

    def keys(start, count):
        result = []
        for offset in range(start, start + 3 * count, 3):
            port = int.from_bytes(engine[offset:offset + 2], 'little')
            mask = engine[offset + 2]
            assert mask in (1, 2, 4, 8, 16)
            key = KEY_ROWS[port][mask.bit_length() - 1]
            result.append(dict(key=key, role=labels[key], port=port, mask=mask))
        return result

    target = int.from_bytes(engine[0x4DE:0x4E0], 'little') - 0x4000
    rules = [tuple(engine[offset:offset + 5])
             for offset in range(target + 1, target + 1 + engine[target] * 5, 5)]
    profiles = []
    for state in (0x4842, 0x4895):
        offset = state - 0x4000
        primary = keys(offset + 0x1E, 5)
        mirror = keys(offset + 0x2D, 5)
        extra = keys(offset + 0x3C, 4)
        assert [row['role'] for row in primary] == ['jump', 'crouch', 'right', 'left', 'block']
        assert mirror == [primary[0], primary[1], primary[3], primary[2], primary[4]]
        assert [row['role'] for row in extra] == ['low punch', 'high punch', 'low kick', 'high kick']
        for rows, is_primary in ((primary, True), (extra, False)):
            for bit, row in enumerate(rows):
                first, second = (1 << bit, 0) if is_primary else (0, 1 << bit)
                row['action_from_idle'] = next(code for pm, pv, em, ev, code in rules
                                               if first & pm == pv and second & em == ev)
        assert [row['action_from_idle'] for row in primary] == [3, 4, 1, 2, 9]
        assert [row['action_from_idle'] for row in extra] == [12, 13, 14, 15]
        profiles.append(dict(record=state, primary=primary, mirrored_key_order=[row['key'] for row in mirror], extra=extra))
    assert set(labels) == {row['key'] for profile in profiles for row in profile['primary'] + profile['extra']}
    return profiles


def compare_release(archive_path):
    member = 'MKDEMO2.SCL'
    with ZipFile(archive_path) as bundle:
        scl = bundle.read(member)
    assert scl[:9] == b'SINCLAIR\x13' and int.from_bytes(scl[-4:], 'little') == sum(scl[:-4])
    archive_keys = {slot: key for slot, key, *_ in ARCHIVE_ROWS}
    position = 9 + 14 * scl[8]
    rows = []
    for index, slot in enumerate(range(30, 48)):
        header = scl[9 + 14 * index:23 + 14 * index]
        entry = DISK[16 * slot:16 * (slot + 1)]
        key = header[:9]
        if slot in archive_keys:
            assert key == archive_keys[slot] and entry[0] == 0 and entry[1:14] == header[1:14]
        else:
            assert entry[:14] == header
        size = 256 * header[13]
        offset = (16 * entry[15] + entry[14]) * 256
        physical = scl[position:position + size]
        assert len(physical) == size and physical == DISK[offset:offset + size]
        if slot == 46:
            engine = physical
        rows.append(dict(scl_index=index, trd_slot=slot, published_key=key.decode('ascii'),
                         original_header_hex=entry.hex(), original_disk_offset=offset,
                         logical_bytes=int.from_bytes(header[11:13], 'little'), allocated_bytes=size,
                         physical_sha256=sha256(physical).hexdigest()))
        position += size

    header = scl[9 + 14 * 18:9 + 14 * 19]
    assert header[:9] == b'readme  t' and position + header[13] * 256 == len(scl) - 4
    readme_length = int.from_bytes(header[11:13], 'little')
    readme = scl[position:position + readme_length]
    assert readme not in DISK
    matched = sum(row['allocated_bytes'] for row in rows)
    assert matched == 972 * 256 and len(rows) == 18
    return dict(passed=True, archive_sha256=sha256(archive_path.read_bytes()).hexdigest(), scl_member=member,
                scl_sha256=sha256(scl).hexdigest(), original_disk_sha256=sha256(DISK).hexdigest(),
                scl_checksum_verified=True, matching_allocated_bytes=matched, files=rows,
                readme_sha256=sha256(readme).hexdigest(), readme_logical_bytes=readme_length,
                readme_exact_copy_in_trd=False, controls=check_controls(engine, readme), assembly_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release_archive', type=Path)
    result = compare_release(parser.parse_args().release_archive)
    (ROOT / 'Tools/Disasm/Reports/ArchiveFighterReleaseVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', 'utf-8')
    print('Сверены 972 сектора из 18 файлов MK-II и 18 назначений клавиш.')


if __name__ == '__main__':
    main()

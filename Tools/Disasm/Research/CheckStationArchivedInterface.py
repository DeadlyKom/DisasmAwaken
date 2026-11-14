"""Сверяет поля записей OBJECT.a и начальный список Sur1 с исходным STATIONF."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckStationFlightCycle import DISK, ROOT, payload


WORD = b'\x06\x8c\x05h\x06\x83'
BYTE = b'\x06\x8c\x05g\x06\x83'


def read_descriptors(lines):
    assert lines[29].decode('cp866').endswith('РЕЗЕРВ')
    rows = {}
    for index, line in enumerate(lines):
        if not (line.startswith(WORD) and line.endswith(b'_,0')):
            continue
        name = line[len(WORD):-2].decode('ascii')
        flags, text, coords = (lines[index - step] for step in (4, 3, 1))
        assert flags.startswith(BYTE + b'%') and text.startswith(BYTE)
        text_id = int(text[len(BYTE):].split(b';', 1)[0])
        bounds = re.search(rb'#([A-F0-9]{4}),#([A-F0-9]{4})$', coords)
        assert bounds and name not in rows
        rows[name] = bytes((int(flags[len(BYTE) + 1:], 2), text_id)) + b''.join(
            int(value, 16).to_bytes(2, 'little') for value in bounds.groups())
    assert len(rows) == 51
    return rows


def compare_interface(archive_path):
    with ZipFile(archive_path) as archive:
        _, data, _ = read_entry(archive.read('awk6.trd'), b'OBJECT  a')
    lines = data.split(b'\r')
    marker = lines.index(b'Sur1')
    older = read_descriptors(lines[:marker])
    list_words = [line[len(WORD):].split(b';', 1)[0].decode('ascii')
                  for line in lines[marker + 1:] if line.startswith(WORD)]
    assert len(list_words) == 14 and list_words[-1] == '#0101'
    assert set(list_words[:-1]) <= set(older)
    assert not any(lines[marker + 19:])

    station = payload(4)
    base, list_start = 0x90FD, 0x93DE
    assert station[list_start - 1] == 0x80 and list_start - 1 - base == 46 * 16
    draw_indices, matched = {}, {}
    reserved = bytearray()
    for index in range(46):
        start = base + 16 * index
        row = station[start:start + 16]
        signature = row[4:6] + row[8:12]
        candidates = [name for name, fields in older.items() if fields == signature]
        assert len(candidates) <= 1
        if candidates:
            matched[index] = candidates[0]
        handler = int.from_bytes(row[12:14], 'little')
        assert handler not in draw_indices
        draw_indices[handler] = index
        reserved.extend(row[14:16])
    assert set(range(46)) - matched.keys() == {2, 6, 31, 32, 33}
    assert reserved == bytes(92)
    words = [int.from_bytes(station[offset:offset + 2], 'little')
             for offset in range(list_start, 0x93F4, 2)]
    assert words[-1] == 0x0101 and station[0x93F4:] == bytes(0xC0C)
    indices = [draw_indices[handler] for handler in words[:-1]]
    assert indices == [0, 2, 3, 4, 5, 6, 7, 8, 9, 45]
    common = [matched[index] for index in indices if index in matched]
    assert common == [name for name in list_words[:-1] if name in common]
    return dict(passed=True, original_disk_sha256=sha256(DISK).hexdigest(),
                archive_sha256=sha256(archive_path.read_bytes()).hexdigest(), source='awk6.trd:OBJECT.a',
                authored_records=len(older), current_records=46, reserved_field_offset=14,
                current_reserved_zero_bytes=len(reserved), descriptor_exact_nonpointer_matches=matched,
                authored_draw_handlers=list_words[:-1], current_draw_indices=indices,
                exact_descriptor_matches_in_both_draw_lists=common, sentinel=words[-1],
                author_object_source_ends_at_list=True, current_bytes_after_draw_list=len(station) - 0x93F4,
                original_purpose_of_entire_tail_proved=False, assembly_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    result = compare_interface(parser.parse_args().archive)
    (ROOT / 'Tools/Disasm/Reports/StationArchivedInterfaceVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', 'utf-8')
    print('Подтверждены резервное слово 46 записей и происхождение списка рисователей станции.')


if __name__ == '__main__':
    main()

"""Сверка ADRXX00 и всех слов таблицы объектов с авторскими 3DTABS.a и LABELS.a."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckActionParameterActivation import flat_action
from CheckControlsArchivedHyperEffect import read_entry
from CheckStationFlightCycle import DISK, ROOT, payload


WORD = b'\x06\x8c\x05h\x06\x83'
BYTE = b'\x06\x8c\x05g\x06\x83'
ALIGN = b'\x06\x8cADRXX00'


def read_table(source, labels):
    lines = source.split(b'\r')
    first, end = lines.index(ALIGN), next(i for i, line in enumerate(lines) if line.startswith(b'OBJBUF:'))
    assert b'\x05g\x06\x83#7F,#10' in lines[first - 7]
    assert lines[first + 5].startswith(b'L97:') and lines[first + 5].endswith(b'$.h')
    values = {}
    for line in labels.split(b'\r'):
        if match := re.fullmatch(rb'(\w+)\x06.\x04f(\d+)', line):
            values[match[1].decode('ascii').upper()] = int(match[2])
    assert values['L97'] == 0x9F
    rows = []
    for line in lines[first + 6:end]:
        if match := re.fullmatch(rb'(\w+):.*\$\.b', line):
            name = match[1].decode('ascii')
            offset, selector = 4 * len(rows), values[name.upper()]
            assert selector == offset & 255, (name, selector, offset)
            rows.append(dict(index=name, table_offset=offset, byte_selector=selector, targets=[]))
        elif line.startswith(WORD):
            for symbol in line[len(WORD):].decode('ascii').split(','):
                rows[-1]['targets'].append(dict(symbol=symbol, address=values[symbol.upper()]))
    assert len(rows) == 71 and all(len(row['targets']) == 2 for row in rows)
    return rows


def check_station_templates(disk, table_rows):
    _, generator, _ = read_entry(disk, b'OBJGENERa')
    _, entry, _ = read_entry(disk, b'SPACE   a')
    assert b'\x06\x8c\x05n"OBJGENER"\r' in entry
    lines = generator.split(b'\r')
    assert WORD.replace(b'\x05h', b'\x05 ') + b'\x03\x8b,STATTB' in lines
    start = lines.index(b'STATTB') + 1
    names = [re.fullmatch(re.escape(WORD) + rb'(ST(?:[1-9]|1[0-6])k)', line)[1]
             for line in lines[start:start + 16]]
    assert len(set(names)) == 16 and names[11] == b'ST16k'
    by_name = {row['index']: row for row in table_rows}
    memory = bytes(flat_action())
    template_rows = []
    for index, name in enumerate(names):
        offset = lines.index(name) + 1
        coordinates, model, end = lines[offset:offset + 3]
        assert coordinates == WORD + b'#0000,#0000,#0000' and end == WORD + b'#80FF'
        author_index, = re.fullmatch(re.escape(BYTE) + rb'(IST\d+),#00', model).groups()
        assert author_index == b'I' + name[:-1]
        author = by_name[author_index.decode('ascii')]
        selector = author['byte_selector']
        source_pointer = 0x7799 + index * 2
        pointer = int.from_bytes(memory[source_pointer:source_pointer + 2], 'little')
        assert pointer == 0x77B9 + 10 * (int(name[2:-1]) - 1)
        assert memory[pointer:pointer + 10] == bytes(6) + bytes((selector, 0, 255, 128))
        actual = table_rows[selector // 4]
        template_rows.append(dict(index=index, name=name.decode('ascii'), pointer=pointer,
                                  selector=selector, authored_pair=author['index'],
                                  selected_pair=actual['index'], authored_pair_offset=author['table_offset'],
                                  selected_targets=actual['targets']))
    mismatches = [(row['index'], row['authored_pair'], row['selected_pair'])
                  for row in template_rows if row['authored_pair'] != row['selected_pair']]
    assert mismatches == [(11, 'IST16', 'IPOL1')]
    return dict(source='awk1.trd:OBJGENER.a:STATTB', table_address=0x7799,
                matched_template_bytes=160, rows=template_rows, alias_indices=[11])


def check_alignment(archive_path):
    with ZipFile(archive_path) as archive:
        source_disk = archive.read('awk1.trd')
        compiled_disk = archive.read('awk5.trd')
    _, source, _ = read_entry(source_disk, b'3DTABS  a')
    _, labels, _ = read_entry(source_disk, b'LABELS  a')
    _, macros, _ = read_entry(source_disk, b'MACRO   a')
    assert b'ADRXX00\x06\x85\x03\xa2\r\x06\x8c\x05i\x06\x83(($-1).h).e-$+256\r' in macros
    rows = read_table(source, labels)
    words = b''.join(target['address'].to_bytes(2, 'little') for row in rows for target in row['targets'])
    assert len(words) == 284
    datas_origin, datas, _ = read_entry(source_disk, b'DATAS   C')
    sp_origin, sp, _ = read_entry(compiled_disk, b'SP      C')
    objects_origin, old_objects, _ = read_entry(source_disk, b'OBJECT3DC')
    assert (datas_origin, sp_origin, objects_origin) == (0x8C00, 0x6000, 0xC000)
    current = payload(17)
    assert old_objects == payload(24)
    assert current[0x3E00:0x3F1C] == datas[0x1300:0x141C] == words
    assert sp[0x3F00:0x3F70] == words[:112] and sp[0x3F70] != words[112]

    settings = current[0x3D4C:0x3D82]
    assert settings == datas[0x1212:0x1248] == sp[0x3E10:0x3E46]
    final_keys = bytes.fromhex('F7 01 BF 08 FB 01 FD 04 7F 10')
    assert datas[0x125A:0x1264] == sp[0x3E58:0x3E62] == current[0x3D94:0x3D9E] == final_keys
    assert current[0x3D9E:0x3DA0] == b'\0\0'
    ranges = []
    for name, blob, origin, start, table in (
        ('DATAS.C', datas, datas_origin, 0x9E64, 0x9F00),
        ('SP.C', sp, sp_origin, 0x9E62, 0x9F00),
        ('ACTION.C', current, 0x6000, 0x9DA0, 0x9E00),
    ):
        assert ((start - 1) & 0xFF00) + 256 == table
        assert blob[start - origin:table - origin] == bytes(table - start)
        ranges.append(dict(file=name, alignment_start=start, table_start=table, bytes=table - start))
    assert 0x9BBD + 512 == 0x9DBD and 0x9E00 - 0x9DBD == 67
    aliases = [dict(tail_index=row['index'], selector=row['byte_selector'],
                    selected_index=rows[row['byte_selector'] // 4]['index']) for row in rows[64:]]
    assert [row['selector'] for row in aliases] == list(range(0, 28, 4))
    return dict(passed=True, original_disk_sha256=sha256(DISK).hexdigest(),
                archive_sha256=sha256(archive_path.read_bytes()).hexdigest(), macro='ADRXX00',
                source='awk1.trd:3DTABS.a', label_source='awk1.trd:LABELS.a',
                archive_model_file_match_bytes=len(old_objects), matching_table_bytes=len(words),
                alignment_ranges=ranges, published_ranges=[[0x3DBD, 0x3E00]],
                current_alignment_bytes_inside_state_transfer=29, current_alignment_bytes_after_state_transfer=67,
                original_table_rows=rows, byte_selector_aliases=aliases,
                station_templates=check_station_templates(source_disk, rows), assembly_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    result = check_alignment(parser.parse_args().archive)
    (ROOT / 'Tools/Disasm/Reports/ActionArchivedObjectTableVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', 'utf-8')
    print('Сверены ADRXX00, 142 указателя и 10580 байтов моделей OBJECT3D.')


if __name__ == '__main__':
    main()

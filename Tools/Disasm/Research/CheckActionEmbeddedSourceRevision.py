"""Сверяет встроенную редакцию 3DTABS и её начальные данные с авторским архивом."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from InspectActionEquipmentNotes import decode_rows


ARCHIVE_START, ARCHIVE_END = 0x086F, 0x16E9
ACTION_START, ACTION_END = 0x516F, 0x6000
TO_FE = (114, 118, 122, 125, 131, 143, 145, 149, 153, 155, 170, 172, 174, 175, 176, 177, 178)


def reproduce_revision(archived, embedded):
    lines = archived.split(b'\r')
    assert len(lines) == 207 and lines[20] == lines[56] == lines[191] == b''
    assert lines[52] == b'SKIMMER:\x06\x84\x05g\x06\x83#FF'
    lines[52] = lines[52][:-3] + b'0'
    changed = [(index, b'#FF', b'#FE') for index in TO_FE]
    changed.extend(((116, b'#FE', b'#FF'), (165, b'0', b'200'), (167, b'0', b'10')))
    for index, old, new in changed:
        code, comment = lines[index].split(b';', 1)
        assert code == b'\x06\x8c\x05g\x06\x83' + old
        lines[index] = b'\x06\x8c\x05g\x06\x83' + new + b';' + comment
    lines[191:191] = [b'']
    lines[56:57] = ['Воин рат'.encode('cp866'), b'PIRCO:\x06\x86\x05h\x06\x830']
    del lines[20]
    assert len(lines) == 208 and b'\r'.join(lines) == embedded
    return dict(archived_rows=207, embedded_rows=208, equipment_literal_changes=len(changed),
                skimmer_literal=[255, 0], pirate_score_word_added=True,
                removed_empty_row_before_time=True, added_empty_row_before_order=True)


def player_prefix(source):
    data = bytearray()
    start, end = source.index(b'TIME:'), source.index(b'TWRI:')
    declaration = re.compile(rb'(?:[A-Z]+:)?\x06[\x80-\x8C]\x05([gh])\x06\x83([#0-9A-F,]+)(?:;.*)?')
    for line in source[start:end].split(b'\r'):
        if not (match := declaration.fullmatch(line)):
            continue
        width = 1 if match[1] == b'g' else 2
        for literal in match[2].split(b','):
            value = int(literal[1:], 16) if literal.startswith(b'#') else int(literal)
            data.extend(value.to_bytes(width, 'little'))
    return data


def equipment(source):
    start = source.index(b'FUEL:')
    end = source.index('СОСТОЯНИЕ НОВОСТЕЙ'.encode('cp866'))
    data = bytes(row['value'] for row in decode_rows(source[start:end], 'FUEL'))
    assert len(data) == 49 and data[33] == data[48] == 0x80
    return data


def compare_machine_data(disk, archived_source, embedded, action):
    origin, datas, _ = read_entry(disk, b'DATAS   C')
    _, raw_labels, _ = read_entry(disk, b'LABELS  a')
    labels = raw_labels.split(b'\r')
    for label, address in ((b'TIME', 0x9BBD), (b'FUEL', 0x9C0E), (b'WSKMI', 0x9C30), (b'NEWS', 0x9C3F)):
        line, = (line for line in labels if line.startswith(label + b'\x06'))
        assert int(line.split(b'\x04f')[1]) == address
    old, new = player_prefix(archived_source), player_prefix(embedded)
    assert len(old) == 21 and len(new) == 23
    assert old == datas[0x9BBD - origin:0x9BD2 - origin] and new == action[0x3BBD:0x3BD4]
    assert old[:15] == new[:15] and old[15:17] == b'\xFF\x00' and new[15:19] == bytes(4)
    assert old[17:] == new[19:]
    old, new = equipment(archived_source), equipment(embedded)
    assert old == datas[0x9C0E - origin:0x9C3F - origin] and new == action[0x3C10:0x3C41]
    differences = [
        dict(old_address=0x9C0E + index, new_address=0x9C10 + index, old=before, new=after)
        for index, (before, after) in enumerate(zip(old, new, strict=True)) if before != after
    ]
    assert len(differences) == 20
    assert datas[0x9C3F - origin:0x9C86 - origin] == action[0x3C41:0x3C88]
    return dict(archived_player_prefix_bytes=21, embedded_player_prefix_bytes=23,
                score_address=0x9BCE, equipment_bytes_per_version=49, equipment_changes=differences,
                equal_news_and_order_bytes=71)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    archive_hash = sha256(args.archive.read_bytes()).hexdigest()
    assert archive_hash == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
    _, source, _ = read_entry(disk, b'3DTABS  a')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    origin, action, _ = read_entry(original, b'ACTION  C')
    assert origin == 0x6000 and action[ACTION_START - 1] == 0xC9
    archived = source[ARCHIVE_START:ARCHIVE_END]
    embedded = action[ACTION_START:ACTION_END]
    assert len(archived) == 3706 and len(embedded) == 3729
    preceding = 'ВЕРОЯТНОСТЬ ПОЯВЛ'.encode('cp866')
    assert source[ARCHIVE_START - len(preceding):ARCHIVE_START] == preceding
    assert source[ARCHIVE_END:ARCHIVE_END + 3] == 'ЛИ '.encode('cp866')
    revision = reproduce_revision(archived, embedded)
    machine_data = compare_machine_data(disk, archived, embedded, action)
    report = dict(passed=True, archive_sha256=archive_hash, archive_file='awk1.trd:3DTABS.a',
                  archive_range=[ARCHIVE_START, ARCHIVE_END], action_range=[ACTION_START, ACTION_END],
                  exact_reconstruction_bytes=len(embedded), revision=revision, machine_data=machine_data,
                  data_is_tokenized_author_source=True, placement_cause_proved=False,
                  live_consumer_proved=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionEmbeddedSourceRevisionVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Сверены 3729 байтов встроенной редакции и машинные данные обеих версий.')


if __name__ == '__main__':
    main()

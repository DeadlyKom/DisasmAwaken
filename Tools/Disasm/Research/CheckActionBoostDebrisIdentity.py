"""Авторское T_TRASH, текущая модель TRASH и вызывающий хвост форсажа.

Документация: ../../../Docs/ActionClass20Spawn.md
Документация: ../../../Docs/ActionBoostAdvance.md
"""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


def main():
    assert sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256
    with ZipFile(ARCHIVE) as archive:
        old_disk = archive.read('awk1.trd')
    _, definitions, _ = read_entry(old_disk, b'EQUS    a')
    definition = next(line for line in definitions.split(b'\r') if line.startswith(b'T_TRASH'))
    match = re.fullmatch(rb'T_TRASH\x06[\x80-\x8f]\x05f\x06\x82#14\xfe(.+)', definition)
    assert match and match[1].decode('cp866') == 'МУСОР ДЛЯ ФОРСАЖА'
    _, labels, _ = read_entry(old_disk, b'LABELS  a')
    assert b'TRASH\x06\x8a\x04f55482' in labels.split(b'\r')
    _, source, _ = read_entry(old_disk, b'OBJECTS2a')
    lines = source.split(b'\r')
    begin = lines.index(b'TRASH:')
    packet = bytearray()
    for line in lines[begin+1:begin+9]:
        row = re.fullmatch(rb'\x06\x8a\x05g(#[A-F0-9]{2}(?:,#[A-F0-9]{2})*)', line)
        assert row, line.hex()
        packet.extend(int(value[1:], 16) for value in row[1].split(b','))
    assert len(packet) == 24
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(disk).hexdigest() == manifest['sha256']
    _, current_objects, _ = read_entry(disk, b'OBJECT3DC')
    _, archived_objects, _ = read_entry(old_disk, b'OBJECT3DC')
    assert current_objects == archived_objects and len(current_objects) == 10580
    assert current_objects[0x18BA:0x18D2] == bytes(packet)
    _, action, _ = read_entry(disk, b'ACTION  C')
    assert action[0x3EC0:0x3EC2] == bytes.fromhex('BAD8')
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    code = next(region['instructions'] for region in flow if region['name'] == 'Action')
    # Проверка двух полей создателя и настоящего условного CALL из AdvanceBoost.
    checks = ((0x617D, 0x6201, 'FD3606C0'), (0x617D, 0x6201, 'FD361214'),
              (0x7504, 0x754C, 'DC7D61'))
    records = []
    for start, end, expected in checks:
        found = [row for row in code if start <= row['address'] < end
                 and row['hex'].upper() == expected]
        assert len(found) == 1, (expected, found)
        row = found[0]
        assert row['slot'] == 17
        assert action[row['offset']:row['offset']+len(bytes.fromhex(expected))] == bytes.fromhex(expected)
        records.append(dict(address=row['address'], file_offset=row['offset'], hex=expected,
                            operation=row['operation']))
    result = dict(passed=True, method='author_class_comment_model_packet_and_current_boost_call',
        archive_sha256=ARCHIVE_SHA256, original_disk_sha256=manifest['sha256'],
        author_definition='awk1.trd:EQUS.a', original_definition_hex=definition.hex(),
        class_code=20, class_code_hex='14', author_name='T_TRASH', author_comment=match[1].decode('cp866'),
        author_model_source='awk1.trd:OBJECTS2.a', model_label='TRASH', model_address=0xD8BA,
        matched_model_bytes=24, full_object3d_file_match_bytes=10580,
        current_model_offset=0xC0, model_pointer_address=0x9EC0,
        current_instruction_witnesses=records, current_AdvanceBoost_caller_proved=True,
        author_boost_debris_role_and_current_use_linked=True,
        native_visual_appearance_proved=False, full_class_behavior_proved=False,
        assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionBoostDebrisIdentityVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

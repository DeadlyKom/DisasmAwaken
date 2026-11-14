"""Связь авторского T_ROKET, модели ROKET и общего создателя ракеты.

Документация: ../../../Docs/ActionClass17Spawn.md
"""
from hashlib import sha256
import json
from zipfile import ZipFile

from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from ControlsObjectGlyphData import verify_archived_roles


def main():
    # Проверка определения типа и совпадения архивных ресурсов с текущим CONTROL.
    archived = verify_archived_roles()
    definition = archived['type_definitions']['T_ROKET']
    assert definition['value'] == 0x11 and definition['comment'] == 'РАКЕТА'
    role = next(row for row in archived['roles'] if row['class_code'] == 0x11)
    assert role['archived_label'] == 'MROKET'
    assert sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256
    with ZipFile(ARCHIVE) as archive:
        old_disk = archive.read('awk1.trd')
    _, labels, _ = read_entry(old_disk, b'LABELS  a')
    declaration = b'ROKET\x06\x8a\x04f55396'
    assert declaration in labels.split(b'\r') and 55396 == 0xD864
    # Проверка всего файла моделей, одного имени в другой версии недостаточно.
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(disk).hexdigest() == manifest['sha256']
    _, objects, _ = read_entry(disk, b'OBJECT3DC')
    _, old_objects, _ = read_entry(old_disk, b'OBJECT3DC')
    assert objects == old_objects and len(objects) == 10580
    _, action, _ = read_entry(disk, b'ACTION  C')
    assert action[0x3E90:0x3E92] == bytes.fromhex('64D8')
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    code = {row['address']: row for region in flow if region['name'] == 'Action'
            for row in region['instructions']}
    # Проверка модели, класса, происхождения и обеих форм передачи общему создателю.
    expected = {0x6106:'FD360690', 0x6127:'FD361211', 0x6124:'FD7711',
                0x60D7:'3E01', 0x60D9:'08', 0x60E6:'061A',
                0xF26C:'08', 0xF26D:'AF', 0xF26E:'08', 0xF27D:'C3E860'}
    witnesses = []
    for address, encoded in expected.items():
        row = code[address]
        raw = bytes.fromhex(encoded)
        assert row['slot'] == 17 and row['hex'].upper() == encoded
        assert action[row['offset']:row['offset']+len(raw)] == raw
        witnesses.append(dict(address=address, offset=row['offset'], hex=encoded,
                              operation=row['operation']))
    assert code[0x60E6]['address'] + len(bytes.fromhex(code[0x60E6]['hex'])) == 0x60E8
    result = dict(passed=True, method='author_class_current_model_and_both_creation_paths',
        archive_sha256=ARCHIVE_SHA256, original_disk_sha256=manifest['sha256'],
        author_name='T_ROKET', class_code=0x11, author_comment=definition['comment'],
        original_definition_hex=definition['raw_hex'], corresponding_icon=role,
        model_label='ROKET', model_address=0xD864, model_offset=0x90,
        model_pointer_address=0x9E90, archived_model_label_hex=declaration.hex(),
        full_object3d_file_match_bytes=len(objects), current_instruction_witnesses=witnesses,
        player_fallthrough_and_character_tail_jump_proved=True,
        full_missile_behavior_proved=False, native_visual_appearance_proved=False,
        assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileIdentityVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('T_ROKET=#11, ROKET=#D864, указатель #9E90 и оба пути создания сверены с оригиналом.')


if __name__ == '__main__':
    main()

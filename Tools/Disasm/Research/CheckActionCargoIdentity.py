"""Авторский T_CARGO, модель CRG1 и подготовленный вход команды выброса мины.

Документация: ../../../Docs/ActionClass19Spawn.md
Документация: ../../../Docs/ActionEjectCommands.md
"""
from hashlib import sha256
import json
from zipfile import ZipFile

from ArchivedSourceInventory import ARCHIVE,ARCHIVE_SHA256
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from ControlsObjectGlyphData import verify_archived_roles


def main():
    # Проверка авторского типа и совпадения всех архивных значков с текущим CONTROL.
    archived = verify_archived_roles()
    definition = archived['type_definitions']['T_CARGO']
    assert definition['value'] == 0x13 and definition['comment'] == 'ГРУЗ'
    role = next(row for row in archived['roles'] if row['class_code'] == 0x13)
    assert role['archived_label'] == 'MCARGO'
    assert sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256
    with ZipFile(ARCHIVE) as archive:
        old_disk = archive.read('awk1.trd')
    _,labels,_ = read_entry(old_disk,b'LABELS  a')
    declaration = b'CRG1\x06\x8b\x04f55506'
    assert declaration in labels.split(b'\r') and 55506 == 0xD8D2
    # Проверка всего файла моделей и текущего указателя, одного имени в другом выпуске недостаточно.
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(disk).hexdigest() == manifest['sha256']
    _,objects,_ = read_entry(disk,b'OBJECT3DC')
    _,old_objects,_ = read_entry(old_disk,b'OBJECT3DC')
    assert objects == old_objects and len(objects) == 10580
    _,action,_ = read_entry(disk,b'ACTION  C')
    assert action[0x3E98:0x3E9A] == bytes.fromhex('D2D8')
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    code = {row['address']:row for area in flow if area['name'] == 'Action' for row in area['instructions']}
    expected = {0x6472:'FD360698',0x64A9:'FD361213',0x75F1:'CD4164',
                0x75F4:'D5',0x75F5:'1102F4',0x75F8:'CD4060',0x75FB:'D1',0x75FC:'C9'}
    witnesses = []
    for address,encoded in expected.items():
        row = code[address]
        raw = bytes.fromhex(encoded)
        assert row['slot'] == 17 and row['hex'].upper() == encoded
        assert action[row['offset']:row['offset']+len(raw)] == raw
        witnesses.append(dict(address=address,offset=row['offset'],hex=encoded,operation=row['operation']))
    # Проверка собственного хвоста команды, между создателем и возвратом нет изменения типа или модели.
    tail = [code[pc]['operation'] for pc in (0x75F4,0x75F5,0x75F8,0x75FB,0x75FC)]
    assert tail == ['PUSH DE','LD DE,#F402','CALL #6040','POP DE','RET']
    reports = ROOT/'Tools/Disasm/Reports'
    for name in ('ActionClass19SpawnVerification.json','ActionEjectCommandsVerification.json'):
        assert json.loads((reports/name).read_bytes())['passed']
    result = dict(passed=True,method='author_cargo_type_current_model_and_eject_mine_prepared_call',
        archive_sha256=ARCHIVE_SHA256,original_disk_sha256=manifest['sha256'],
        author_name='T_CARGO',class_code=0x13,author_comment=definition['comment'],
        original_definition_hex=definition['raw_hex'],corresponding_icon=role,
        model_label='CRG1',model_address=0xD8D2,model_offset=0x98,
        model_pointer_address=0x9E98,archived_model_label_hex=declaration.hex(),
        full_object3d_file_match_bytes=len(objects),current_instruction_witnesses=witnesses,
        prepared_entry=0x6441,eject_mine_calls_same_creator=True,
        own_eject_mine_tail_does_not_retype_record=True,
        created_class_and_model_are_distinct_from_command_message_identity=True,
        full_created_object_lifecycle_proved=False,native_mine_behavior_proved=False,
        assembly_executed=False,native_execution=False)
    (reports/'ActionCargoIdentityVerification.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('T_CARGO=#13, CRG1=#D8D2 и вызов SpawnPrepared из команды мины подтверждены, дальнейшее поведение не утверждается.')


if __name__ == '__main__':
    main()

"""Авторский T_STATION и две текущие проверки класса в хвосте освобождения.

Документация: ../../../Docs/ActionClassReuse.md
"""
from hashlib import sha256
import json

from CheckIntro import ROOT
from ControlsObjectGlyphData import verify_archived_roles


def main():
    # Повторная сверка EQUS, MOTAB и всех физических байтов ресурсов CONTROL.
    archived = verify_archived_roles()
    definition = archived['type_definitions']['T_STATION']
    assert definition['value'] == 0x12 and definition['comment'] == 'ЧАСТЬ СТАНЦИИ'
    role = next(row for row in archived['roles'] if row['class_code'] == 0x12)
    assert role['archived_label'] == 'MSTATION'
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    item = next(row for row in manifest['entries'] if row['slot'] == 17)
    source = (ROOT/(item['path']+'.bin')).read_bytes()
    assert source == disk[item['offset']:item['offset']+item['length']]
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    code = next(region['instructions'] for region in flow if region['name'] == 'Action')
    # Проверка чтения ClassCode по IX, затем сравнения выбранных итератором записей по IY.
    expected = {0xE65F:'DD7E12', 0xE662:'FE12', 0xE678:'FD7E12', 0xE67B:'FE12'}
    witnesses = []
    for address, raw in expected.items():
        row = next(row for row in code if row['address'] == address)
        assert row['hex'].upper() == raw and row['slot'] == 17
        assert source[row['offset']:row['offset']+len(bytes.fromhex(raw))] == bytes.fromhex(raw)
        witnesses.append(dict(address=address, file_offset=row['offset'], hex=raw, operation=row['operation']))
    result = dict(passed=True, method='author_class_definition_icon_and_current_release_class_checks',
        archive_sha256=archived['archive_sha256'], original_disk_sha256=manifest['sha256'],
        author_name='T_STATION', class_code=0x12, class_code_hex='12',
        author_comment=definition['comment'], original_definition_hex=definition['raw_hex'],
        corresponding_icon_role=role, archived_control_bytes_matched=archived['matched_bytes'],
        current_instruction_witnesses=witnesses, station_part_class_role_linked=True,
        alternate_nonstation_restore_path_preserved=True, full_station_behavior_proved=False,
        native_visual_appearance_proved=False, assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionStationPartIdentityVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

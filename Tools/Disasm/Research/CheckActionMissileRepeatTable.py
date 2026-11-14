"""Авторский JTYPE и исходные значения повторного пуска ракет."""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from CheckActionParameterActivation import flat_action
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


def main():
    path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(path) as archive:
        _, source, _ = read_entry(archive.read('awk1.trd'), b'BRAINPROa')
        _, equs, _ = read_entry(archive.read('awk1.trd'), b'EQUS    a')
        sp_origin, sp, _ = read_entry(archive.read('awk5.trd'), b'SP      C')
    rows = source.split(b'\r')
    start = rows.index(b'JTYPE')
    caption = ['СЧЕТЧИК ПОВТОРНОГО ПУСКА РАКЕТ ДЛЯ', 'КАЖДОГО ПЕРСОНАЖА']
    assert rows[start + 1:start + 3] == [line.encode('cp866') for line in caption]
    values, class_notes = [], []
    for row in rows[start + 3:start + 12]:
        match = re.match(rb'\x06\x8c\x05g\x06\x83(\d+)', row)
        assert match and b'\xfe' in row
        values.append(int(match[1]))
        class_notes.append(row.split(b'\xfe', 1)[1].decode('cp866'))
    assert values == [20, 0, 18, 30, 0, 30, 35, 10, 40]
    equs_rows = equs.split(b'\r')
    declaration = b'RCO\x06\x89\x05f\x06\x8220'
    index = equs_rows.index(declaration)
    assert equs_rows[index - 1] == 'СЧЕТЧИК ДЛЯ ПОВТОРНОГО ПУСКА РАКЕТ'.encode('cp866')
    current = flat_action()
    table = bytes(values)
    assert bytes(current[0xF280:0xF289]) == table
    assert sp.count(table) == 1 and sp.index(table) == 0x9289
    reports = ROOT / 'Tools/Disasm/Reports'
    action = next(region for region in json.loads((reports / 'ControlFlow.json').read_bytes())
                  if region['name'] == 'Action')
    code = {row['address']: row for row in action['instructions']}
    reload = {0xF244:'LD HL,#F280', 0xF247:'ADD HL,BC',
              0xF248:'LD A,(HL)', 0xF249:'LD (IX+#14),A'}
    operations = []
    for address, expected in reload.items():
        row = code[address]
        assert row['operation'] == expected
        encoded = bytes.fromhex(row['hex'])
        assert bytes(current[address:address + len(encoded)]) == encoded
        operations.append(dict(address=address, operation=expected, hex=row['hex']))
    for name in ('ActionSpawnWindowVerification', 'ActionLinkedTargetStateVerification'):
        assert json.loads((reports / (name + '.json')).read_bytes())['passed']
    report = dict(passed=True, archive_sha256=digest, source='awk1.trd:BRAINPRO.a:JTYPE',
                  caption_cp866_hex=[line.encode('cp866').hex() for line in caption],
                  class_notes=class_notes, values=values, matched_bytes=len(table),
                  current_address=0xF280, archived_sp_file_offset=0x9289,
                  archived_sp_address=sp_origin + 0x9289, rco_record_offset=20,
                  current_field='FActionRecord.MissileRepeatDelay', current_reload_operations=operations,
                  reload_occurs_after_failed_allocation_too=True,
                  counter_unit='eligible_counter_updates_in_state02',
                  constant_frame_or_seconds_duration_proved=False,
                  all_other_state_meanings_proved=False, assembly_executed=False, native_execution=False)
    (reports / 'ActionMissileRepeatTableVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('JTYPE: подтверждены девять исходных счётчиков повторного пуска и поле RCO=#14.')


if __name__ == '__main__':
    main()

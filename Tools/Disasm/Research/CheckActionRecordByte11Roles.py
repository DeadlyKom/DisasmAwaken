"""Реестр подтверждённых обращений к байту #11 объектной записи ACTION."""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from CheckStationFlightCycle import ROOT, payload
from CheckControlsArchivedHyperEffect import read_entry
from CheckActionArchivedPlayerPanel import compare_player


ROLES = {
    0x6124: 'входной параметр уведомления ребёнка в состоянии 08',
    0x64A6: 'количество пополнения для подбираемой записи класса 13',
    0x790F: 'нулевой параметр шаблонной записи класса 12',
    0x7A61: 'полный параметр SpawnField11 из текущего набора',
    0x7DE5: 'полный параметр SpawnField11 из изменяемого операнда',
    0x7E55: 'запись 6E после несовместимых проверок класса 06 и 07',
    0xE8EA: 'начальный байт 28 для дочерней записи класса 09, при State02 порог младшего байта потока 0',
    0xF212: 'беззнаковый порог младшего байта случайного слова в состоянии 02',
    0xF3E4: 'беззнаковый порог младшего байта случайного слова в состоянии 10',
    0xF45E: 'начальный порог 46 младшего байта потока 0 для дочерней записи класса 03 в State02',
    0xF59F: 'разрешение уведомления при потерянной цели в состоянии 08',
    0xF630: 'разрешение уведомления при достижении цели в состоянии 08',
    0xF66A: 'уменьшаемый по модулю 256 таймер состояния 07',
    0xF724: 'начальное время 12 после перевода в состояние 07',
}


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    flow_bytes = (reports / 'ControlFlow.json').read_bytes()
    action = next(region for region in json.loads(flow_bytes) if region['name'] == 'Action')
    functions = [row for row in json.loads((reports / 'Functions.json').read_bytes()) if row['region'] == 'Action']
    indexed = [row for row in action['instructions'] if re.search(r'\((?:IX|IY)\s*\+\s*#11\)', row['operation'])]
    assert {row['address'] for row in indexed} == set(ROLES) | {0x6DF4}
    rows = []
    for row in indexed:
        function = next(item for item in functions if item['slot'] == row['slot']
                        and item['offset'] <= row['offset'] < item['end_offset'])
        source = (ROOT / function['path']).read_text(encoding='utf-8')
        if row['address'] == 0x6DF4:
            assert row['operation'] == 'LD H,(IX+#11)' and 'FVisualEffect.FrameHeight' in source
            continue
        assert 'FActionRecord.Unknown11' in source
        rows.append(dict(pc=row['address'], operation=row['operation'], path=function['path'],
                         role=ROLES[row['address']]))

    symbols = json.loads((reports / 'Symbols.json').read_bytes())
    indirect = symbols['Action.RequestAimOrCollectTarget.ReadPayload']
    code = {row['address']: row for row in action['instructions']}
    prefix = b''.join(bytes.fromhex(code[indirect + offset]['hex']) for offset in (0, 1, 3, 4, 5, 7, 8))
    assert prefix == bytes.fromhex('7D C6 11 6F 5E C6 EE 6F 7E')
    assert 0x12 + 0x11 + 0xEE == 0x111
    # Границы проверок берём из самого потока, между CP нет изменения A.
    before_write = [row for row in action['instructions'] if 0x7E40 <= row['address'] < 0x7E55]
    comparisons = [row['operation'] for row in before_write if row['operation'].startswith('CP ')]
    assert comparisons == ['CP #06', 'CP #07']
    assert sum(row['operation'].startswith('JR NZ,') for row in before_write) == 2
    start = next(index for index, row in enumerate(before_write) if row['operation'] == 'CP #06')
    tests = [row['operation'] for row in before_write[start:start + 4]]
    assert tests[0] == 'CP #06' and tests[2] == 'CP #07'
    assert tests[1] == tests[3] and tests[1].startswith('JR NZ,')
    # Сопоставление архивного LZS с параметром происхождения текущей ракеты.
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    archive_hash = sha256(archive_path.read_bytes()).hexdigest()
    assert archive_hash == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        _, equs, _ = read_entry(archive.read('awk1.trd'), b'EQUS    a')
    source_lines = equs.split(b'\r')
    assert b'LZS\x06\x89\x05f\x06\x8217' in source_lines
    owner_note = 'П LZS'.encode('cp866') + b'\x06\x820 ' + 'РАКЕТА ПЕРСОНАЖА <>0 ИГРОКА'.encode('cp866')
    assert owner_note in source_lines
    shooter_note = 'П RAND КТО ПУСТИЛ РАКЕТУ'.encode('cp866')
    target_note = 'П MSPD НА КОГО НАПРАВЛЕНА РАКЕТА'.encode('cp866')
    assert shooter_note in source_lines and target_note in source_lines
    player = compare_player(archive_path)
    assert player['authored_bytes'] == 21 and player['current_player'] == 0xA780
    assert 0xA100 + 64 * 0x1A == player['current_player']
    expected = {0x60D7: ('LD A,#01', '3e01'), 0x60D9: ("EX AF,AF'", '08'),
                0xF26C: ("EX AF,AF'", '08'), 0xF26D: ('XOR A', 'af'),
                0xF26E: ("EX AF,AF'", '08'), 0xF27D: ('JP #60E8', 'c3e860'),
                0x6124: ('LD (IY+#11),A', 'fd7711'),
                0x60E6: ('LD B,#1A', '061a'),
                0x611D: ('LD (IY+#0D),B', 'fd700d'),
                0x6120: ('LD (IY+#0F),C', 'fd710f')}
    original = payload(17)
    ownership_operations = []
    for address, (operation, encoded) in expected.items():
        row = code[address]
        assert row['slot'] == 17 and row['operation'] == operation and row['hex'] == encoded
        assert original[row['offset']:row['offset'] + len(bytes.fromhex(encoded))] == bytes.fromhex(encoded)
        ownership_operations.append(dict(address=address, operation=operation, hex=encoded))
    report = dict(passed=True, control_flow_sha256=sha256(flow_bytes).hexdigest(),
                  indexed_object_accesses=rows, excluded_visual_effect_access=0x6DF4,
                  indirect_pickup_reader=indirect + 8, indexed_contexts_audited=True,
                  archived_lzs_ownership=dict(archive_sha256=archive_hash,
                      source='awk1.trd:EQUS.a', field_offset=17, note_cp866_hex=owner_note.hex(),
                      player_initializer_value=1, character_initializer_value=0,
                      shooter_note_cp866_hex=shooter_note.hex(), target_note_cp866_hex=target_note.hex(),
                      player_shooter_index=0x1A, player_address=player['current_player'],
                      matched_archived_player_bytes=player['authored_bytes'],
                      current_original_operations=ownership_operations,
                      ownership_does_not_replace_other_state_and_class_roles=True),
                  original_function_models_used=[
                      'ActionTimedDecayStateVerification.json', 'ActionLinkedTargetStateVerification.json',
                      'ActionTimedLinkedStateVerification.json', 'ActionTractorCollectVerification.json',
                      'ActionSpawnedClass3ThresholdVerification.json',
                      'ActionChildInitialByte11Verification.json'],
                  whole_program_indirect_accesses_excluded=False, assembly_executed=False)
    for name in report['original_function_models_used']:
        assert json.loads((reports / name).read_bytes())['passed']
    (reports / 'ActionRecordByte11RolesVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Сверены 14 индексированных обращений объекта, косвенный подбор и отдельная запись визуального эффекта.')


if __name__ == '__main__':
    main()

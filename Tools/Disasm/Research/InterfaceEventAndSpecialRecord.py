"""Два станционных кода событий и физический префикс особой родительской записи ACTION."""
import json
from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records


EVENT_FIELDS = (
    ('InterfaceCode', 1, 'код интерфейсного события, используется при передаче действия и выборе меню'),
    ('ScriptCode', 1, 'код события для LANG, ReadEventCode переносит его в стек выражений'),
)
SPECIAL_FIELDS = (
    ('Component0', 2, 'первое слово родителя для SpawnPrepared, UpdateFrame очищает старший байт'),
    ('Component1', 2, 'второе слово родителя, его старший байт совпадает с позицией до списка эффектов'),
    ('Component2', 2, 'третье слово родителя для SpawnPrepared'),
    ('ModelOffset', 1, 'байтовое смещение модели игрока, PrepareLargeEffect читает заголовок OBJECT3D'),
    ('OffsetPhase0', 1, 'первый фазовый байт, копируется из родителя в создаваемую запись'),
    ('OffsetPhase1', 1, 'второй фазовый байт, копируется из родителя в создаваемую запись'),
    ('OffsetPhase2', 1, 'третий фазовый байт, копируется из родителя в создаваемую запись'),
    ('PlayerMarker', 1, 'маркер игрока FF, на ближнем пути State08 запрещает освобождение текущей ракеты'),
    ('LinkedIndex', 1, 'индекс связанной записи, при создании ракеты с целью 1A получает её индекс'),
)
TABLES = (
    (4, 0x6000, ('StationEventCodes', 'Source/Station/Data/EventCodes.asm',
                 0x3839, 0x383B, 'FStationEventCodes', EVENT_FIELDS, ('Value',))),
    (17, 0x6000, ('ActionSpecialRecord', 'Source/Action/Data/SpecialRecordPrefix.asm',
                  0x4780, 0x478C, 'FSpecialRecordPrefix', SPECIAL_FIELDS, ('Value',))),
)
BINDINGS = (
    ('InterfaceState', 'EventCode', 0x9839, 'StationEventCodes.Value.InterfaceCode'),
    ('ScriptCallState', 'EventCode', 0x983A, 'StationEventCodes.Value.ScriptCode'),
)
REQUIRED_REPORTS = ('EventDispatchVerification', 'TradePanelEventVerification', 'ActionEjectCommandsVerification',
                    'ActionBankedCallbackVerification', 'ActionVisualEffectTransferVerification',
                    'ActionPlayerEffectFieldsVerification')
DOCUMENT = 'InterfaceEventAndSpecialRecord'
TAG = DOCUMENT


def name_operands(region, address, operation):
    if region != 'Action':
        return operation
    if address == 0xA85E:
        return operation.replace('(#A781)', '(@ActionSpecialRecord.Value.Component0 + 1)')
    if address in (0x7859, 0x7B58) and operation == 'LD HL, #EC00':
        return 'LD HL, @Voxel.CreateSmallEffect.Entry'
    return operation


def validate_sources(sources):
    station = sources[4]
    action = sources[17]
    assert station[0x3839:0x383B] == bytes(2)
    assert station[0x3E06:0x3E09] == station[0x3E4E:0x3E51] == bytes.fromhex('32 39 98')
    assert action[0x4780:0x478C] == bytes(10) + bytes.fromhex('ff 00')
    assert action[0x48CC:0x48CF] == bytes.fromhex('32 81 a7')
    assert action[0x0F34:0x0F38] == bytes.fromhex('fd 21 83 a7')
    assert action[0x4795:0x4797] == bytes(2)
    assert action[0x8A37:0x8A3A] == bytes.fromhex('DD 7E 06')
    effect = json.loads((ROOT / 'Tools/Disasm/Reports/ActionPlayerEffectFieldsVerification.json').read_bytes())
    assert effect['passed'] and effect['cases'] == 512 and effect['model_offset_address'] == 0xA786
    return dict(station_event_code_bytes=2, special_record_prefix_bytes=12,
                banked_effect_scan_anchor=0xA783, first_effect_address=0xA795,
                special_record_prefix_starts_after_initial_marker=True,
                full_special_record_layout_proved=False,
                special_player_model_offset_reader=0xEA37, player_target_effect_profiles=512)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические поля и потребители](../../../Docs/' + DOCUMENT + '.md)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    lines = []
    for name, fields in (('FStationEventCodes', EVENT_FIELDS), ('FSpecialRecordPrefix', SPECIAL_FIELDS)):
        lines.append('                struct ' + name)
        offset = 0
        assertions = []
        for field, width, note in fields:
            declaration = 'db #00' if width == 1 else 'dw #0000'
            lines.append((field.ljust(16) + declaration).ljust(80) + '; ' + note)
            assertions.append(f'                assert {name}.{field} == {offset}')
            offset += width
        lines.extend(('                ends', f'                assert {name} == {offset}', *assertions, ''))
    return '\n'.join(lines) + '\n'

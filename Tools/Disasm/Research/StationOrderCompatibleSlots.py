"""Совпадающие по байтам записи ORDER в переносимом состоянии станции."""
from ActionNewsOrdersAndJumpCost import ORDER_FIELDS as ACTION_FIELDS
from PreviewSceneTables import parse as parse_records, render as render_records
from SavedStateLayout import SLOTS


DOCUMENT = 'StationOrderCompatibleSlots'
TAG = DOCUMENT
REQUIRED_REPORTS = ('StationHyperJumpCostTransferVerification',)
BINDINGS = ()
LABELS = ('Slot0', 'Slot1', 'Slot2')
ORDER_FIELDS = (('Marker', 1, 'исходный первый байт записи, условие использования неизвестно'),) + ACTION_FIELDS[1:]
TABLES = ((4, 0x6000, (
    'StationOrderSlots', 'Source/Station/Data/OrderCompatibleSlots.asm',
    0x38C6, 0x38F6, 'FActionOrderRecord', ORDER_FIELDS, LABELS,
)),) + tuple(
    (slot, 0, (name.title() + 'OrderSlots', f'Source/Resources/{slot:02d}_{name}/OrderCompatibleSlots.asm',
               0x8B, 0xBB, 'FActionOrderRecord', ORDER_FIELDS, LABELS))
    for slot, name in SLOTS
)


def validate_sources(sources):
    station, action = sources[4], sources[17]
    assert 0x38C6 - 0x383B == 0x3C48 - 0x3BBD == 0x8B
    expected = (bytes([255]) + bytes(15)) * 3
    assert station[0x38C6:0x38F6] == action[0x3C48:0x3C78] == expected
    assert station[0x38F6:0x3906] != action[0x3C78:0x3C88]
    for slot, name in SLOTS:
        assert sources[slot][0x8B:0xBB] == (bytes(48) if name == 'SAVE5' else expected)
    return dict(matching_action_records=3, station_bytes=48, save_files=6,
                fourth_record_aliases_secondary_quantities=True, actual_order_consumer_proved=False)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[совпадающие записи переноса](../../../Docs/StationOrderCompatibleSlots.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    return ''

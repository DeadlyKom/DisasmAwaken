"""Пятибайтовые записи транспорта и начальные количества второго оснащения."""
from PreviewSceneTables import parse as parse_records, render as render_records
from SavedStateLayout import SLOTS


DOCUMENT = 'StationTransportTradeTables'
TAG = DOCUMENT
REQUIRED_REPORTS = ('OriginalShipTradeVerification', 'StrideFiveVerification',
                    'WeightedLoadVerification', 'SecondaryEquipmentRowsVerification')
PRIMARY = (
    ('Capacity', 1, 'поле K.t, переносится в вместимость при покупке'),
    ('Price', 2, 'цена K.c, младший байт первым'),
    ('Unknown03', 1, 'назначение отдельного байта пока не установлено'),
    ('SaleField', 1, 'поле k.s, нуль выбирает особую ветвь продажи'),
)
SECOND = (
    ('Unknown00', 1, 'назначение отдельного байта пока не установлено'),
    ('PriceField', 2, 'слово свойства c второго набора, сценарий покупки отсутствует'),
    ('Unknown03', 1, 'назначение отдельного байта пока не установлено'),
    ('LoadAddend', 1, 'свойство v и добавка в ComputeWeightedLoad'),
)
QUANTITY = (('Code', 1, 'исходное кодированное количество второго списка'),)
ROWS = tuple(f'Item{index:02X}' for index in range(14))
TABLES = (
    (4, 0x6000, ('StationShipTradeRows', 'Source/Station/Data/ShipTradeRows.asm',
                 0x3802, 0x3825, 'FStationShipTradeRow', PRIMARY,
                 tuple(f'Ship{index}' for index in range(7)))),
    (4, 0x6000, ('StationSkimmerTradeRows', 'Source/Station/Data/SkimmerTradeRows.asm',
                 0x3825, 0x3839, 'FStationSkimmerTradeRow', SECOND,
                 tuple(f'Skimmer{index}' for index in range(4)))),
    (4, 0x6000, ('StationSecondaryQuantities', 'Source/Station/Data/SecondaryQuantities.asm',
                 0x38F6, 0x3904, 'FEquipmentQuantityCode', QUANTITY, ROWS)),
) + tuple(
    (slot, 0, (name.title() + 'SecondaryQuantities',
               f'Source/Resources/{slot:02d}_{name}/SecondaryQuantities.asm',
               0xBB, 0xC9, 'FEquipmentQuantityCode', QUANTITY, ROWS))
    for slot, name in SLOTS
)
BINDINGS = (('SecondaryEquipmentData', 'Quantities', 0x98F6, 'StationSecondaryQuantities.Item00.Code'),)


def validate_sources(sources):
    data = sources[4]
    assert 0x3802 + 7 * 5 == 0x3825 and 0x3825 + 4 * 5 == 0x3839
    assert data[0x3802:0x3807] == bytes.fromhex('64 00 FA 82 01')
    assert data[0x3825:0x382A] == bytes.fromhex('00 30 75 AA 05')
    assert data[0x38F6:0x3904] == bytes([255]) * 14
    for slot, name in SLOTS:
        assert sources[slot][0xBB:0xC9] == bytes([0 if name == 'SAVE5' else 255]) * 14
    return dict(ship_rows=7, skimmer_rows=4, secondary_quantity_rows=14, save_files=6,
                all_transport_fields_proved=False)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические записи транспорта и количества](../../../Docs/StationTransportTradeTables.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    lines = []
    for name, fields in (('FStationShipTradeRow', PRIMARY), ('FStationSkimmerTradeRow', SECOND)):
        lines.append('                struct ' + name)
        offsets = []
        offset = 0
        for field, width, note in fields:
            lines.append((field.ljust(16) + ('db #00' if width == 1 else 'dw #0000')).ljust(80) + '; ' + note)
            offsets.append(f'                assert {name}.{field} == {offset}')
            offset += width
        lines.extend(('                ends', f'                assert {name} == {offset}', *offsets, ''))
    return '\n'.join(lines)

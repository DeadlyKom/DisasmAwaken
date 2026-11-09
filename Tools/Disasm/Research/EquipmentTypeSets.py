"""Четыре кода типа на строку в основном и дополнительном списках оснащения."""
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'EquipmentPhysicalTables'
TAG = 'EquipmentTypeSets'
REQUIRED_REPORTS = ('EquipmentRowsVerification', 'SecondaryEquipmentRowsVerification')
FIELDS = tuple((f'Type{index}', 1, 'код для сравнения с текущим типом транспорта')
               for index in range(4))
TABLES = tuple(
    (4, 0x6000, (name, f'Source/Station/Data/{name}.asm', start, end, 'FEquipmentTypeSet',
                  FIELDS, tuple(f'Row{index:02X}' for index in range((end - start) // 4))))
    for name, start, end in (('EquipmentShipTypeSets', 0x3400, 0x3484),
                             ('EquipmentSkimmerTypeSets', 0x3484, 0x34BC))
)
BINDINGS = (('EquipmentListData', 'ShipSets', 0x9400, 'EquipmentShipTypeSets.Row00.Type0'),)


def validate_sources(sources):
    data = sources[4][0x3400:0x34BC]
    assert len(data) == 188 and set(data) == {1, 2, 3, 4, 5, 6, 255}
    return dict(ship_rows=33, skimmer_rows=14, type_codes_per_row=4)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические таблицы оснащения](../../../Docs/EquipmentPhysicalTables.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    name = 'FEquipmentTypeSet'
    lines = ['                struct ' + name]
    lines.extend((field.ljust(16) + 'db #FF').ljust(80) + '; ' + note for field, _, note in FIELDS)
    lines.extend(('                ends', f'                assert {name} == 4'))
    lines.extend(f'                assert {name}.{field} == {offset}'
                 for offset, (field, _, _) in enumerate(FIELDS))
    return '\n'.join(lines) + '\n'

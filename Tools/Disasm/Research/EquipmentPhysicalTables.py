"""Физические записи между рынком и клавиатурной таблицей станции."""
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'EquipmentPhysicalTables'
TAG = DOCUMENT
REQUIRED_REPORTS = ('EquipmentPhysicalTablesVerification', 'EquipmentRowsVerification')
PRICES = (('Price', 2, 'слово для колонки «Цена» и стекового запроса LANG'),)
WEIGHTS = (
    ('Threshold', 1, 'нижний допустимый признак L для вывода веса и прямой проверки'),
    ('Weight', 1, 'выводимый вес и множитель взвешенной суммы'),
)
SECOND_WEIGHTS = (
    ('Threshold', 1, 'нижний допустимый признак L в прямой проверке второго набора'),
    ('Factor', 1, 'множитель третьего слагаемого и байт запроса Property071'),
)
BOUNDS = (
    ('Left', 1, 'число шагов влево кодируется отрицанием по модулю 256'),
    ('Right', 1, 'число шагов вправо без преобразования'),
)


def table(module, start, end, structure, fields):
    return (4, 0x6000, (
        module, f'Source/Station/Data/{module}.asm', start, end, structure, fields,
        tuple(f'Row{index:02X}' for index in range((end - start) // 2)),
    ))


TABLES = (
    table('EquipmentPrices', 0x3592, 0x35D4, 'FEquipmentPrice', PRICES),
    table('SecondEquipmentPrices', 0x35D4, 0x35F0, 'FEquipmentPrice', PRICES),
    table('EquipmentWeights', 0x35F0, 0x3632, 'FEquipmentWeight', WEIGHTS),
    table('SecondWeightFactors', 0x3632, 0x364E, 'FSecondWeightFactor', SECOND_WEIGHTS),
    table('EquipmentNeighborBounds', 0x364E, 0x3690, 'FNeighborBounds', BOUNDS),
    table('SecondNeighborBounds', 0x3690, 0x36AA, 'FNeighborBounds', BOUNDS),
)
BINDINGS = (
    ('EquipmentListData', 'Prices', 0x9592, 'EquipmentPrices.Row00.Price'),
    ('EquipmentListData', 'Weights', 0x95F0, 'EquipmentWeights.Row00.Threshold'),
)


def validate_sources(sources):
    data = sources[4]
    assert data[0x3592:0x3596] == bytes((4, 0, 10, 0))
    assert data[0x35D4:0x35D8] == bytes((7, 0, 15, 0))
    assert data[0x35F0:0x35F4] == bytes((1, 1, 1, 1))
    assert data[0x3632:0x3636] == bytes((1, 1, 1, 2))
    assert data[0x364E:0x3652] == bytes((0, 1, 255, 0))
    assert data[0x3690:0x3694] == bytes((0, 0, 0, 1))
    assert data[0x36AA:0x36AC] == bytes(2)
    assert sum(entry[2][3] - entry[2][2] for entry in TABLES) == 280
    return dict(primary_rows=33, second_property_rows=14, second_weight_rows=14,
                second_standalone_neighbor_rows=13, keyboard_anchor_preserved=True)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические таблицы оснащения](../../../Docs/EquipmentPhysicalTables.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    lines = []
    emitted = set()
    for _, _, (_, _, _, _, name, fields, _) in TABLES:
        if name in emitted:
            continue
        emitted.add(name)
        lines.append('                struct ' + name)
        offset = 0
        assertions = []
        for field, width, note in fields:
            storage = 'db #00' if width == 1 else 'dw #0000'
            lines.append((field.ljust(16) + storage).ljust(80) + '; ' + note)
            assertions.append(f'                assert {name}.{field} == {offset}')
            offset += width
        lines.extend(('                ends', f'                assert {name} == {offset}', *assertions, ''))
    return '\n'.join(lines)

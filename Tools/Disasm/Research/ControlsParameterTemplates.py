"""Исходные группы строк и прибавок с сохранением перекрытия коэффициентов."""
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'ControlsParameterTables'
TAG = 'ControlsParameterTemplates'
REQUIRED_REPORTS = ('ControlsParameterTablesVerification',)
BINDINGS = ()
ROWS = (('First', 1, 'первая строка получает этот байт без добавки индекса'),) + tuple(
    (f'Row{index:02d}', 1, 'база строки, к ней прибавляется средний индекс C')
    for index in range(1, 9)
)
VALUES = tuple(
    (f'Value{index:02d}', 1, 'групповая прибавка к соответствующему полю Parameters')
    for index in range(15)
)
ROW_SPACING = tuple(
    (f'Spacing{index}', 1, 'исходный байт между группами, DE10 его не читает')
    for index in range(7)
)
VALUE_SPACING = (('Spacing', 1, 'исходный байт между группами, DE10 его не читает'),)
TABLES = tuple(
    (23, 0xDADE, (name, f'Source/Controls/Data/{name}.asm', start, end, structure, fields, labels))
    for name, start, end, structure, fields, labels in (
        ('ParameterRowGroups', 0x03FE, 0x043E, 'FParameterRowGroup', ROWS + ROW_SPACING,
         ('Group0', 'Group1', 'Group2', 'Group3')),
        ('ParameterLastRowGroup', 0x043E, 0x0447, 'FParameterRowValues', ROWS, ('Group4',)),
        ('ParameterValueGroups', 0x0447, 0x0477, 'FParameterValueGroup', VALUES + VALUE_SPACING,
         ('Group0', 'Group1', 'Group2')),
        ('ParameterLastValueGroup', 0x0477, 0x0486, 'FParameterValueBytes', VALUES, ('Group3',)),
    )
)


def validate_sources(sources):
    data = sources[23]
    assert data[0x043E:0x0447] == bytes(range(1, 10))
    assert all(data[0x03FE + group * 16 + 9:0x03FE + (group + 1) * 16] == bytes(7)
               for group in range(4))
    assert all(data[0x0447 + group * 16 + 15] == 0 for group in range(3))
    assert data[0x0457:0x0467] == bytes(16)
    assert data[0x0487:0x0496] == data[0x0486:0x04B3][1:16]
    assert sum(definition[3] - definition[2] for _, _, definition in TABLES) == 136
    return dict(row_groups=5, independent_value_groups=4,
                preserved_intergroup_bytes=31, fifth_value_group_inside_coefficients=True)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[группы исходных шаблонов](../../../Docs/ControlsParameterTables.md)')
    if definition[0] == 'ParameterRowGroups':
        text = text.replace('                assert $ == #DEDC',
                            '                assert $ == @ControlsParameterTablesConst.RowTemplates')
    if definition[0] == 'ParameterValueGroups':
        text = text.replace('                assert $ == #DF25',
                            '                assert $ == @ControlsParameterTablesConst.ValueTemplates')
    return text, labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    lines = []
    for _, _, (_, _, _, _, name, fields, _) in TABLES:
        lines.append('                struct ' + name)
        for field, _, note in fields:
            lines.append((field.ljust(16) + 'db #00').ljust(80) + '; ' + note)
        lines.extend(('                ends', f'                assert {name} == {len(fields)}'))
        lines.extend(f'                assert {name}.{field} == {offset}'
                     for offset, (field, _, _) in enumerate(fields))
        lines.append('')
    return '\n'.join(lines)

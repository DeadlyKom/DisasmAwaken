"""Физические структуры 95 потоков банка OBJECT3D."""
import re

HEADER = 'FActionModelHeader'
GROUP = 'FActionModelGroup'


def structures():
    lines = []
    definitions = [(HEADER, ('Unknown00', 'ScaleExponent')),
                   (GROUP, ('Mask', 'Component0', 'Component1', 'Component2'))]
    definitions += [('FActionModelPrimitive' + str(size), ('Header',) + tuple('Vertex' + str(i) for i in range(size)))
                    for size in range(2, 16)]
    for name, fields in definitions:
        lines.append('                struct ' + name)
        for field in fields:
            lines.append((field.ljust(16) + 'db #00').ljust(80) + '; ' + (
                'назначение исходного байта пока не установлено' if field == 'Unknown00' else
                'показатель масштаба преобразования' if field == 'ScaleExponent' else
                'код создаваемых комбинаций компонент' if field == 'Mask' else
                'компонента поставщика произведений' if field.startswith('Component') else
                'тип, материал либо режим и число индексов' if field == 'Header' else
                'байтовое смещение проецированной вершины, кратное пяти'))
        lines.extend(('                ends', f'                assert {name} == #{len(fields):02X}', ''))
    return '\n'.join(lines)


def render(data, packet):
    start = packet['offset']
    lines = ['                module ActionModels',
             '                ; Документация [формат потоков OBJECT3D](../../../Docs/ActionModelPackets.md)',
             f'                assert $ == #{0xC000 + start:04X}']
    labels = {}

    def record(offset, name, kind, fields, values):
        labels['ActionModels.' + name] = 0xC000 + offset
        lines.append(name.ljust(0) + ':'.ljust(16 - len(name)) + kind + ' {')
        for index, (field, value) in enumerate(zip(fields, values)):
            line = f'                    #{value:02X}' + (',' if index < len(values) - 1 else '')
            lines.append(line.ljust(80) + '; ' + field)
        lines.append('                }')

    record(start, f'M{start:04X}', HEADER, ('Unknown00, смысл не установлен', 'ScaleExponent'),
           data[start:start + 2])
    for index, group in enumerate(packet['fixed_groups']):
        record(group['offset'], f'G{start:04X}_{index:02X}', GROUP,
               ('Mask, комбинации вершин', 'Component0', 'Component1', 'Component2'),
               data[group['offset']:group['offset'] + 4])
    lines.append('                db #00'.ljust(80) + '; конец групп компонент')
    for index, primitive in enumerate(packet['records']):
        count = primitive['count']
        record(primitive['offset'], f'R{start:04X}_{index:02X}', 'FActionModelPrimitive' + str(count),
               ('Header, ' + ('линия' if primitive['kind'] == 'line' else 'грань'),) +
               tuple('Vertex' + str(i) for i in range(count)),
               data[primitive['offset']:primitive['offset'] + count + 1])
    lines.extend(('                db #00'.ljust(80) + '; конец потока примитивов',
                  f'                assert $ == #{0xC000 + packet["end"]:04X}', '                endmodule', ''))
    return '\n'.join(lines), labels


def parse(text):
    raw = bytearray()
    labels = {}
    position = None
    structure = None
    fields = 0
    for original in text.splitlines():
        line = original.partition(';')[0].strip()
        if not line or line in ('module ActionModels', 'endmodule'):
            continue
        if line.startswith('assert $ == #'):
            address = int(line.rsplit('#', 1)[1], 16)
            if position is None:
                position = address
            else:
                assert position == address
            continue
        match = re.fullmatch(r'(\w+):\s+(FActionModel\w+) \{', line)
        if match:
            assert structure is None
            name, structure = match.groups()
            labels['ActionModels.' + name] = position
            fields = 0
            continue
        if line == '}':
            expected = 2 if structure == HEADER else 4 if structure == GROUP else 1 + int(structure.removeprefix('FActionModelPrimitive'))
            assert fields == expected
            structure = None
            continue
        match = re.fullmatch(r'#([0-9A-F]{2}),?', line) if structure else re.fullmatch(r'db #([0-9A-F]{2})', line)
        assert match, original
        raw.append(int(match[1], 16))
        position += 1
        fields += bool(structure)
    assert structure is None and position is not None
    return bytes(raw), labels

"""Физические структуры и авторские имена 102 потоков банка OBJECT3D."""
import re
from ActionBank4Writes import HEADER_ADDRESSES

HEADER = 'FActionModelHeader'
GROUP = 'FActionModelGroup'
AUTHORED_TAIL_NAMES = {0x2469: 'St16', 0x251F: 'StPirat', 0x25C1: 'Prison',
    0x266B: 'StU1', 0x2707: 'StScince', 0x27AB: 'StU2', 0x2859: 'GipPl'}


# Авторские имена проверены по 3DTABS.a, LABELS.a и всем 10580 байтам OBJECT3D.
AUTHORED_PRIMARY_NAMES = {
    0x0000: 'KN01pol1',
    0x0040: 'Kd1',
    0x00A5: 'KN02mlt1',
    0x00CC: 'Kd2',
    0x0140: 'KN04trg1',
    0x0167: 'Kd4',
    0x01E2: 'KN05trg2',
    0x0202: 'Kd5',
    0x0251: 'KN06pol2',
    0x0271: 'Kd6',
    0x02BE: 'KN07krs1',
    0x0329: 'Kd7',
    0x03AE: 'KN08grz2',
    0x03F1: 'Kd8',
    0x0454: 'KN09mlt2',
    0x04B2: 'Kd9',
    0x054F: 'KN10trg3',
    0x056F: 'Kd10',
    0x0602: 'KN11grz3',
    0x064F: 'Kd11',
    0x06EA: 'Kd15',
    0x078D: 'KN16trg4',
    0x07C6: 'Kd16',
    0x0845: 'KN17mlt3',
    0x08A0: 'Kd17',
    0x0935: 'Kd19',
    0x09D7: 'KN21plS3',
    0x09F7: 'Kd21',
    0x0A40: 'Kd22',
    0x0AEE: 'KN25plS4',
    0x0B13: 'Kd25',
    0x0B52: 'KN26mlt4',
    0x0B7A: 'Kd26',
    0x0BEC: 'KN27pol7',
    0x0C11: 'Kd27',
    0x0C7D: 'KN28plS5',
    0x0CA5: 'Kd28',
    0x0CEB: 'KN29pol6',
    0x0D10: 'Kd29',
    0x0D8B: 'KN30grz4',
    0x0DC9: 'Kd30',
    0x0E36: 'KN31grz5',
    0x0E82: 'Kd31',
    0x0EF5: 'micKN',
    0x0F11: 'micKd1',
    0x0F61: 'micKd2',
    0x0FA2: 'REM_DR',
    0x0FF5: 'KontUFO',
    0x1047: 'ufo_K',
    0x1089: 'UfoRD',
    0x10DB: 'Kib_K',
    0x1103: 'KN03grz1',
    0x1150: 'Kd3',
    0x11C0: 'KN13ufo2',
    0x11F9: 'Kd13',
    0x1254: 'KN14ufo3',
    0x128A: 'Kd14',
    0x1308: 'Kd12',
    0x1398: 'KN18UFo4',
    0x13D5: 'Kd18',
    0x1479: 'KN20ufo5',
    0x14BE: 'Kd20',
    0x154A: 'KN24ufo7',
    0x157E: 'Kd24',
    0x15E2: 'KN23ufo6',
    0x1622: 'Kd23',
    0x1683: 'KOBRA',
    0x16E0: 'KOBRAD',
    0x1780: 'KRYL',
    0x17DF: 'KRYLD',
    0x184C: 'OSKOL',
    0x1864: 'ROKET',
    0x18B2: 'TARGET',
    0x18BA: 'TRASH',
    0x18D2: 'CRG1',
    0x1930: 'ASTER1',
    0x19A8: 'ASTER2',
    0x19E8: 'ASTER3',
    0x1A1E: 'UFO1D',
    0x1A6B: 'UFO1',
    0x1AAA: 'St1',
    0x1B80: 'St2',
    0x1C3A: 'St3',
    0x1CEC: 'St4',
    0x1D82: 'St5',
    0x1E12: 'St6',
    0x1EAC: 'St7',
    0x1F76: 'St8',
    0x2044: 'St9',
    0x20B0: 'St10',
    0x2152: 'St11',
    0x21CB: 'St12',
    0x22B9: 'St13',
    0x232D: 'St14',
    0x23D3: 'St15',
}
AUTHORED_MODEL_NAMES = AUTHORED_PRIMARY_NAMES | AUTHORED_TAIL_NAMES


def model_name(offset):
    return AUTHORED_MODEL_NAMES.get(offset, f'M{offset:04X}')


def model_path(offset):
    return 'Source/Action/Data/Model' + AUTHORED_MODEL_NAMES.get(offset, f'{offset:04X}') + '.asm'


def verify_bound_mantissa(raw):
    magnitudes = []
    for offset in range(2, len(raw), 4):
        if not raw[offset]:
            break
        assert offset + 4 <= len(raw)
        magnitudes.extend(min(byte, 256 - byte) for byte in raw[offset + 1:offset + 4])
    else:
        raise AssertionError('Нет ограничителя групп OBJECT3D')
    assert raw[0] == max(magnitudes, default=1)
    return len(magnitudes) // 3


def structures():
    lines = []
    definitions = [(HEADER, ('BoundMantissa', 'ScaleExponent')),
                   (GROUP, ('Mask', 'Component0', 'Component1', 'Component2'))]
    definitions += [('FActionModelPrimitive' + str(size), ('Header',) + tuple('Vertex' + str(i) for i in range(size)))
                    for size in range(2, 16)]
    for name, fields in definitions:
        lines.append('                struct ' + name)
        for field in fields:
            lines.append((field.ljust(16) + 'db #00').ljust(80) + '; ' + (
                'мантисса границы близости и проекции' if field == 'BoundMantissa' else
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
    if start == 0x18B2:
        lines.append('                ; Авторский пакет TARGET, хвост после ограничителей подключён отдельно.')
    labels = {}

    def record(offset, name, kind, fields, values):
        labels['ActionModels.' + name] = 0xC000 + offset
        if kind.startswith('FActionModelPrimitive') and 0xC000 + offset in HEADER_ADDRESSES:
            labels['ActionModels.' + name + '.Header'] = 0xC000 + offset
        lines.append(name.ljust(0) + ':'.ljust(16 - len(name)) + kind + ' {')
        for index, (field, value) in enumerate(zip(fields, values)):
            line = f'                    #{value:02X}' + (',' if index < len(values) - 1 else '')
            lines.append(line.ljust(80) + '; ' + field)
        lines.append('                }')

    record(start, model_name(start), HEADER, ('BoundMantissa, мантисса границы близости и проекции', 'ScaleExponent'),
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
            if structure.startswith('FActionModelPrimitive') and position in HEADER_ADDRESSES:
                labels['ActionModels.' + name + '.Header'] = position
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

"""128 физических little-endian указателей 9E00, чётность игрового индекса этим не вводится."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records
from ActionModelPhysicalData import model_name, AUTHORED_PRIMARY_NAMES
FIELDS = (('Target', 2, 'адрес потока OBJECT3D банка 4, это не адрес вызова'),)
TABLE = ('ActionObjectPointers', 'Source/Action/Data/ObjectPointers.asm', 0x3E00, 0x3F00,
         'FObjectDataPointer', FIELDS, tuple('Offset' + format(index, '02X') for index in range(0, 256, 2)))
TAIL_MODELS = (0x2469, 0x251F, 0x25C1, 0x266B, 0x27AB, 0x2707, 0x2859)
TAIL_FIELDS = (('Target', 2, 'адрес начала дополнительного потока OBJECT3D банка 4'),)
TAIL_TABLE = ('ActionTailModelPointers', 'Source/Action/Data/TailModelPointers.asm', 0x3F00, 0x3F1C,
              'FObjectDataPointer', TAIL_FIELDS, tuple(f'Offset{offset:02X}' for offset in range(0, 28, 2)))


def tail_targets():
    return {'ActionModels.' + model_name(offset): 0xC000 + offset for offset in TAIL_MODELS}


def render_tail(source):
    text, labels = render_records(source, TAIL_TABLE, 0x6000)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[дополнительные указатели OBJECT3D](../../../Docs/ActionModelTail.md)')
    text = text.replace('                assert $ == #9F00',
        '                ; Авторские пары в физическом порядке: IST16, IST_PIRAT, IPRISON, IST_U1, IST_U2, IST_SCINCE, IGIP_PL\n'
        '                assert $ == #9F00')
    for label, address in tail_targets().items():
        literal = f'#{address:04X}'
        assert text.count(literal) == 2
        text = re.sub(fr'^ {{20}}{literal} *(;.*)$',
                      lambda match: (' ' * 20 + '@' + label).ljust(80) + match[1], text, flags=re.M)
    return text, labels


def parse_tail(text, symbols):
    targets = tail_targets()
    assert all(symbols[label.upper()] == address for label, address in targets.items())
    names = re.findall(r'^ {20}@([\w.]+) *;', text, re.M)
    assert names == [label for label in targets for _ in range(2)]
    for label, address in targets.items():
        text = text.replace('@' + label, f'#{address:04X}')
    return parse_records(text, TAIL_TABLE, 0x6000)


def render(source):
    text, labels = render_records(source, TABLE, 0x6000)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[указатели OBJECT3D](../../../Docs/ActionObjectPointers.md)')
    text = text.replace('                assert $ == #9E00',
        '                ; Первая страница архивной таблицы L97, номера пар и цели сверены с LABELS.a\n'
        '                assert $ == #9E00')
    count = 0
    for offset, name in AUTHORED_PRIMARY_NAMES.items():
        pattern = fr'^ {{20}}#{0xC000 + offset:04X} *(;.*)$'
        text, matches = re.subn(pattern,
            lambda match: (' ' * 20 + '@ActionModels.' + name).ljust(80) + match[1], text, flags=re.M)
        assert matches > 0
        count += matches
    assert count == 128
    return text, labels


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines() if line.partition(';')[0].strip()]
    assert clean.pop(0) == 'module ActionObjectPointers'
    assert clean.pop(0) == 'assert $ == #9E00'
    targets = {'ActionModels.' + name: 0xC000 + offset for offset, name in AUTHORED_PRIMARY_NAMES.items()}
    for label in TABLE[-1]:
        assert clean.pop(0) == label + ':'.ljust(16 - len(label)) + 'FObjectDataPointer {'
        reference = clean.pop(0)
        assert reference.startswith('@') and reference[1:] in targets
        assert clean.pop(0) == '}'
    assert clean == ['assert $ == #9F00', 'endmodule']
    text = re.sub(r'^ {20}@([\w.]+) *(;.*)$',
        lambda match: (' ' * 20 + f'#{targets[match[1]]:04X}').ljust(80) + match[2], text, flags=re.M)
    return parse_records(text, TABLE, 0x6000)


def structure_text():
    return '\n'.join(('', '                ; Исходный little-endian указатель потока OBJECT3D банка 4',
        '                struct FObjectDataPointer',
        'Target          dw #0000'.ljust(80) + '; адрес данных банка 4, не адрес кода',
        '                ends', '                assert FObjectDataPointer == #02',
        '                assert FObjectDataPointer.Target == #00', ''))

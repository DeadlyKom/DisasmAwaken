"""128 физических little-endian указателей 9E00, чётность игрового индекса этим не вводится."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records
FIELDS = (('Target', 2, 'адрес потока OBJECT3D банка 4, это не адрес вызова'),)
TABLE = ('ActionObjectPointers', 'Source/Action/Data/ObjectPointers.asm', 0x3E00, 0x3F00,
         'FObjectDataPointer', FIELDS, tuple('Offset' + format(index, '02X') for index in range(0, 256, 2)))
TAIL_MODELS = (0x2469, 0x251F, 0x25C1, 0x266B, 0x27AB, 0x2707, 0x2859)
TAIL_FIELDS = (('Target', 2, 'адрес начала дополнительного потока OBJECT3D банка 4'),)
TAIL_TABLE = ('ActionTailModelPointers', 'Source/Action/Data/TailModelPointers.asm', 0x3F00, 0x3F1C,
              'FObjectDataPointer', TAIL_FIELDS, tuple(f'Offset{offset:02X}' for offset in range(0, 28, 2)))


def tail_targets():
    return {f'ActionModels.M{offset:04X}': 0xC000 + offset for offset in TAIL_MODELS}


def render_tail(source):
    text, labels = render_records(source, TAIL_TABLE, 0x6000)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[дополнительные указатели OBJECT3D](../../../Docs/ActionModelTail.md)')
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
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[указатели OBJECT3D](../../../Docs/ActionObjectPointers.md)'), labels


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines() if line.partition(';')[0].strip()]
    assert clean.pop(0) == 'module ActionObjectPointers'
    assert clean.pop(0) == 'assert $ == #9E00'
    for label in TABLE[-1]:
        assert clean.pop(0) == label + ':'.ljust(16 - len(label)) + 'FObjectDataPointer {'
        assert re.fullmatch(r'#[0-9A-F]{4}', clean.pop(0))
        assert clean.pop(0) == '}'
    assert clean == ['assert $ == #9F00', 'endmodule']
    return parse_records(text, TABLE, 0x6000)


def structure_text():
    return '\n'.join(('', '                ; Исходный little-endian указатель потока OBJECT3D банка 4',
        '                struct FObjectDataPointer',
        'Target          dw #0000'.ljust(80) + '; адрес данных банка 4, не адрес кода',
        '                ends', '                assert FObjectDataPointer == #02',
        '                assert FObjectDataPointer.Target == #00', ''))

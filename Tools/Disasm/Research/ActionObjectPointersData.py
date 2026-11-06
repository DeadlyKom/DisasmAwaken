"""128 физических little-endian указателей 9E00, чётность игрового индекса этим не вводится."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records
FIELDS = (('Target', 2, 'адрес потока OBJECT3D банка 4, это не адрес вызова'),)
TABLE = ('ActionObjectPointers', 'Source/Action/Data/ObjectPointers.asm', 0x3E00, 0x3F00,
         'FObjectDataPointer', FIELDS, tuple('Offset' + format(index, '02X') for index in range(0, 256, 2)))


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

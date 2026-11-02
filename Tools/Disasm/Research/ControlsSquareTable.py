"""Две исходные байтовые плоскости квадратов 0..255 в CONTROL0."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS = (('Value',1,'байт квадрата, плоскость и индекс определяются именем физической записи'),)
TABLE = ('ControlsSquareTable','Source/Controls/Data/Squares.asm',0x300,0x500,
    'FSquareTableByte',FIELDS,tuple(part+format(i,'02X') for part in ('Low','High') for i in range(256)))


def validate(source):
    raw = source[0x300:0x500]
    assert len(raw) == 512
    # Сравнение фактических плоскостей с квадратом индекса, сборочные данные берутся из оригинала.
    assert all(raw[i]+256*raw[256+i] == i*i for i in range(256))
    return raw


def render(source):
    validate(source)
    text,symbols = render_records(source,TABLE,0xC000)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[две плоскости квадратов](../../../Docs/ControlsSquares.md)')
    return text,symbols


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines()]
    clean = [line for line in clean if line]
    assert clean.pop(0) == 'module ControlsSquareTable' and clean.pop(0) == 'assert $ == #C300'
    for name in TABLE[6]:
        assert clean.pop(0) == (name+':').ljust(16)+'FSquareTableByte {'
        assert re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0))
        assert clean.pop(0) == '}'
    assert clean == ['assert $ == #C500','endmodule']
    return parse_records(text,TABLE,0xC000)

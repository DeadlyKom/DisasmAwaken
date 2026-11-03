"""Семь физических масок E973, нулевой индекс текущая шкала не читает."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records
FIELDS=(('Pattern',1,'байт шести строк частичного столбца, индекс 0 этот потребитель не читает'),)
TABLE=('ControlsGaugeMasks','Source/Controls/Data/GaugeMasks.asm',0xE95,0xE9C,
       'FGaugePartialMask',FIELDS,tuple('Index'+format(i,'02X') for i in range(7)))


def render(source):
    assert source[0xE95:0xE9C]==bytes(0xAA & ((255 << (7-i))&255) for i in range(7))
    text,symbols=render_records(source,TABLE,0xDADE)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[шестистрочная шкала](../../../Docs/ControlsSixRowGauge.md)'),symbols


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module ControlsGaugeMasks' and clean.pop(0)=='assert $ == #E973'
    for name in TABLE[6]:
        assert clean.pop(0)==(name+':').ljust(16)+'FGaugePartialMask {'
        assert re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #E97A','endmodule']
    return parse_records(text,TABLE,0xDADE)

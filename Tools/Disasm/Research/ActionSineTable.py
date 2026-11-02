"""Исходная знаковая синусоида ACTION, 256 физических байтов с масштабом 128."""
import math
import re
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=(('Value',1,'знаковый байт синуса в дополнительном коде, масштаб 128'),)
TABLE=('ActionSineTable','Source/Action/Data/SineTable.asm',0x3900,0x3A00,
       'FFixedSineValue',FIELDS,tuple('Angle'+format(i,'02X') for i in range(256)))


def validate(source):
    data=source[0x3900:0x3A00]
    assert len(data)==256
    # Сравнение формулы с фактическими байтами, таблица для сборки не вычисляется заново.
    formula=bytes(max(-127,min(127,round(128*math.sin(2*math.pi*i/256))))&255 for i in range(256))
    assert data==formula
    assert all(data[(i+128)&255]==((-data[i])&255) for i in range(128))
    return data


def render(source):
    validate(source)
    text,symbols=render_records(source,TABLE,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[исходная синусоида ACTION](../../../Docs/ActionSineTable.md)'),symbols


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module ActionSineTable' and clean.pop(0)=='assert $ == #9900'
    for name in TABLE[6]:
        assert clean.pop(0)==(name+':').ljust(16)+'FFixedSineValue {'
        assert re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #9A00','endmodule']
    return parse_records(text,TABLE,0x6000)

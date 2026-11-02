"""Две девятибайтовые таблицы затравок и 12 фактически записываемых байтов масок."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records

TABLES = (
    ('ControlsSmallMaskSeeds','Source/Controls/Data/SmallMaskSeeds.asm',0x197E,0x1990,
        'FSmallMaskSeed',(('Packed',1,'разряды 7..3 задают начальную маску, 2..0 число арифметических сдвигов'),),
        tuple(part+'R'+str(radius) for part in ('Primary','Alternate') for radius in range(9))),
    ('ControlsSmallMaskRows','Source/Controls/Data/SmallMaskRows.asm',0x1990,0x199C,
        'FSmallMaskRow',(('Mask',1,'исходный ноль, при подготовке заменяется строковой маской'),),
        tuple('Row'+format(i,'02X') for i in range(12))))


def validate(source):
    assert source[0x197E:0x1990]==bytes.fromhex('000081414222231314000081c1c2e2e3f3f4')
    assert source[0x1990:0x199C]==bytes(12)
    return [source[t[2]:t[3]] for t in TABLES]


def render(source,table):
    validate(source)
    text,symbols=render_records(source,table,0xC000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[затравки и строки масок малых тел](../../../Docs/ControlsSmallMasks.md)'),symbols


def parse(text,table):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module '+table[0]
    assert clean.pop(0)=='assert $ == #'+format(0xC000+table[2],'04X')
    for name in table[6]:
        assert clean.pop(0)==(name+':').ljust(16)+table[4]+' {'
        assert re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #'+format(0xC000+table[3],'04X'),'endmodule']
    return parse_records(text,table,0xC000)

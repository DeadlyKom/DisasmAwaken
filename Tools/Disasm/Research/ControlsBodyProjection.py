"""Четыре физически смежных входных байта проекции, флаги разобраны частично."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=(('OffsetY',1,'вертикальное числовое смещение до выбора знака'),
    ('OffsetX',1,'горизонтальное числовое смещение до выбора знака'),
    ('Flags',1,'разряды 0 и 1 задают направления, остальные этим форматом не объявляются разобранными'),
    ('Radius',1,'радиус, малый рисователь принимает только 2..8'))
TABLE=('ControlsBodyProjection','Source/Controls/Data/BodyProjection.asm',0x117D,0x1181,
    'FBodyProjection',FIELDS,('Value',))


def render(source):
    text,symbols=render_records(source,TABLE,0xC000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[вход проекции и малый рисователь](../../../Docs/ControlsSmallBodies.md)'),symbols


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean[:3]==['module ControlsBodyProjection','assert $ == #D17D','Value:'.ljust(16)+'FBodyProjection {']
    assert all(re.fullmatch(r'#[0-9A-F]{2},?' if i<3 else r'#[0-9A-F]{2}',line) for i,line in enumerate(clean[3:7]))
    assert clean[7:]==['}','assert $ == #D181','endmodule']
    return parse_records(text,TABLE,0xC000)

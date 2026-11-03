"""Физическая пара байтов ACTION по 9C10, локальный приоритет доказан читателем 74FB."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records
FIELDS=(('Preferred',1,'выбирается вместе со своим адресом, если байт ненулевой'),
        ('Fallback',1,'выбирается вместе со своим адресом, если Preferred равен нулю'))
TABLE=('ActionPreferredByteState','Source/Action/Data/PreferredByteState.asm',0x3C10,0x3C12,
       'FPreferredBytePair',FIELDS,('Value',))


def render(source):
    text,labels=render_records(source,TABLE,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[выбор байта с приоритетом](../../../Docs/ActionPreferredByte.md)'),labels


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module ActionPreferredByteState' and clean.pop(0)=='assert $ == #9C10'
    assert clean.pop(0)=='Value:          FPreferredBytePair {'
    assert re.fullmatch(r'#[0-9A-F]{2},',clean.pop(0))
    assert re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0))
    assert clean==['}','assert $ == #9C12','endmodule']
    return parse_records(text,TABLE,0x6000)

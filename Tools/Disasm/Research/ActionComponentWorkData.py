"""Три существующих физических FComponent24 перед преобразованием, без выдуманных единиц младшего байта."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records
FIELDS=(('Low',1,'младшие восемь бит модуля проекции, вес 1, подготовитель обнуляет, кодировщик сохраняет'),
    ('Middle',1,'биты 15..8 модуля проекции, вес байта 256'),
    ('High',1,'бит 7 является кодом знака после публикатора, биты 6..0 хранят старшую часть модуля'))
TABLE=('ActionComponentWork','Source/Action/Data/ComponentWork.asm',0x3B1E,0x3B27,'FComponent24',FIELDS,
    ('Component0','Component1','Component2'))


def validate(source):
    raw=bytes(source[TABLE[2]:TABLE[3]]);assert raw==bytes(9)
    return raw


def render(source):
    validate(source);text,labels=render_records(source,TABLE,0x6000)
    text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[кодирование знака и модуля](../../../Docs/ActionComponentEncoding.md)')
    return text,labels


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()];clean=[line for line in clean if line]
    assert clean.pop(0)=='module ActionComponentWork' and clean.pop(0)=='assert $ == #9B1E'
    for name in TABLE[6]:
        assert clean.pop(0)==(name+':').ljust(16)+'FComponent24 {'
        for index in range(3):assert re.fullmatch(r'#[0-9A-F]{2}'+(',' if index<2 else ''),clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #9B27','endmodule']
    return parse_records(text,TABLE,0x6000)

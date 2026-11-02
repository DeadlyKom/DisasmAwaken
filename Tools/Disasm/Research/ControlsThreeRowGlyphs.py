"""Четыре исходных знака 3x3, восемь фаз и шесть физических байтов каждой фазы."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records

FIELDS = tuple((name,1,meaning) for name,meaning in (
    ('Row0Left','левая байтовая маска верхней строки'),('Row0Right','правая байтовая маска верхней строки'),
    ('Row1Left','левая байтовая маска средней строки'),('Row1Right','правая байтовая маска средней строки'),
    ('Row2Left','левая байтовая маска нижней строки'),('Row2Right','правая байтовая маска нижней строки')))
SHAPES = (('Plus',(0x40,0xE0,0x40)),('Cross',(0xA0,0x40,0xA0)),
          ('Solid',(0xE0,0xE0,0xE0)),('Hollow',(0xE0,0xA0,0xE0)))
TABLE = ('ControlsThreeRowGlyphs','Source/Controls/Data/ThreeRowGlyphs.asm',0x6D3,0x793,
         'FThreeRowGlyphPhase',FIELDS,tuple(name+format(phase,'02X') for name,_ in SHAPES for phase in range(8)))


def validate(source):
    raw = source[0x6D3:0x793]
    assert len(raw)==192
    # Сравнение с тремя исходными пиксельными строками, данные сборки читаются из оригинала.
    for shape,(_,rows) in enumerate(SHAPES):
        for phase in range(8):
            for row,value in enumerate(rows):
                position = shape*48+phase*6+row*2
                assert (raw[position]<<8)|raw[position+1] == (value<<8)>>phase
    return raw


def render(source):
    validate(source)
    text,symbols = render_records(source,TABLE,0xDADE)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[трёхстрочные знаки и рисователь](../../../Docs/ControlsThreeRowGlyph.md)'),symbols


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines()]
    clean = [line for line in clean if line]
    assert clean.pop(0)=='module ControlsThreeRowGlyphs' and clean.pop(0)=='assert $ == #E1B1'
    for name in TABLE[6]:
        assert clean.pop(0)==(name+':').ljust(16)+'FThreeRowGlyphPhase {'
        for index in range(6):
            assert re.fullmatch(r'#[0-9A-F]{2}'+(',' if index<5 else ''),clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #E271','endmodule']
    return parse_records(text,TABLE,0xDADE)

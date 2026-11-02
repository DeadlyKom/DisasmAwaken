"""Физические байты входов E021, порядок координат третьего входа отличается."""
import re

PATH = 'Source/Action/Data/GlyphIndicatorState.asm'
START,END = 0x3B81,0x3B8D
MODULE = 'ActionGlyphIndicatorState'
STRUCTURES = {
    'FGlyphIndicatorControl': (
        ('FirstMode','код 01 пропускает первый знак, остальные значения допускают его'),
        ('ThirdGate','ноль допускает третий знак после проверки второго, ненулевое значение запрещает'),
        ('Unknown83','E021 этот байт не читает, полный игровой смысл не установлен')),
    'FGlyphIndicatorYX': (
        ('Y','байт вертикального смещения в формуле экрана'),
        ('X','байт горизонтального смещения в формуле экрана'),
        ('SignSource','знаковый байт выбора заполненного или полого квадрата, глобальный смысл не установлен')),
    'FGlyphIndicatorXY': (
        ('X','байт горизонтального смещения в формуле экрана'),
        ('Y','байт вертикального смещения в формуле экрана'),
        ('SignSource','знаковый байт выбора формы, у Second весь байт также входит в OR-маркер отсутствия')),
}
RECORDS = (('Control','FGlyphIndicatorControl'),('Third','FGlyphIndicatorYX'),
           ('Second','FGlyphIndicatorXY'),('First','FGlyphIndicatorXY'))


def render(source):
    raw = source[START:END]
    assert len(raw)==12
    lines = ['                module '+MODULE,
        '                ; Документация [входы трёх знаков](../../../Docs/ControlsGlyphIndicators.md)',
        '                assert $ == #9B81']
    for index,(label,structure) in enumerate(RECORDS):
        lines += ['                ; -----------------------------------------',
                  '                ; исходная физическая запись '+label,(label+':').ljust(16)+structure+' {']
        for field_index,(field,meaning) in enumerate(STRUCTURES[structure]):
            line='                    #'+format(raw[3*index+field_index],'02X')+(',' if field_index<2 else '')
            lines.append(line.ljust(80)+'; '+field+', '+meaning)
        lines += ['                }']
    lines += ['                assert $ == #9B8D','                endmodule']
    text='\n'.join(lines)+'\n'
    reconstructed,bindings = parse(text)
    assert reconstructed==raw
    return text,bindings


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module '+MODULE and clean.pop(0)=='assert $ == #9B81'
    raw=bytearray()
    bindings={}
    for index,(label,structure) in enumerate(RECORDS):
        assert clean.pop(0)==(label+':').ljust(16)+structure+' {'
        address=0x9B81+3*index
        bindings[MODULE+'.'+label]=address
        for field_index,(field,_) in enumerate(STRUCTURES[structure]):
            literal=clean.pop(0)
            assert re.fullmatch(r'#[0-9A-F]{2}'+(',' if field_index<2 else ''),literal)
            raw.append(int(literal.rstrip(',')[1:],16))
            bindings[MODULE+'.'+label+'.'+field]=address+field_index
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #9B8D','endmodule']
    return bytes(raw),bindings

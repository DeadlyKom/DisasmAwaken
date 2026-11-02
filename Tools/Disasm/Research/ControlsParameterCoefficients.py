"""Пятнадцать исходных трёхбайтовых правил, сохраняются как физические записи."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records

FIELDS = (('Base',1,'аддитивная база перед байтом выбранного шаблона'),
          ('SlopeCode',1,'числовой код наклона, 01 ноль, 02 плюс C, FE минус C'),
          ('ShiftMask',1,'ненулевая степень двойки, число SRA равно позиции установленного разряда'))
TABLE = ('ControlsParameterCoefficients','Source/Controls/Data/ParameterCoefficients.asm',0x486,0x4B3,
         'FParameterCoefficient',FIELDS,tuple('Field'+format(i,'02X') for i in range(15)))


def validate(source):
    raw = source[0x486:0x4B3]
    assert len(raw)==45
    assert all(raw[3*i+1] in (1,2,254) and raw[3*i+2] in (1,2,4,8) for i in range(15))
    return raw


def render(source):
    validate(source)
    text,symbols = render_records(source,TABLE,0xDADE)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[формирование набора параметров](../../../Docs/ControlsParameterTables.md)'),symbols


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines()]
    clean = [line for line in clean if line]
    assert clean.pop(0)=='module ControlsParameterCoefficients' and clean.pop(0)=='assert $ == #DF64'
    for name in TABLE[6]:
        assert clean.pop(0)==(name+':').ljust(16)+'FParameterCoefficient {'
        for index in range(3):
            assert re.fullmatch(r'#[0-9A-F]{2}'+(',' if index<2 else ''),clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #DF91','endmodule']
    return parse_records(text,TABLE,0xDADE)

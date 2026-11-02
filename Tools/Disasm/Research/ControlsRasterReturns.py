"""Шестнадцать физических адресов для перенаправленного RET внутри неразобранного E291."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=(('Target',2,'адрес выбранного кодового хвоста банка 1, полный алгоритм хвоста ещё не установлен'),)
TABLE=('ControlsRasterReturns','Source/Controls/Data/RasterReturns.asm',0x793,0x7B3,
       'FReturnDispatchEntry',FIELDS,tuple('Index'+format(i,'02X') for i in range(16)))


def render(source):
    raw=source[0x793:0x7B3]
    assert len(raw)==32 and len({raw[2*i]|raw[2*i+1]<<8 for i in range(16)})==16
    text,bindings=render_records(source,TABLE,0xDADE)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[частичная диспетчеризация через RET](../../../Docs/ControlsRasterReturns.md)'),bindings


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module ControlsRasterReturns' and clean.pop(0)=='assert $ == #E271'
    for name in TABLE[6]:
        assert clean.pop(0)==(name+':').ljust(16)+'FReturnDispatchEntry {'
        assert re.fullmatch(r'#[0-9A-F]{4}',clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #E291','endmodule']
    return parse_records(text,TABLE,0xDADE)


def name_operands(region,function_address,operation):
    if region=='Controls' and function_address==0xE291:
        operation=operation.replace('LD SP, #E271','LD SP, @ControlsRasterReturns.Index00')
        operation=operation.replace('(#E2BC)','(@ControlsRasterReturnsState.EntryIndex)')
        operation=operation.replace('(#E471)','(@ControlsRasterReturnsState.RepeatIndex)')
    return operation

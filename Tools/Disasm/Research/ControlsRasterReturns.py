"""Шестнадцать физических входов фаз фона DrawRadar, адреса исходного RET сохранены."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records
from ControlsRasterBackgroundFacts import ROWS

TARGETS=(0xE2DB,)+ROWS[1:]
FIELDS=(('Target',2,'адрес начального входа фазы фона радара в банке 1'),)
TABLE=('ControlsRasterReturns','Source/Controls/Data/RasterReturns.asm',0x793,0x7B3,
       'FReturnDispatchEntry',FIELDS,tuple('Index'+format(i,'02X') for i in range(16)))


def render(source):
    raw=source[0x793:0x7B3]
    assert len(raw)==32 and len({raw[2*i]|raw[2*i+1]<<8 for i in range(16)})==16
    text,bindings=render_records(source,TABLE,0xDADE)
    assert [int.from_bytes(raw[index:index+2],'little') for index in range(0,32,2)]==list(TARGETS)
    for index,target in enumerate(TARGETS):
        line=next(line for line in text.splitlines() if line.lstrip().startswith(f'#{target:04X} '))
        note='начальный вход фазы 0 с двумя обменами AF' if index==0 else f'начальный вход фазы {index} фона радара'
        replacement=f'                    @Controls.DrawRadar.DrawPhase{index:02d}'.ljust(80)+'; Target, '+note
        text=text.replace(line,replacement)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[диспетчеризация фаз фона через RET](../../../Docs/ControlsRasterReturns.md)'),bindings


def parse(text):
    # Преобразование только установленных символических целей для проверки физических слов.
    text=re.sub(r'@Controls\.DrawRadar\.DrawPhase(0[0-9]|1[0-5])\b',
        lambda match:f'#{TARGETS[int(match[1])]:04X}',text)
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
        operation=operation.replace('LD HL, #E685','LD HL, @ControlsObjectPixelMasks.Phase00')
        operation=operation.replace('LD HL, #E68D','LD HL, @ControlsObjectClearMasks.Phase00')
    return operation

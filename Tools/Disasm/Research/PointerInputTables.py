"""Физические флаги, 16 направлений и шесть привязок клавиатуры исходного файла станции."""
FLAGS='Source/Station/Data/InputFlags.asm'
DIRECTIONS='Source/Station/Data/PointerDirections.asm'
KEYS='Source/Station/Data/PointerKeys.asm'
FIELDS=('Right','Left','Down','Up','Action2','Action1')
TARGETS=(0x6762,0x6757,0x6750,0x6762,0x676A,0x673D,0x671C,0x6762,0x6763,0x672A,0x670E,0x6762,0x6762,0x6762,0x6762,0x6762)
LABELS=('None','Right','Left','BothX','Down','DownRight','DownLeft','DownBothX','Up','UpRight','UpLeft','UpBothX','BothY','RightBothY','LeftBothY','BothXY')


def render(source,names):
    outputs={};symbols={}
    lines=['                module InputFlags','; Документация [опрос ввода](../../../Docs/PointerInputs.md)',
           '                assert $ == #66E8','State:          FInputFlags {']
    for i,field in enumerate(FIELDS):lines.append((f'                    #{source[0x994+i]:02X}'+(',' if i<5 else '')).ljust(80)+'; FInputFlags.'+field)
    lines+=['                }','                assert $ == #66EE','                endmodule']
    outputs[FLAGS]='\n'.join(lines)+'\n';symbols['InputFlags.State']=0x66E8
    lines=['                module PointerDirections','; Документация [опрос ввода](../../../Docs/PointerInputs.md)',
           '; индекс из младших четырёх битов текущей выборки, порядок 0..15', '                assert $ == #66EE']
    for i,(label,target) in enumerate(zip(LABELS,TARGETS)):
        assert int.from_bytes(source[0x99A+2*i:0x99C+2*i],'little')==target
        lines.append((label+':').ljust(16)+('FPointerDirection { @'+names['Station',target]+' }').ljust(64)+'; Handler для маски #'+f'{i:X}')
        symbols['PointerDirections.'+label]=0x66EE+2*i
    lines+=['                assert $ == #670E','                endmodule'];outputs[DIRECTIONS]='\n'.join(lines)+'\n'
    lines=['                module PointerKeys','; Документация [опрос ввода](../../../Docs/PointerInputs.md)',
           '; исходные привязки, RowMask выбирает строку, KeyMask проверяет её активные низкие разряды',
           '                assert $ == #99B6']
    for i,label in enumerate(('Up','Down','Left','Right','Action2','Action1')):
        row,mask=source[0x39B6+2*i:0x39B8+2*i]
        lines.append((label+':').ljust(16)+f'FKeyBinding {{ #{row:02X}, #{mask:02X} }}'.ljust(64)+'; RowMask, KeyMask для '+label)
        symbols['PointerKeys.'+label]=0x99B6+2*i
    lines+=['                assert $ == #99C2','                endmodule'];outputs[KEYS]='\n'.join(lines)+'\n'
    return outputs,symbols

"""Физическая девятибайтовая запись состояния мыши, исходный адрес #6585."""
PATH='Source/Station/Data/MouseInput.asm'
FIELDS=('Action2','Up','Down','Right','Left','Action1','ExtraButton','PreviousX','PreviousY')


def render(source):
    values=source[0x831:0x83A]
    assert len(values)==9
    lines=['                module MouseInput','; Документация [мышь](../../../Docs/MouseInput.md)',
           '; семь независимых байтов флагов и два последних аппаратных счётчика',
           '                assert $ == #6585','State:          FMouseInput {']
    for i,(value,field) in enumerate(zip(values,FIELDS)):
        lines.append((f'                    #{value:02X}'+(',' if i<8 else '')).ljust(80)+'; FMouseInput.'+field)
    lines+=['                }','                assert $ == #658E','                endmodule']
    return '\n'.join(lines)+'\n',{'MouseInput.State':0x6585}

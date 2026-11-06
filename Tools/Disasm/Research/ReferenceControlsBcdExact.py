"""Независимые маски знаков, полные состояния пар и M1 исходных F142/F188."""
from ReferenceControlsPointMotion import block_cost
from ReferenceControlsPointRespawn import refresh


def or_flags(value):return (value&0xA8)|(64 if not value else 0)|(4 if value.bit_count()%2==0 else 0)


def nibble(memory,registers,value,column,stack,emit):
    index=16+(value&15);pointer=0xC600+6*(index//2);mask=0x0F if column&1 else 0xF0
    rotate=(column&1)!=(index&1);new_c=(column+1)&255
    # Расчёт альтернативного AF после первого BIT, Carry остаётся от SRL исходной колонки.
    registers[16:18]=[column>>1,(column&1)|16|(new_c&0x28)|(0 if new_c&1 else 68)]
    emit(stack-2,0xA9);emit(stack-1,0xF1)
    for row in range(6):
        address=((0x51+row)<<8)|(column//2);source=memory[pointer+row]
        rotated=((source<<4)|(source>>4))&255 if rotate else source
        preserved=memory[address]&(~mask&255);result=preserved|(rotated&mask)
        emit(address,result)
    registers[0:2]=[result,or_flags(result)]
    registers[18:24]=[preserved,mask,(pointer+5)>>8,(pointer+5)&255,0x56,column//2]
    m1=block_cost(0xF188,0xF1AB)+block_cost(0xEFF1,0xEFF7)+int(not new_c&1)
    m1+=block_cost(0xEFF9,0xEFFD)+(block_cost(0xEFFD,0xF001) if index&1 else 0)+block_cost(0xF001,0xF006)
    m1+=block_cost(0xF006,0xF059) if rotate else block_cost(0xF059,0xF094)
    return m1


def evaluate(memory,initial,value=None,column=None):
    registers=list(initial);writes=[];shadow={};stack=initial[12];m1=0
    class View:
        def __getitem__(self,address):return shadow.get(address,memory[address])
    view=View()
    def emit(address,value):writes.append((address,value));shadow[address]=value
    if value is not None:
        m1=nibble(view,registers,value,column,stack,emit)
    else:
        values=(initial[7],initial[6],initial[5],initial[4]);mask=initial[2]
        columns=((47,46),(44,43),(41,40),(39,38));returns=((0xF148,0xF152),(0xF15B,0xF165),(0xF16E,0xF178),(0xF181,None))
        starts=(0xF142,0xF155,0xF168,0xF17B);ends=(0xF155,0xF168,0xF17B,0xF188)
        for pair,(byte,cols,targets) in enumerate(zip(values,columns,returns)):
            for half,(col,target) in enumerate(zip(cols,targets)):
                value=byte if half==0 else ((byte>>4)|(byte<<4))&255
                registers[3]=col
                child_stack=stack-2 if target is not None else stack
                if target is not None:emit(child_stack,target&255);emit(child_stack+1,target>>8)
                m1+=nibble(view,registers,value,col,child_stack,emit)
            m1+=block_cost(starts[pair],ends[pair])
            if pair==3:break
            # Проверка разрешения следующей пары, Carry сохранён от последнего пиксельного OR и равен нулю.
            clear=not mask&(1<<pair)
            registers[1]=16|(mask&0x28)|(68 if clear else 0)
            if clear:break
    registers[12],registers[15],registers[24]=stack+2,refresh(initial[15],m1),0x3FFF
    return registers,writes,m1

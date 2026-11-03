"""Композиционный оракул шести шкал, геометрия задаётся формулами ранее проверенных детей."""
from CheckControlsSixRowGauge import inc_flags
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointMotion import block_cost

REQUESTS=(0x664A,0x665C,0x666B,0x667D,0x668E,0x669F)
POSITIONS=(0x49A1,0x49E1,0x5121,0x5181,0x51C1,0x49B9)
RETURNS=(0x6657,0x666A,0x6678,0x6689,0x669A,0x66D1)


def gauge(registers,value,address,emit):
    effective=((value+8)&248) if value and value&7==7 else value
    full=(effective>>3)&7
    rest=effective&7
    rounded=(((effective+8)&255)>>3)&7 if rest else full
    clear=max(6-rounded,0)
    patterns=[0xAA]*full+([0xAA & ((255 << (7-rest))&255)] if rest else [])+[0]*clear
    high,low=address>>8,address&255
    for column,pattern in enumerate(patterns):
        for row in range(6):emit(((high+row)<<8)|((low+column)&255),pattern)
    registers[6:8]=[high,(low+len(patterns))&255]
    registers[2:4]=[0,effective]
    if clear:
        registers[0:2]=[high,inc_flags((low+len(patterns)-1)&255)]
        registers[4:6]=[0,5]
    else:
        registers[0:2]=[rounded-6,sub8_flags(rounded,6)]
        pointer=0xE973+rest if rest else 0x05AA
        registers[4:6]=[pointer>>8,pointer&255]
    registers[16:18]=[high,inc_flags((low+full)&255)] if rest else [0,0x54]
    m1=block_cost(0xE8FD,0xE901)
    if value:
        m1+=block_cost(0xE901,0xE907)+block_cost(0xE90C,0xE913)
        if value&7==7:m1+=block_cost(0xE907,0xE90C)
    if full:m1+=block_cost(0xE913,0xE917)+full*block_cost(0xE917,0xE928)
    m1+=block_cost(0xE928,0xE92F)+block_cost(0xE949,0xE950)+block_cost(0xE952,0xE95A)
    if rest:m1+=block_cost(0xE92F,0xE949)+block_cost(0xE950,0xE952)
    if clear:m1+=block_cost(0xE95A,0xE961)+clear*block_cost(0xE961,0xE972)+1
    return m1


def reference(initial,requests,values,preferred,fallback,word,old):
    registers=list(initial)
    writes=[];ports=[]
    def emit(address,value):writes.append((5 if address<0x8000 else 2,address&0x3FFF,value))
    def wrapper(index,value):
        caller_return=RETURNS[index]
        emit(0xBFFD,caller_return>>8);emit(0xBFFC,caller_return&255)
        emit(0xBFFB,0x66);emit(0xBFFA,0x3F)
        emit(0xBFF9,registers[2]);emit(0xBFF8,registers[3])
        ports.append((0x7FFD,0x11))
        emit(0xBFFB,0x66);emit(0xBFFA,0x43)
        cost=gauge(registers,value,POSITIONS[index],emit)+20
        emit(0xBFFB,0x66);emit(0xBFFA,0x48)
        emit(0xBFF9,registers[2]);emit(0xBFF8,registers[3])
        ports.append((0x7FFD,0x10))
        registers[0]=0x10
        return cost
    m1=19
    for index,request in enumerate(requests):
        if not request:continue
        if index==1:
            # Выбор байта вместе с адресом, Carry читателя всегда нулевой, RRA даёт логическую половину.
            emit(0xBFFD,0x66);emit(0xBFFC,0x63)
            value=(preferred if preferred else fallback)>>1
            m1+=4+(4 if preferred else 7)+wrapper(index,value)
        elif index==5:
            emit(REQUESTS[index],0)
            magnitude=abs(word if word<0x8000 else word-0x10000)
            value=min(magnitude//4,46)
            m1+=23+(7 if word&0x8000 else 0)+(1 if magnitude>=1024 else 0)
            if magnitude<1024 and magnitude//4>=47:m1+=1
            m1+=wrapper(index,value)
        else:
            value=values[(0,2,3,4).index(index)]
            m1+=5+wrapper(index,value)
            emit(REQUESTS[index],0)
    if not requests[5]:registers[0:2]=[0,0x54]
    return registers,writes,ports,m1,(0x10 if ports else old)

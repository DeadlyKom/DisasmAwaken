"""AD5A, три разности арифметических половин, два усечённых квадрата и два исходных кода отношения."""
import math
from ReferenceActionCachedRoot import evaluate as cached_root
from ReferenceActionSignedRatioCode import evaluate as ratio_code
from CheckActionRecordIndex import add_flags
from CheckControlsComponentCompare import logical_flags


def signed(word):return word if word<32768 else word-65536
def half(word):return signed(word)//2


def evaluate(registers,ratio_table,root_table,return_address=0x3FFF):
    r=list(registers);stack=r[12];writes=[]
    pair=lambda index:r[index]*256+r[index+1]
    left0,right0,right1,left1,left2,right2=(pair(i) for i in (6,4,2,22,20,18))
    dx,dy,dz=half(left0)-half(right0),half(left1)-half(right1),half(left2)-half(right2)
    assert all(-32767<=value<=32767 for value in (dx,dy,dz))
    rawx,rawy,rawz=(value&65535 for value in (dx,dy,dz))
    high0=(dx*dx)>>16;high1=(dy*dy)>>16;root_input=high0+high1
    assert root_input<=0x7FFE
    root=math.isqrt(root_input)
    root_result=cached_root(root_input,high0,tuple(r[16:18]),root_table)
    assert root_result['af'][0]==root
    first=ratio_code(root<<8,rawz,ratio_table);second=ratio_code(rawy,rawx,ratio_table)
    first_signed=first['af'][0] if first['af'][0]<128 else first['af'][0]-256
    first_absolute=abs(first_signed)&255;first_saved=(first_absolute+128)&255

    def put_word(address,value):writes.extend(((address,value&255),(address+1,value>>8)))

    # Ожидаемая рамка первой разности и первого настоящего произведения.
    put_word(stack-2,pair(8));put_word(stack-4,rawx);put_word(stack-6,right1)
    put_word(stack-8,0xAD6E);put_word(stack-10,0x0044)
    # Временный перенос альтернативного HL и рамка второго произведения.
    put_word(stack-6,left1);put_word(stack-6,rawy);put_word(stack-8,high0)
    put_word(stack-10,0xAD86);put_word(stack-12,0x0044)
    # Настоящая банковая обёртка корня и два SelectMemoryPage с сохранением BC.
    multiplication_bc=(half(right1)&65535) if abs(dy)<256 else 0
    put_word(stack-8,0xAD8C);put_word(stack-10,multiplication_bc)
    put_word(stack-12,0xAD4E);put_word(stack-14,multiplication_bc)
    put_word(stack-12,0xAD51);put_word(stack-12,0xAD57);put_word(stack-14,root_result['bc'])
    # Рамка первой пары кодировщика, числитель содержит именно слово root*256 по модулю.
    put_word(stack-8,root<<8);put_word(stack-10,rawz);put_word(stack-8,0xADA4)
    sign=(root^((rawz>>8)&255))&255
    put_word(stack-10,(sign<<8)|logical_flags(sign));put_word(stack-12,rawz);put_word(stack-14,0xAE36)
    writes.extend(first['writes'])
    # Рамка второго кодировщика и сохранённого байта B, затем исходные POP BC и LD C,A.
    put_word(stack-4,(first_saved<<8)|add_flags(first_absolute,128));put_word(stack-6,0xADB2)
    sign=(rawy>>8)^(rawx>>8)
    put_word(stack-8,(sign<<8)|logical_flags(sign));put_word(stack-10,rawx);put_word(stack-12,0xAE36)
    writes.extend(second['writes'])
    r[0:2]=second['af'];r[2:4]=[first_saved,second['af'][0]]
    r[4:8]=[second['de']>>8,second['de']&255,second['hl']>>8,second['hl']&255]
    r[16:18]=second['alternate_af'];r[18:24]=[(half(right2)&65535)>>8,half(right2)&255,left1>>8,left1&255,rawz>>8,rawz&255]
    r[12],r[24]=stack+2,return_address
    return dict(registers=r,writes=writes,ports=[(0x7FFD,17),(0x7FFD,16)],
        deltas=(dx,dy,dz),root_input=root_input,root=root,first=first,second=second)

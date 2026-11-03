"""Композиционный числовой договор AF43 для проверки вызывающей обёртки."""
from CheckActionPatchedVector import adc16
from CheckActionScaledMultiply import signed
from CheckMusicGateTicks import xor_flags
from ReferenceControlsBufferPoints import sub16_flags


def evaluate(vector,matrix,old_outputs):
    outputs=list(old_outputs);m1=2;stop=False;performed=[]
    for row in range(3):
        partial=0
        for column in range(3):
            coefficient,value=matrix[row][column],vector[column]
            cv,vv=signed(coefficient,8),signed(value,16);factor=abs(cv)&127;product=factor*abs(vv);magnitude=product//128
            negative=bool((coefficient^(value>>8))&128);result=(-magnitude if negative else magnitude)&65535
            a=coefficient^(value>>8);f=sub16_flags(0,magnitude) if negative else xor_flags(a)
            de=magnitude if negative else abs(vv);upper=product>>15;previous=product>>16;carry=(product>>15)&1
            alt=(upper,(upper&0x28)|(64 if not upper else 0)|(16 if (previous&15)*2+carry>15 else 0))
            child=(35+factor.bit_length()-1+2*factor.bit_count() if factor else 32)+7*(vv<0)+2*(cv<0)+4*negative
            m1+=((5 if row==0 else 6) if column==0 else (6 if row==0 else 7))+child
            if column:
                result,f=adc16(result,partial,f&1);m1+=3
                if f&4:stop=True
            if stop:break
            if column<2:partial=result
        if stop:break
        outputs[row]=result;performed.append(row);m1+=1
    return dict(outputs=outputs,performed=performed,af=(a,f),alternate_af=alt,de=de,hl=result,
        refresh_m1=m1+4,overflow=stop)

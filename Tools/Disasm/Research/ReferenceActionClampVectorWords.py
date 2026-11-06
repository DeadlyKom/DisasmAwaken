"""Числовая модель 7F0E, исходный бит 23 управляет знаком результата."""
from ReferenceControlsPointRespawn import refresh


def logical_flags(value):return (value&0xA8)|(0x40 if value==0 else 0)|(4 if value.bit_count()%2==0 else 0)


def evaluate(registers,values,return_address=0x3FFF):
    r=list(registers);stack=r[12];magnitudes=[];negative=[];signed=[]
    # Расчёт полного модуля и точного порога исходного насыщения.
    for value in values:
        magnitude=min(value,(-value)&0xFFFFFFFF)
        magnitudes.append(magnitude if magnitude<0x8000 else 0x7F00)
        negative.append(bool(value&0x80000000));signed.append(bool(value&0x800000))
    result=[(-m)&65535 if sign else m for m,sign in zip(magnitudes,signed)]
    r[6:8]=[result[0]>>8,result[0]&255];r[4:6]=[result[1]>>8,result[1]&255];r[2:4]=[result[2]>>8,result[2]&255]
    source=(values[2]>>16)&255;flags=logical_flags(source)
    if signed[2]:
        r[0]=(magnitudes[2]>>8)^255;r[1]=(flags&~0x28)|0x12|(r[0]&0x28)
    else:r[0:2]=[source,flags]
    writes=[]
    # Создание реальных временных слов CPU-стека тремя CALL и двумя PUSH.
    for address,word in ((stack-2,0x7F17),(stack-2,magnitudes[0]),(stack-4,0x7F2B),
        (stack-4,magnitudes[1]),(stack-6,0x7F3F)):
        writes.extend(((address,word&255),(address+1,word>>8)))
    m1=48+20*sum(negative)+sum(min(v,(-v)&0xFFFFFFFF)>=0x8000 for v in values)+7*signed[0]+7*signed[1]+8*signed[2]
    r[15]=refresh(r[15],m1);r[12]=stack+2;r[24]=return_address
    return dict(registers=r,writes=writes,refresh_m1=m1,magnitudes=magnitudes,signs_from_bit23=signed)

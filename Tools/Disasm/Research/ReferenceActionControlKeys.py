"""Числовой договор накопления повтора и исходных знаковых переходов полного байтового домена."""
from CheckActionRecordIndex import add_flags
from ReferenceControlsPointRespawn import cp_flags,refresh


def evaluate(registers,layout,counter,value):
    start,name,tag,channel,direction,step,limit,own,opposite,latch,address=layout
    r=list(registers);total=counter+step;writes=[(latch,1),(own,total&255),(opposite,200)]
    r[0:2]=[200,add_flags(counter,step)];m1=8;written=False;forced=False
    if total>=256:
        # Расчёт исходного кандидата, переполнение знака приводит к исходной подстановке, а не насыщению.
        candidate=(value+direction)&255
        forced=bool(candidate&128) if direction>0 else not bool(candidate&128)
        if forced:candidate=1 if direction>0 else 255
        r[0:2]=[candidate,cp_flags(candidate,limit)];m1+=5+forced
        written=candidate<limit if direction>0 else candidate>=limit
        if written:writes.append((address,candidate));m1+=2
    r[15]=refresh(r[15],m1);r[12]+=2;r[24]=0x3FFF
    return dict(registers=r,writes=writes,refresh_m1=m1,overflow=total>=256,written=written,forced=forced)

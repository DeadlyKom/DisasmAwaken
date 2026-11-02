"""Возврат точки на границу с независимым расчётом двух чтений R по числу M1."""
from ReferenceControlsBufferPoints import sub8_flags


def cp_flags(a,b):
    return (sub8_flags(a,b)&~0x28) | (b&0x28)


def refresh(value,increment):
    return (value&128) | ((value+increment)&127)


def respawn(entry,phase,step,offset,initial_r):
    assert step
    phase ^= 1
    positive = phase == 0
    first = refresh(initial_r,7)
    quotient,remainder = divmod(first,step)
    capped = min(remainder,94)
    y = (capped+offset)&255 if positive else 95-capped
    second = refresh(first,4*quotient+(8 if positive else 10)+int(remainder>=94))
    low_x = positive if entry == 0xCE5D else not positive
    if low_x:
        x = max(second,1)
        flags = 0 if second == 0 else cp_flags(second,1)
        final_r = refresh(second,4+int(second==0))
    else:
        raw = (second+128)&255
        x = raw-1 if raw>=254 else raw
        flags = sub8_flags(raw,1) if raw>=254 else cp_flags(raw,254)
        final_r = refresh(second,5+int(raw>=254))
    return dict(phase=phase,y=y,x=x,flags=flags,r=final_r,first_r=first,second_r=second)

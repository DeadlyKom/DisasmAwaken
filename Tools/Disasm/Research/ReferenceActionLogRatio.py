"""Числовой эталон AE73 на точных таблицах двух доказанных генераторов."""
from CheckActionLogarithmTable import table_values as logarithms
from CheckActionExponentialTable import table_values as exponentials
from ReferenceControlsBufferPoints import sub8_flags,sub16_flags
from CheckControlsEvenSpan import and_flags
LOG=logarithms()[0]
EXP=exponentials()[0]


def normalize(word):
    high=word>>8;shift=min(7,high.bit_length())
    signed=word if word<32768 else word-65536;index=(signed>>shift)&255
    return LOG[index],shift


def evaluate(numerator,denominator):
    denominator_log,ds=normalize(denominator);denominator_log=(denominator_log+256*ds)&65535
    negative=bool(numerator&32768);magnitude=(-numerator)&65535 if negative else numerator
    sign_a=((~(numerator>>8))&255) if negative else ((numerator>>7)&254)
    sign_f=0x80|(sign_a&0x28)|int(negative)
    num_log,ns=normalize(magnitude);difference=(num_log+256*(8+ns)-denominator_log)&65535
    normalization=lambda s:6*s-int(s==7)
    m1=5+normalization(ds)+10+8*negative+5+normalization(ns)+10
    if difference&32768:
        a=num_log&255
        return dict(hl=0,de=denominator_log,bc=(8+ns)<<8,af=(a,and_flags(a)),
            alternate_af=(sign_a,sign_f),writes=[],refresh_m1=m1+3,path='log_underflow')
    exponent=difference>>8;fraction=difference&255;base=256+EXP[fraction];m1+=7
    if exponent>15:
        return dict(hl=base,de=denominator_log,bc=exponent<<8,
            af=((15-exponent)&255,sub8_flags(15,exponent)),alternate_af=(sign_a,sign_f),
            writes=[],refresh_m1=m1+3,path='overflow')
    if exponent<8:
        shift=exponent;shift_a=7-exponent;shift_f=sub8_flags(7,exponent)
        writes=[(0xAF14,shift_a)];m1+=7+shift
    else:
        shift=exponent-8;shift_a=15-exponent;shift_f=sub8_flags(15,exponent)
        writes=[(0xAF2F,shift_a)];m1+=5+shift
    # Вычисление флагов последнего удвоения, флаги S/Z/PV сохраняются от SUB выбора числа сдвигов.
    expanded=base<<shift
    if shift:
        previous=base<<(shift-1)
        shift_f=(shift_f&0xC4)|((expanded>>8)&0x28)|(16 if (previous&4095)*2>4095 else 0)|int(expanded>65535)
    result=expanded>>8 if exponent<8 else expanded
    a=sign_a
    if negative:a=(~(result>>8))&255;result=(-result)&65535
    m1+=4+7*negative
    return dict(hl=result,de=denominator_log,bc=exponent<<8,af=(a,and_flags(a)),
        alternate_af=(shift_a,shift_f),writes=writes,refresh_m1=m1,path='negative' if negative else 'positive')

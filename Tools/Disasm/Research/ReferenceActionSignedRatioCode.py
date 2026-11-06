"""AE24, исходный табличный код знакового отношения, без подмены обычным atan2."""
from ReferenceActionLogRatio import evaluate as divide
from CheckControlsComponentCompare import logical_flags
from CheckActionRecordIndex import add_flags


def evaluate(numerator,denominator,table):
    sign_byte=(numerator>>8)^(denominator>>8);sign_negative=bool(sign_byte&128)
    negative_denominator=bool(denominator&32768)
    magnitude=(-denominator)&65535 if negative_denominator else denominator
    child=divide(numerator,magnitude)
    extra=7+7*negative_denominator+1+2
    if child['af'][1]&1:
        return dict(hl=child['hl'],de=child['de'],bc=denominator,
            af=(192 if sign_negative else 64,logical_flags(sign_byte)),alternate_af=child['alternate_af'],
            writes=child['writes'],refresh_m1=child['refresh_m1']+extra+3+2*sign_negative,
            path='divider_overflow',table_index=None,child=child)
    negative_ratio=bool(child['hl']&32768)
    absolute=(-child['hl'])&65535 if negative_ratio else child['hl']
    index=absolute>>4;extra+=3+7*negative_ratio+17
    if index>=256:
        return dict(hl=index,de=child['de'],bc=denominator,
            af=(192 if sign_negative else 64,logical_flags(sign_byte)),alternate_af=child['alternate_af'],
            writes=child['writes'],refresh_m1=child['refresh_m1']+extra+3+2*sign_negative,
            path='shifted_range_reject',table_index=None,child=child)
    code=table[index];high=denominator>>8;extra+=4
    if not sign_negative:
        extra+=3
        if negative_denominator:
            flags=add_flags(code,128);code=(code+128)&255;extra+=2;path='quadrant_2'
        else:flags=0x54|(high&0x28);path='quadrant_0'
    else:
        code=(code+64)&255;extra+=4
        if negative_denominator:flags=0x90|(high&0x28);path='quadrant_1'
        else:flags=add_flags(code,128);code=(code+128)&255;extra+=2;path='quadrant_3'
    return dict(hl=0x9A00|index,de=child['de'],bc=denominator,af=(code,flags),alternate_af=child['alternate_af'],
        writes=child['writes'],refresh_m1=child['refresh_m1']+extra,path=path,table_index=index,child=child)

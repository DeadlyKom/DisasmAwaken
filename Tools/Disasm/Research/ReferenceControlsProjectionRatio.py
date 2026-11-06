"""Полные числовые ветви отношения, включая исходное округление внешней области и снятие внешнего CALL."""
from CheckControlsRatioInside import reference as inside,divide_fraction


def evaluate(numerator,divisor,coordinate):
    assert 0<=numerator<=0x7FFFFF and 0<=divisor<=0x7FFFFF and coordinate in (2,3)
    if numerator<=divisor:
        result=inside(numerator,divisor)
        return dict(result,flag_mask=1<<(5-coordinate),reject=False,sp_delta=2,
            branch='inside_tiny' if divisor<2 else 'inside')
    # Нормализация по старшему разряду числителя, исходный код имеет три разных пути переноса младших байтов.
    if numerator>=65536:
        shift=25-numerator.bit_length();scaled_q=divisor<<shift
        n_word=((numerator<<(shift-1))>>8)&65535
        q_word=(scaled_q>>8)&65535;carry=bool(scaled_q&0x1000000)
        low_n=(numerator<<shift)&255;low_q=scaled_q&255;branch='outside24'
    elif numerator>=256:
        shift=17-numerator.bit_length();previous_q=(divisor<<(shift-1))&65535
        n_word=(numerator<<(shift-1))&65535
        q_word=((previous_q<<1)|((divisor&255)>>7))&65535;carry=bool(previous_q&32768)
        low_n=numerator&255;low_q=(2*divisor)&255;branch='outside16'
    else:
        shift=9-numerator.bit_length();previous_q=(divisor<<(shift-1))&255
        n_word=((numerator<<(shift-1))&255)<<8
        q_word=(((previous_q<<1)&255)<<8)|((divisor&255)>>7);carry=bool(previous_q&128)
        low_n=numerator&255;low_q=(2*divisor)&255;branch='outside8'
    # Проверка исходного сравнения усечённых слов, равенство тоже снимает адрес внутреннего CALL.
    if not carry and n_word>=q_word:
        return dict(hl=n_word,de=q_word,bc=(low_q<<8)|low_n,a=0,f=0x44,
            flag_mask=0,reject=True,sp_delta=4,branch=branch+'_reject')
    # Расчёт исходного скорректированного слова, SCF/RR D изменяет только старший байт, E не вращается.
    denominator_byte=128|((q_word>>8)>>1)
    adjusted_q=(denominator_byte<<8)|(q_word&255)
    difference=(n_word-adjusted_q)&65535
    quotient,remainder,flags=divide_fraction(difference>>8,denominator_byte)
    return dict(hl=difference,de=quotient<<8,bc=(denominator_byte<<8)|low_n,a=remainder,f=flags,
        flag_mask=0,reject=False,sp_delta=2,branch=branch)

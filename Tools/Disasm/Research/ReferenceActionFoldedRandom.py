"""Числовая формула трёхбайтового состояния, без переноса последовательности Z80-команд."""
def step(word,fold):
    previous=(word-1)&65535
    mixed=(8*word&65535)+(64*previous&65535)+3*word
    low=mixed&65535
    carry_fold=(fold+(previous>>10).bit_count()+(mixed>>16))&255
    difference=carry_fold*256+(low>>8)-(low&255)
    temporary=difference&65535
    first_high=(carry_fold-(difference<0))&255
    borrow=low<temporary
    high=(first_high-borrow)&255
    result=(low-temporary-1)&65535
    # Расчёт всех флагов последнего SBC A,0, DEC HL уже не меняет AF.
    flags=2|(high&0xA8)|(0x40 if high==0 else 0)|(0x10 if (first_high&15)<borrow else 0)
    flags|=4 if first_high==128 and borrow else 0
    flags|=int(first_high<borrow)
    return dict(word=result,fold=high,flags=flags,temporary=temporary,mixed_low=low,folded_carries=carry_fold)

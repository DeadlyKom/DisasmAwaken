"""Исходное табличное приближение и вычитание нечётных разностей, включая особый верх таблиц."""


def add_word(left,right,flags):
    total=left+right;value=total&65535
    return value,(flags&0xC4)|((value>>8)&0x28)|(16 if (left&4095)+(right&4095)>4095 else 0)|int(total>65535)


def increment(value,flags):
    following=(value+1)&255
    return following,(following&0xA8)|(64 if not following else 0)|(16 if value&15==15 else 0)|(
        4 if value==127 else 0)|(flags&1)


def evaluate(value,initial_hl,initial_alternate_af,table):
    if value<256:
        a=0;flags=0x44;hl=value;bc=65535;m1=6
        for step in range(15):
            hl,flags=add_word(hl,bc,flags);m1+=2
            if not flags&1:break
            a,flags=increment(a,flags);m1+=1
            if step==14:m1+=1;break
            bc=(bc-2)&65535;m1+=2
        return dict(af=(a,flags),hl=hl,de=initial_hl,bc=bc,alternate_af=initial_alternate_af,refresh_m1=m1)
    index=value>>8;initial=table[index];base=table[256+index]+256*table[512+index]
    a=initial^255;flags=0x92|(a&0x28)
    bc=(2*((0xFF00|initial)+1)-1)&65535
    alternate_af=(base&255,0x80|int(initial!=255))
    hl,flags=add_word(base,value,flags);m1=23
    for step in range(6):
        hl,flags=add_word(hl,bc,flags);m1+=2
        if not flags&1:break
        if step==5:
            a,flags=increment(a,flags);m1+=2;break
        bc=(bc-2)&65535;m1+=2;a,flags=increment(a,flags);m1+=1
    return dict(af=(a,flags),hl=hl,de=value,bc=bc,alternate_af=alternate_af,refresh_m1=m1)

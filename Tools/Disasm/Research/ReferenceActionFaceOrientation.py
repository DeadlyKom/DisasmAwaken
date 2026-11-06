"""Композиционный числовой эталон ориентации, сохраняющий заёмы и исключение 8000 умножителя."""
from CheckSignedMultiply import signed,sbc16_flags
from CheckActionVertexCodes import logic_flags


def multiply(left,right,bc,ix):
    mx,my=abs(signed(left)),abs(signed(right))
    wide=mx>=256 and my>=256
    magnitude=mx*(256 if wide and right==32768 else my)
    negative=bool((left^right)&32768)
    value=(-magnitude if negative else magnitude)&0xFFFFFFFF
    a=(left>>8)^(right>>8)
    f=sbc16_flags(0,magnitude>>16,int(bool(magnitude&65535))) if negative else logic_flags(a)
    out_bc=magnitude>>16 if negative else 0 if wide else bc if mx<256 and my<256 else bc&0xFF00
    return dict(high=value>>16,low=value&65535,af=(a,f),bc=out_bc,ix=magnitude&65535 if wide else ix,wide=wide,
        defect=wide and right==32768,stack_af=(a,logic_flags(a)))


def face(points,count,ix):
    p0,p1,p2=(points[i] for i in ((0,1,2) if count<5 else (0,2,4)))
    x0,y0=p0;x1,y1=p1;x2,y2=p2
    # Расчёт четырёх исходных SBC, заём каждого передаётся следующему даже между осями.
    def subtract(left,right,carry):return (left-right-carry)&65535,int(left-right-carry<0)
    u_first,carry=subtract(y2,y0,int(count<5))
    v_first,carry=subtract(y1,y0,carry)
    u_second,carry=subtract(x2,x0,carry)
    v_second,carry=subtract(x1,x0,carry)
    first=multiply(v_second,u_first,y0,ix)
    second=multiply(v_first,u_second,x0,first['ix'])
    low=(second['low']-first['low']-(second['af'][1]&1))&65535
    borrow=int(second['low']-first['low']-(second['af'][1]&1)<0)
    flags=sbc16_flags(second['high'],first['high'],borrow)
    return dict(first=first,second=second,low=low,af=(second['af'][0],flags),ix=second['ix'],
        v_second=v_second,v_first=v_first,selected=(p0,p1,p2))

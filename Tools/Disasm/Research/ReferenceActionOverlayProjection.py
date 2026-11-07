"""ADC5, числовая проекция с произвольным внешним SP и независимым подсчётом M1."""
from CheckActionOverlayProjection import reference
from ReferenceActionLogRatio import evaluate as ratio
from ReferenceControlsPointRespawn import refresh


def evaluate(registers,return_address=0x3FFF):
    r=list(registers);stack=r[12];horizontal=r[2]*256+r[3];depth=r[4]*256+r[5];vertical=r[6]*256+r[7]
    result=reference(horizontal,vertical,depth);negative=bool(depth&32768)
    denominator=(-depth)&65535 if negative else depth;first=ratio(vertical,denominator)
    cost=12+7*negative+first['refresh_m1']
    if not first['af'][1]&1:
        second=ratio(horizontal,denominator)
        cost=(28+21*negative if second['af'][1]&1 else 32+28*negative)+first['refresh_m1']+second['refresh_m1']
    for position,name in ((6,'hl'),(4,'de'),(2,'bc')):
        word=result[name];r[position:position+2]=[word>>8,word&255]
    r[0:2],r[16:18]=result['af'],result['alternate_af']
    writes=[(address+stack-0xBFFE if 0xBFF8<=address<=0xBFFD else address,value) for address,value in result['writes']]
    r[12],r[15],r[24]=stack+2,refresh(r[15],cost),return_address
    return dict(registers=r,writes=writes,path=result['path'],refresh_m1=cost)

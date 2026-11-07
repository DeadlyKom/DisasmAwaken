"""EC54, два кода границ, локальные маркеры и OR только обычных записей."""
from CheckActionVertexCodes import code,logic_flags
from ReferenceControlsPointRespawn import cp_flags,refresh


def evaluate(registers,points,return_address=0x3FFF):
    r=list(registers);writes=[];aggregate=0;cost=6;outcomes=[];side=0
    for index,(second,first) in enumerate(points):
        sh,fh=second>>8,first>>8
        if sh==128:
            value=side=0;cost+=14;outcomes.append('marker')
        else:
            side,value=code(second,first);aggregate|=value
            second_cost=11 if 0<sh<128 else 10
            first_cost=6 if fh else 11 if first>=96 else 10
            cost+=second_cost+first_cost+17;outcomes.append('ordinary')
        writes.append((0x8E04+5*index,value))
    r[0:2]=[aggregate,logic_flags(aggregate)];r[16:18]=[10,cp_flags(10,10)]
    r[2:4]=[10,side];r[6:8]=[0x8E,11]
    r[12]+=2;r[15]=refresh(r[15],cost);r[24]=return_address
    return dict(registers=r,writes=writes,refresh_m1=cost,outcomes=outcomes)

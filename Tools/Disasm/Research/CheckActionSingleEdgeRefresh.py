"""Полный C941, точные M1 и R вместе с реальными Case-путями.

Документация: ../../../Docs/ActionSingleEdge.md#точный-r-полного-одиночного-ребра
"""
from collections import Counter
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from InspectZ80 import decoder
from ReferenceActionClipping import Clipping


def main(unconditional_branch=False):
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    if unconditional_branch:base[0][0xC94B-0xC000]=0x18
    m=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);s=Simulator(m)
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    counts=Counter();touched=set();maximum=0
    def check(first,second,seen):
        nonlocal touched,maximum
        m.recording=False
        for bank,index in touched:m.banks[bank][index]=base[bank][index]
        for address,(x,y) in ((0xCF0B,first),(0xCF1B,second)):
            code=(2 if x<0 else 1 if x>255 else 0)|(8 if y<0 else 4 if y>95 else 0)
            data=(x&65535).to_bytes(2,'little')+(y&65535).to_bytes(2,'little')+bytes((((code^15)<<4)|code,))
            for i,value in enumerate(data):m[address+i]=value
        m[0xCF07]=seen;m[0x9BA3]=0xA5;m[0xCF03]=0x5A;m[0xBFFE],m[0xBFFF]=255,63
        serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':(serial*73)&65535,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':0xC941},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*73&255,serial&1,serial%3
        oracle=Clipping(m.banks,initial,ops,PC,SP);oracle.single_edge()
        s.registers[:]=initial;m.writes=[];m.recording=True
        measured_m1=0
        for _ in range(2000):
            if s.registers[PC]==0x3FFF:break
            before=s.registers[15];s.run();increment=(s.registers[15]-before)&127
            assert increment in (1,2);measured_m1+=increment
        else:raise AssertionError('возврат одиночного ребра')
        assert measured_m1==oracle.refresh_m1,(first,second,seen,measured_m1,oracle.refresh_m1)
        m.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(oracle.r[i]==s.registers[i] for i in compared),(first,second,seen,[(i,oracle.r[i],s.registers[i]) for i in compared if oracle.r[i]!=s.registers[i]])
        assert all(a==b for a,b in zip(oracle.banks,m.banks)),('RAM',first,second,seen)
        assert Counter(oracle.writes)==Counter(m.writes),('write multiplicity',first,second,seen)
        touched={(bank,index) for bank,index,value in m.writes}
        counts['special' if oracle.special else 'normal']+=1;maximum=max(maximum,m[0x9BA3])
    # Проверка всех девяти зон и полного байта прежних отметок, в том числе перестановки внутренней точки.
    representatives=[(x,y) for x in (-64,7,319) for y in (-64,11,159)]
    for first in representatives:
        for second in representatives:
            for seen in range(256):check(first,second,seen)
    rng=random.Random(0xC941)
    for _ in range(4096):check(tuple(rng.randrange(-512,768) for _ in range(2)),tuple(rng.randrange(-512,768) for _ in range(2)),rng.randrange(256))
    report=dict(passed=True,total_cases=counts.total(),exits=dict(counts),maximum_output_bytes_in_series=maximum,
        all_zone_pairs_and_corner_bytes=True,inside_first_swap_checked=not unconditional_branch,inside_first_swap_suppressed=unconditional_branch,corner_block_forced_to_one=True,
        all_final_registers_including_R_proved=True,full_M1_count_compared=True,exact_T_claimed=False,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        real_helpers_without_stubs=True,unconditional_C94B_branch=unconditional_branch,independent_geometry_proof=False,all_joint_inputs_exhausted=False,
        refresh_and_timing_independently_checked=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/('Tools/Disasm/Reports/ActionSingleEdgeUnconditionalRefreshVerification.json' if unconditional_branch else 'Tools/Disasm/Reports/ActionSingleEdgeRefreshVerification.json')).write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

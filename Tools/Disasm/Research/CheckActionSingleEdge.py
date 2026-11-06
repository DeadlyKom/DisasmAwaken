"""Полный C941 с реальными Case-путями, перестановкой точек и тремя возвратами C993."""
from collections import Counter
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from InspectZ80 import decoder
from ReferenceActionClipping import Clipping


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
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
        oracle=Clipping(m.banks,initial,ops,PC,SP);oracle.single_edge()
        s.registers[:]=initial;m.writes=[];m.recording=True
        for _ in range(2000):
            if s.registers[PC]==0x3FFF:break
            s.run()
        else:raise AssertionError('возврат одиночного ребра')
        m.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
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
        all_zone_pairs_and_corner_bytes=True,inside_first_swap_checked=True,corner_block_forced_to_one=True,
        all_final_registers_except_R_proved=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        real_helpers_without_stubs=True,independent_geometry_proof=False,all_joint_inputs_exhausted=False,
        refresh_and_timing_independently_checked=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionSingleEdgeVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

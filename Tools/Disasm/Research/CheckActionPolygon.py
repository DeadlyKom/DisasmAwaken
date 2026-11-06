"""Полный C000, настоящие обработчики, все выходные регистры кроме R, вся RAM и стековые записи."""
from collections import Counter
from itertools import product
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from InspectZ80 import decoder
from ReferenceActionPolygon import Polygon


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);s=Simulator(m)
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    touched=set();counts=Counter();maximum=0
    def check(points,low_counter=0x9C,pointer=0xA000):
        nonlocal touched,maximum
        m.recording=False
        for bank,index in touched:m.banks[bank][index]=base[bank][index]
        for i,(x,y) in enumerate(points):
            code=(2 if x<0 else 1 if x>255 else 0)|(8 if y<0 else 4 if y>95 else 0)
            data=(x&65535).to_bytes(2,'little')+(y&65535).to_bytes(2,'little')+bytes((((code^15)<<4)|code,))
            for j,value in enumerate(data):m[0x8E00+5*i+j]=value
            m[pointer+i]=5*i
        m[0xBFFE],m[0xBFFF]=255,63
        initial=get_registers({'AF':counts.total()&65535,'HL':pointer,'DE':0x2468,'BC':len(points)*256+low_counter,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':0xC000},None,False)
        oracle=Polygon(m.banks,initial,ops,PC,SP);oracle.polygon()
        s.registers[:]=initial;m.writes=[];m.recording=True
        for _ in range(20000):
            if s.registers[PC]==0x3FFF:break
            s.run()
        else:raise AssertionError('возврат полигона')
        m.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(oracle.r[i]==s.registers[i] for i in compared),(points,low_counter,pointer,[(i,oracle.r[i],s.registers[i]) for i in compared if oracle.r[i]!=s.registers[i]])
        assert all(a==b for a,b in zip(oracle.banks,m.banks)),('RAM',points)
        assert Counter(oracle.writes)==Counter(m.writes),('write multiplicity',points,Counter(oracle.writes)-Counter(m.writes),Counter(m.writes)-Counter(oracle.writes))
        touched={(bank,index) for bank,index,value in m.writes}
        counts['special' if oracle.special else 'normal']+=1;maximum=max(maximum,m[0x9BA3])
    # Проверка замыкания контуров на представителях всех девяти зон, включая одиночную вершину и вырожденные рёбра.
    representatives=[(x,y) for x in (-64,7,319) for y in (-64,11,159)]
    for n in (1,2,3):
        for points in product(representatives,repeat=n):check(points)
    # Проверка числа вершин 1..15, обычного и специального завершения, смешанных пересечений.
    rng=random.Random(0xC000)
    for n in range(1,16):
        for _ in range(256):check([tuple(rng.randrange(-512,768) for _ in range(2)) for _ in range(n)],rng.randrange(256))
    # Проверка младшего C и входного списка, пересекающего границу страницы, без выбора новых областей в игре.
    for low in range(256):
        check(((0,0),(255,95),(256,96)),low,0xA0FE)
        check(((-1,47),(511,96),(127,0)),low,0xA0FE)
    report=dict(passed=True,total_cases=counts.total(),exits=dict(counts),maximum_output_bytes_in_series=maximum,
        counts_1_to_15=True,all_zone_sequences_up_to_three_vertices=True,all_low_counter_bytes=True,
        real_handlers_without_stubs=True,all_final_registers_except_R_proved=True,all_physical_ram_bytes_proved=True,
        write_multiplicity_proved=True,closed_contour_last_to_first=True,normal_and_special_stack_frames_checked=True,
        independent_geometry_proof=False,all_joint_inputs_exhausted=False,refresh_and_timing_independently_checked=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPolygonVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

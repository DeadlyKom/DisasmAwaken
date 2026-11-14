"""Полный C000, настоящие обработчики, все выходные регистры кроме R, вся RAM и стековые записи."""
from collections import Counter
from itertools import product
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from InspectZ80 import decoder
from ReferenceActionPolygon import Polygon
from ReferenceControlsPointRespawn import cp_flags
from CheckActionApproachWord import ReadOnlyFixture
from ReferenceActionClipping import PRODUCT,CACHED,DELTA,CORNERS


def check_immediate_end():
    """Приватная рамка ContinueClipPolygon с сохранённым B=1, без обхода рёбер."""
    memory=ReadOnlyFixture(flat_action())
    simulator=Simulator(memory)
    initial=get_registers({'AF':0x1357,'HL':0x2468,'DE':0x369C,'BC':0x47AD,
        '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
        'IX':0xABCD,'IY':0x5C3A,'SP':0xBFF0,'PC':0xC071},None,False)
    cases=0
    # Проверка всех размеров и сохранённых C, включая размеры вне обычного игрового диапазона.
    for size in range(256):
        for low in range(256):
            final_pointer=(0xA0FE+size+low)&65535
            # Подготовка синтетической трёхсловной рамки только в фикстуре модели.
            frame=(0x0100+low,final_pointer,0x3FFF)
            for index,word in enumerate(frame):
                list.__setitem__(memory,0xBFF0+2*index,word&255)
                list.__setitem__(memory,0xBFF1+2*index,word>>8)
            list.__setitem__(memory,0x9BA3,size)
            initial[14],initial[15],initial[27]=size,low,size%3
            wanted=list(initial)
            wanted[0:2]=[size,cp_flags(size,6)]
            wanted[2:4]=[0,low]
            wanted[6:8]=[final_pointer>>8,final_pointer&255]
            wanted[15]=(low&128)|((low+6)&127)
            wanted[PC],wanted[SP]=0x3FFF,0xBFF6
            simulator.registers[:]=initial
            # Проверка точного пути из шести M1, каждая инструкция даёт одно чтение M1.
            for pc in (0xC071,0xC072,0xC074,0xC075,0xC078,0xC07A):
                assert simulator.registers[PC]==pc,(size,low,pc,simulator.registers[PC])
                simulator.run()
            compared=(*range(24),PC,26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(size,low)
            cases+=1
    return dict(passed=True,total_cases=cases,all_output_sizes_and_saved_C=True,
                saved_B=1,synthetic_private_frame=True,full_game_execution=False,
                exact_registers_flags_r_sp=True,m1_increment=6,any_memory_write_rejected=True,
                loop_branch_proved_by_this_series=False,assembly_executed=False,
                irq_executed=False,native_execution=False)


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);s=Simulator(m)
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    touched=set();counts=Counter();maximum=0;edge_observations=Counter()
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
        edge=None;last_edge_context=None
        for _ in range(20000):
            if s.registers[PC]==0x3FFF:break
            pc=s.registers[PC]
            # Проверка контекста сразу перед косвенным входом каждого обработчика ребра.
            if pc==0xC070:
                assert edge is None
                assert s.registers[4:6]==[0xC0,0x71]
                edge=dict(af_alt=s.registers[16:18],ix=s.registers[8:10],
                          division=False,wide_multiply=False,de_writer=False)
                edge_observations['entered']+=1
            # Учёт реально достигнутых помощников, их тела продолжают исполняться без подмены.
            if edge is not None:
                if pc==0xC88C:edge['division']=True
                if pc==0xC6F4:
                    def magnitude(index):
                        word=256*s.registers[index]+s.registers[index+1]
                        return abs(word-65536 if word&32768 else word)
                    edge['wide_multiply']|=magnitude(6)>=256 and magnitude(4)>=256
                if pc in PRODUCT or pc in CACHED or pc in DELTA or pc==0xC6D3:
                    edge['de_writer']=True
                if pc in CORNERS and m[0xCF03]==0:edge['de_writer']=True
            # Проверка сохранения контекста у обычного и специального выхода из ребра.
            if pc in (0xC071,0xC6EA):
                assert edge is not None
                if not edge['division']:
                    assert s.registers[16:18]==edge['af_alt'],('AF без деления',points)
                    edge_observations['no_division_preserves_AF_alt']+=1
                    if edge['af_alt']!=initial[16:18]:
                        edge_observations['no_division_preserves_earlier_edge_AF_alt']+=1
                if not edge['wide_multiply']:
                    assert s.registers[8]==edge['ix'][0],('IXH без полного умножения',points)
                    edge_observations['no_wide_multiply_preserves_IXH']+=1
                    if edge['ix'][0]!=initial[8]:
                        edge_observations['no_wide_multiply_preserves_earlier_edge_IXH']+=1
                    if not edge['division']:
                        assert s.registers[8:10]==edge['ix'],('IX без умножения и деления',points)
                        edge_observations['no_wide_multiply_or_division_preserves_IX']+=1
                if not edge['de_writer']:
                    assert s.registers[4:6]==[0xC0,0x71],('DE без писателя',points)
                    edge_observations['no_DE_writer_returns_C071']+=1
                last_edge_context=tuple(s.registers[i] for i in (4,5,8,9,16,17))
                edge_observations['special' if pc==0xC6EA else 'normal']+=1
                edge=None
            s.run()
        else:raise AssertionError('возврат полигона')
        m.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(oracle.r[i]==s.registers[i] for i in compared),(points,low_counter,pointer,[(i,oracle.r[i],s.registers[i]) for i in compared if oracle.r[i]!=s.registers[i]])
        assert all(a==b for a,b in zip(oracle.banks,m.banks)),('RAM',points)
        assert Counter(oracle.writes)==Counter(m.writes),('write multiplicity',points,Counter(oracle.writes)-Counter(m.writes),Counter(m.writes)-Counter(oracle.writes))
        assert edge is None and last_edge_context is not None
        assert tuple(s.registers[i] for i in (4,5,8,9,16,17))==last_edge_context
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
        assembly_executed=False,irq_executed=False,native_execution=False,
        immediate_continue_clip_polygon_end=check_immediate_end(),
        actual_edge_context_invariants=dict(edge_observations))
    (ROOT/'Tools/Disasm/Reports/ActionPolygonVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

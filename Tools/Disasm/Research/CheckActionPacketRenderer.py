"""Полный рисователь DD23 с настоящими детьми, сравнение композиционного эталона всех регистров и RAM."""
from collections import Counter
import json,math,random
from itertools import combinations
from CheckPreviewPolygon import hull
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceActionPacketRenderer import PacketRenderer


def main(clipped=False):
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);sim=Simulator(memory);counts=Counter()
    entry=0xDBBD if clipped else 0xDD23
    events=Counter()
    ops={}
    if clipped:
        from InspectZ80 import decoder
        ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}

    def check(records,points,gate=0,profile='mixed',codes=None):
        memory.recording=False
        for bank in (0,2):memory.banks[bank][:]=base[bank]
        serial=counts.total();source=bytes((i*37+serial*11)&255 for i in range(3072))
        memory.banks[2][:3072]=source
        stream=bytes(v for header,indices in records for v in (header,*indices))+bytes((0,))
        pointer=(0xA000,0xA0FE,0x9FFE)[serial%3]
        for i,value in enumerate(stream):memory[pointer+i]=value
        for i,(x,y) in enumerate(points):
            region=(2 if x<0 else 1 if x>255 else 0)|(8 if y<0 else 4 if y>95 else 0)
            code=(((region^15)<<4)|region) if codes is None else codes[i]
            for j,value in enumerate((x&255,(x>>8)&255,y&255,(y>>8)&255,code)):memory[0x8E00+5*i+j]=value
        memory[0x8D5A]=gate;memory[0xBFFE],memory[0xBFFF]=255,63
        initial=get_registers({'AF':serial&65535,'HL':pointer,'DE':0x2468,'BC':0x369C,
            'IX':0xABCD,'IY':0x5C3A,'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[26],initial[27]=serial&255,serial&1,serial%3
        oracle=PacketRenderer(memory.banks,initial,ops,PC,SP);oracle.render(clipped=clipped)
        events.update(oracle.events)
        sim.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(250000):
            if sim.registers[PC]==0x3FFF:break
            sim.run()
        else:raise AssertionError(('возврат рисователя',hex(entry)))
        memory.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(oracle.r[i]==sim.registers[i] for i in compared),(records,profile,'registers',[(i,oracle.r[i],sim.registers[i]) for i in compared if oracle.r[i]!=sim.registers[i]])
        assert all(a==b for a,b in zip(oracle.banks,memory.banks)),(records,profile,'RAM')
        assert Counter(oracle.writes)==Counter(memory.writes),(records,profile,'writes',Counter(oracle.writes)-Counter(memory.writes),Counter(memory.writes)-Counter(oracle.writes))
        # Проверка общего выхода напрямую по структуре потока, независимо от композиционного эталона.
        end=pointer+len(stream)-1
        assert (sim.registers[6]<<8|sim.registers[7])==end
        assert sim.registers[0:2]==[0,0x54] and sim.registers[SP]==0xC000
        if not records:
            # Проверка пустого потока, дочерние процедуры не должны менять контекст или RAM.
            assert all(sim.registers[i]==initial[i] for i in (*range(2,12),14,*range(16,24),26,27))
            assert memory.writes==[]
        elif len(records)==1 and records[0][0]&128:
            header,indices=records[0];count=header&15
            if header&64 and gate:
                # Проверка полного пропуска связанной ломаной, SkipRecord оставляет BC равным count+1.
                assert sim.registers[2:4]==[0,count+1]
                assert all(sim.registers[i]==initial[i] for i in (*range(4,6),*range(8,12),*range(16,24)))
                assert memory.writes==[]
            else:
                # Проверка восстановления счётчика после последнего сегмента и сохранённого младшего C.
                assert sim.registers[2:4]==[0,initial[3]]
                if clipped:
                    # Проверка полного последнего конца, включая сегменты, отвергнутые до растеризации.
                    assert sim.registers[8:10]==[0x8E,indices[-1]]
                    x,y=points[indices[-1]//5]
                    for address,value in ((0x8D3E,x),(0x8D4A,y)):
                        assert memory[address]|memory[address+1]<<8==value&65535
                    index=indices[-1]//5
                    region=(2 if x<0 else 1 if x>255 else 0)|(8 if y<0 else 4 if y>95 else 0)
                    expected_code=(((region^15)<<4)|region) if codes is None else codes[index]
                    assert memory[0x8D4D]==expected_code
        counts[profile]+=1

    # Проверка обеих ориентаций выпуклых контуров, всех штатных материалов и счётчиков до 15.
    for number in range(3,16):
        points=[(128+round(80*math.cos(2*math.pi*i/number)),48+round(35*math.sin(2*math.pi*i/number))) for i in range(number)]
        for reverse in (False,True):
            indices=list(range(0,5*number,5));indices=indices[::-1] if reverse else indices
            for mode in range(5):check([(mode*16+number,indices)],points,profile='faces')
    # Проверка четырёх селекторов линий, связи с предыдущей гранью и сохранённого начального состояния.
    points=[(i*17,8+(i*29)%80) for i in range(15)]
    for number in range(2,16):
        for mode in range(4):
            for attached in (0,64):
                for gate in (0,1,255):check([(128+attached+mode*16+number,list(range(0,number*5,5)))],points,gate,'lines')
    # Проверка крайних координат всего окна и плоских исходных граней на каждой строке.
    boundary=[(0,0),(255,0),(255,95),(0,95)]
    for shift in range(4):
        for reverse in (False,True):
            indices=list(range(0,20,5));indices=indices[shift:]+indices[:shift]
            if reverse:indices=indices[::-1]
            for mode in range(5):check([(mode*16+4,indices)],boundary,profile='boundary_faces')
    for row in range(96):
        for mode in range(5):check([(mode*16+3,[0,5,10])],[(0,row),(127,row),(255,row)],profile='flat_faces')
    # Проверка всех 40 штатных слотов и пар равных, соседних и встречных концов.
    points=[((i*37)&255,(i*19)%96) for i in range(40)]
    for index in range(40):
        for other in (index,(index+1)%40,39-index):
            for mode in range(4):check([(128+mode*16+2,[5*index,5*other])],points,profile='all_40_point_slots')
    # Проверка составных потоков, нулевого конца и повторного использования результатов детей.
    points=[(32,16),(224,16),(224,80),(32,80),(128,4),(250,48),(128,92),(6,48)]
    rng=random.Random(0xDD23)
    for _ in range(128):
        records=[]
        for i in range(rng.randrange(1,6)):
            if rng.randrange(2):
                indices=[0,5,10,15];indices=indices[::-1] if rng.randrange(2) else indices
                records.append((rng.randrange(5)*16+4,indices))
            else:
                indices=[rng.randrange(8)*5 for _ in range(rng.randrange(2,8))]
                records.append((128+rng.randrange(2)*64+rng.randrange(4)*16+len(indices),indices))
        check(records,points,rng.randrange(2),'mixed')
    for gate in range(256):check([],points,gate,'empty')
    if clipped:
        # Проверка общих внешних границ, отсечения прямоугольников и обоих обходов граней.
        for x0,x1 in ((-64,-1),(-64,64),(-64,319),(0,255),(64,319),(256,319),(0,0),(255,255)):
            for y0,y1 in ((-40,-1),(-40,32),(-40,135),(0,95),(32,135),(96,135)):
                for reverse in (False,True):
                    indices=[0,5,10,15];indices=indices[::-1] if reverse else indices
                    for mode in range(5):check([(mode*16+4,indices)],[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],profile='clipped_rectangles')
        # Проверка всех пар девяти областей для одиночных сегментов каждого режима.
        points=[(x,y) for y in (-40,47,135) for x in (-64,127,319)]
        for first in range(9):
            for second in range(9):
                for mode in range(4):check([(128+mode*16+2,[first*5,second*5])],points,profile='clipped_segments')
        # Проверка всех невырожденных треугольников девяти зон и открытых ломаных с повторёнными точками.
        for triangle in combinations(range(9),3):
            a,b,c=(points[i] for i in triangle)
            if (b[0]-a[0])*(c[1]-a[1])==(b[1]-a[1])*(c[0]-a[0]):continue
            for reverse in (False,True):
                indices=[5*i for i in triangle];indices=indices[::-1] if reverse else indices
                for mode in range(5):check([(mode*16+3,indices)],points,profile='clipped_triangles')
        for number in range(2,16):
            for mode in range(4):
                indices=[5*((i*7+number)%9) for i in range(number)]
                check([(128+mode*16+number,indices)],points,profile='clipped_chains')
        # Проверка выпуклых внешних контуров с разными начальными вершинами.
        for _ in range(128):
            vertices=hull([(rng.randrange(-40,136),rng.randrange(-64,320)) for i in range(rng.randrange(4,16))])
            if len(vertices)<3:continue
            xy=[(x,y) for y,x in vertices]
            for shift in (0,1,len(xy)-1):
                indices=list(range(0,5*len(xy),5));indices=indices[shift:]+indices[:shift]
                check([(rng.randrange(5)*16+len(xy),indices)],xy,profile='clipped_convex')
        # Проверка локальных ветвей нулевого кода, не выдаваемых за допустимый объект после общего сканера E4DB.
        points=[(0,0),(255,0),(255,95),(0,95)]
        for index in range(4):
            codes=[0xF0]*4;codes[index]=0
            for mode in range(5):check([(mode*16+4,[0,5,10,15])],points,profile='zero_code_faces',codes=codes)
        for codes in ((0,0),(0,0xF0),(0xF0,0)):
            for mode in range(4):check([(128+mode*16+2,[0,5])],points[:2],profile='zero_code_lines',codes=codes)
    assert events['orientation'] and events['fill'] and events['line'] and events['face_rejected'] and events['attached_line_rejected']
    if clipped:assert events['clip_polygon'] and events['clip_segment'] and events['zero_code_abort']
    report=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),child_calls_and_paths=dict(events),entry=entry,
        actual_children_executed_without_stubs=True,composition_oracle=True,independent_full_geometry=False,
        exact_registers_flags_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        convex_onscreen_face_profile=True,clipped_convex_face_profile=clipped,
        direct_final_stream_and_empty_context_invariants=True,
        direct_single_line_counter_invariants=True,direct_clipped_endpoint_invariants=clipped,
        horizontal_degenerate_faces_checked=True,
        all_40_native_point_slots=True,line_counts_2_to_15=True,face_counts_3_to_15=True,
        record_stream_cross_page_boundaries_checked=True,
        modes_0_to_4_for_faces=True,all_four_line_selectors=True,
        clipped_parent_DBBD_proved=clipped,assembly_executed=False,irq_executed=False,native_execution=False)
    tag='ActionClippedPacketRenderer' if clipped else 'ActionPacketRenderer'
    (ROOT/('Tools/Disasm/Reports/'+tag+'Verification.json')).write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

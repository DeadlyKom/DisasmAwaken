"""Две настоящие цепочки ACTION до общего выбора следующего строкового предела."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from PreviewEdgeRasterOracle import arithmetic
from ReferenceControlsPointRespawn import cp_flags


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);sim=Simulator(memory);counts=Counter();ring_paths=Counter()
    for height in range(1,96):
        for delta in range(-255,256):
            for right in (False,True):
                memory.recording=False;memory.banks[0][:]=base[0]
                start=max(0,-delta);end=start+delta
                row=(95-height) if counts.total()&2 else 0
                serial=counts.total();number=3+serial%58
                skipped=(serial//58)%(number-1);anchor=(serial//(58*(number-1)))%number
                direction=1 if right else -1;target=(anchor+direction*(skipped+1))%number
                # Подготовка кольца с равными и меньшими строками между началом и восходящим концом.
                for index in range(number):
                    memory[0x9000+2*index]=(index*37+serial)&255
                    memory[0x9001+2*index]=max(0,row-index%3)
                memory[0x9000+2*anchor],memory[0x9001+2*anchor]=start,row
                memory[0x9000+2*target],memory[0x9001+2*target]=end,row+height
                memory[0xD3B7]=2*number-1
                other_end=(serial//2)%96
                memory[0xD387]=other_end
                cursor=0xD3B0 if right else 0xD275
                memory[cursor],memory[cursor+1]=1+2*anchor,0x90
                entry,stop=(0xD3AD,0xD4C1) if right else (0xD272,0xD386)
                initial=get_registers({'AF':row*256+0x5D,'HL':0x8C3A,'DE':row*256+0x89,'BC':0x80B3,
                    'IX':0x2468,'IY':0x5C3A,'^AF':0x69CF,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,
                    'SP':0xFFE0,'PC':entry},None,False)
                expected=[bytearray(b) for b in memory.banks];writes=[]
                def byte(a,v):
                    expected[0][a&0x3FFF]=v;writes.append((0,a&0x3FFF,v))
                # Расчёт деления наклона и поправки ошибки независимо от развёрнутого делителя.
                magnitude=abs(delta);quotient,remainder=divmod(magnitude,height);wide=magnitude>=height
                step=-((-delta)//height) if delta else 1;packed=(0x2000+32*step)&65535
                subtract=(0 if remainder==0 and wide else height-remainder) if delta>=0 else remainder
                encoded=(quotient^255)>>(1 if right and delta<0 else 0)
                out_e=encoded if wide else start
                if wide:
                    high=packed>>8;flags=arithmetic((high-0x20)&255,0x20)[1]
                elif delta>=0:
                    _,flags=arithmetic(0,(delta-height)&255,True)
                else:
                    flags=cp_flags(magnitude,height)
                wanted=list(initial);wanted[0:2]=[packed>>8 if right and wide else magnitude if right and delta<0 else height-delta if right else row,flags]
                wanted[4:8]=[row,out_e,0x8C,row]
                if right:
                    wanted[20:22]=[packed>>8,packed&255];wanted[22]=height//2
                else:
                    wanted[18:20]=[packed>>8,packed&255];wanted[23]=height//2
                wanted[PC]=stop
                # Обновление конечной вершины, высоты, вычитаемой ошибки и двух байтов временного стека.
                byte(0xFFDE,row);byte(0xFFDF,0x8C);byte(cursor,1+2*target);byte(cursor+1,0x90)
                byte(0xD223 if right else 0xD217,height)
                byte(0xD21F if right else 0xD213,subtract)
                byte(0xD387 if right else 0xD4C4,row+height)
                sim.registers[:]=initial;memory.writes=[];memory.recording=True
                for _ in range(700):
                    if sim.registers[PC]==stop:break
                    sim.run()
                else:raise AssertionError(('граница ребра',height,delta,right))
                memory.recording=False
                compared=(*range(13),14,*range(16,24),PC,26,27)
                assert all(wanted[i]==sim.registers[i] for i in compared),(height,delta,right,[(i,wanted[i],sim.registers[i]) for i in compared if wanted[i]!=sim.registers[i]])
                assert all(a==b for a,b in zip(expected,memory.banks)),(height,delta,right,'RAM')
                assert Counter(writes)==Counter(memory.writes),(height,delta,right,'writes',writes,memory.writes)
                if not right:
                    # Проверка завершения всего левого обновления после выбора состояния правой цепочки.
                    wanted[0:2]=[row,cp_flags(row,other_end)];wanted[7]=other_end
                    wanted[PC]=0xD4C1 if row<other_end else 0xD229
                    if row>=other_end:
                        byte(0xD22A,other_end);byte(0xD22C,0x3B)
                    memory.recording=True
                    for _ in range(12):
                        if sim.registers[PC]==wanted[PC]:break
                        sim.run()
                    else:raise AssertionError(('выбор после левого ребра',height,delta))
                    memory.recording=False
                    assert all(wanted[i]==sim.registers[i] for i in compared),(height,delta,'left scheduler',sim.registers[:8],wanted[:8])
                    assert all(a==b for a,b in zip(expected,memory.banks))
                    assert Counter(writes)==Counter(memory.writes)
                    ring_paths['left_to_selection' if row<other_end else 'left_to_right_preparation']+=1
                key=('right' if right else 'left')+('_negative' if delta<0 else '_positive')+('_wide' if wide else '_short')
                counts[key]+=1
                ring_paths[str(skipped)]+=1
                wrapped=(anchor+direction*(skipped+1))!=target
                ring_paths[('right' if right else 'left')+('_wrapped' if wrapped else '_direct')]+=1
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),all_95_heights_511_signed_slopes=True,
        exact_registers_flags_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        actual_instructions_without_stubs=True,temporary_stack_bytes=2,
        finite_ascending_ring_profile=True,ring_sizes_3_to_60=True,
        skipped_vertices_0_to_58=all(str(i) in ring_paths for i in range(59)),ring_paths=dict(ring_paths),
        whole_left_update_to_row_cycle_or_common_selector=True,
        all_ring_skip_inputs_exhausted=False,
        whole_polygon_fill_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPolygonEdgesVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

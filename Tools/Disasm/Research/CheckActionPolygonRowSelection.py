"""Общий выбор следующего предела, все сочетания трёх допустимых строк."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceControlsPointRespawn import cp_flags


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);sim=Simulator(memory);counts=Counter()
    initial=get_registers({'AF':0x005D,'HL':0x8C3A,'DE':0x2789,'BC':0x80B3,
        'IX':0x2468,'IY':0x5C3A,'^AF':0x69CF,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,
        'SP':0xFFE0,'PC':0xD4C1},None,False)
    for maximum in range(96):
        for left in range(96):
            for right in range(96):
                memory.recording=False
                memory[0xD4C2],memory[0xD4C4],memory[0xD387]=maximum,left,right
                # Проверка ближайшего предела и приоритета левой цепочки при равенстве двух рёбер.
                threshold=min(left,maximum)
                if right<threshold:limit,branch,path=right,0x3B,'right'
                elif left<maximum:limit,branch,path=left,0x45,'left'
                else:limit,branch,path=maximum,0x36,'maximum'
                wanted=list(initial);wanted[0:2]=[branch,cp_flags(right,threshold)]
                wanted[5],wanted[7],wanted[PC]=left,maximum,0xD22D
                sim.registers[:]=initial;memory.writes=[];memory.recording=True
                for _ in range(18):
                    if sim.registers[PC]==0xD22D:break
                    sim.run()
                else:raise AssertionError(('выбор предела',maximum,left,right))
                memory.recording=False
                compared=(*range(13),14,*range(16,24),PC,26,27)
                assert all(wanted[i]==sim.registers[i] for i in compared),(maximum,left,right,sim.registers[:8],wanted[:8])
                # Проверка исчерпывающего журнала всех записей, других изменений RAM данный блок не выполняет.
                assert Counter(memory.writes)==Counter(((0,0x122A,limit),(0,0x122C,branch)))
                assert memory[0xD22A]==limit and memory[0xD22C]==branch
                counts[path]+=1
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),all_96_cubed_row_combinations=True,
        exact_registers_flags_except_R=True,all_ram_writes_accounted_for=True,write_multiplicity_proved=True,
        left_priority_on_equal_edges=True,no_cpu_stack_writes=True,stop=0xD22D,
        whole_polygon_fill_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPolygonRowSelectionVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

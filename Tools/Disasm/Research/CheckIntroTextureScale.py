"""Все допустимые сочетания активных счётчиков масштаба, включая хвостовой селектор."""
from collections import Counter
import json
from CheckIntro import ROOT, original_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator, get_registers, PC, SP


def main():
    flat=original_memory()
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory)
    fixtures=[(warm,ramp,(warm+ramp)%40) for warm in range(3,162) for ramp in range(64)]
    fixtures += [(warm,index%64,index) for warm in (1,2) for index in range(40)]
    table=list(flat[0x6C62:0x6C8A]);cases=0
    for warm,ramp,index in fixtures:
        memory.recording=False
        for bank in (0,2,5):memory.banks[bank][:]=base[bank]
        memory[0x6C22],memory[0x6C2E],memory[0x6C3F]=warm,ramp,index
        stack=(0xBFFE,0x5FFE,0x9AFE)[cases%3]
        memory[stack],memory[stack+1]=255,63
        initial=get_registers({'AF':((cases*37)&255)*256+(cases&255),
            'HL':0x1234,'DE':0x5678,'BC':0x9ABC,'IX':0xDEF0,'IY':0x5C3A,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
            'SP':stack,'PC':0x6C21},None,False)
        initial[14],initial[26],initial[27]=cases&255,cases&1,cases%3
        expected=[bytearray(b) for b in memory.banks];writes=[]

        def put(address,value):
            expected[5][address&0x3FFF]=value
            writes.append((5,address&0x3FFF,value))

        # Обновление только активного второго или третьего счётчика после уменьшения первого.
        updated=max(1,warm-1);put(0x6C22,updated)
        if updated>1:
            new_ramp=min(63,ramp+1);put(0x6C2E,new_ramp)
            selected=39+new_ramp//2
        else:
            new_index=(index+1)%40;put(0x6C3F,new_index)
            selected=56+table[new_index]
        pointer=0xF000+16*selected
        put(0x6BB2,pointer&255);put(0x6BB3,pointer>>8)
        wanted=list(initial)
        wanted[0:2]=[selected,0x20]
        wanted[4:8]=[0xF0,0,pointer>>8,pointer&255]
        wanted[SP],wanted[PC]=stack+2,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6C21,stop=0x3FFF);memory.recording=False
        # Проверка полного контракта и отсутствия записей в CPU-стек.
        compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(warm,ramp,index,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(warm,ramp,index,'RAM')
        assert Counter(writes)==Counter(memory.writes),(warm,ramp,index,'writes')
        cases+=1
    report=dict(passed=True,total_cases=cases,ramp_cases=10176,cycle_cases=80,
        initial_countdown_domain=[1,161],ramp_domain=[0,63],cyclic_index_domain=[0,39],
        all_active_counter_combinations=True,inactive_counters_sampled=True,
        all_initial_flags_values=True,all_registers_except_R=True,exact_final_F=32,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        cpu_stack_written=False,actual_tail_selector_executed=True,
        independent_numeric_oracle=True,arbitrary_corrupt_counter_states_proved=False,
        assembly_executed=False,native_execution=False,irq_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroTextureScaleVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

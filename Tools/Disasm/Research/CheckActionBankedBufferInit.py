"""Обёртка 6CD6, все 65536 Seed, 70 настоящих вызовов генератора и реальные банки/порты."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from ReferenceControlsBufferPoints import random_step,coordinates
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    base[1]=bytearray(base_memory()[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory);costs=[]
    for seed in range(65536):
        memory.recording=False
        for page in (0,1,2,5):memory.banks[page][:]=base[page]
        # Создание исходного Seed в реальном банке 1 и двух вариантов CPU-стека.
        memory.banks[1][0xA8F:0xA91]=bytes((seed&255,seed>>8))
        old=seed&31;stack=0x8002 if seed&1 else 0xBFFE;memory.out7ffd(old)
        memory[stack],memory[stack+1]=255,63
        initial=get_registers({'AF':seed,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0x6CD6},None,False)
        initial[14],initial[15],initial[26],initial[27]=seed&255,seed&255,seed&1,seed%3
        expected=[bytearray(b) for b in memory.banks];writes=[]

        def put(address,value,page=None):
            bank=page if page is not None else 5 if address<0x8000 else 2
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))

        def word(address,value,page=None):put(address,value&255,page);put(address+1,value>>8,page)

        word(stack-2,0x6CDB);word(stack-4,0x369C)
        word(stack-2,0x6CDE)
        state=seed;adjustments=0
        for index in range(35):
            # Расчёт двух состояний и исходных ограничений, X генерируется первым, хранится вторым.
            word(stack-4,0xCAB9);state,mixed,difference,_=random_step(state)
            word(0xCA8F,state,1);raw_x=state&255
            x=2 if raw_x==0 else raw_x-2 if raw_x>=254 else raw_x
            adjustments+=int(raw_x==0 or raw_x>=254)
            word(stack-4,0xCAC9);state,mixed,difference,_=random_step(state)
            word(0xCA8F,state,1);raw_y=state&127
            y=2 if raw_y==0 else raw_y-64 if raw_y>=95 else raw_y
            adjustments+=int(raw_y==0 or raw_y>=95)
            put(0xC500+2*index,y,1);put(0xC501+2*index,x,1)
        following,points,y_flags=coordinates(seed)
        assert state==following and expected[1][0x500:0x546]==bytes(points)
        word(stack-2,0x6CE3);word(stack-4,0x369C)
        wanted=list(initial);wanted[0:2]=[16,0x42];wanted[6:8]=[0xC5,0x46]
        wanted[16:24]=[points[-2],y_flags&1,0,mixed&255,difference>>8,difference&255,state>>8,state&255]
        m1=3030+adjustments
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],m1),stack+2,0x3FFF
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True;simulator.run(start=0x6CD6,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(seed,m1,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(seed,'RAM')
        assert Counter(memory.writes)==Counter(writes),(seed,'writes')
        assert trace.writes==[(0x7FFD,17),(0x7FFD,16)] and memory.o7ffd==16
        assert len(memory.writes)==360
        costs.append(m1)
        if (seed+1)%8192==0:print(str(seed+1)+' seeds passed',flush=True)
    report=dict(passed=True,total_cases=65536,all_initial_seed_words=True,all_input_AF_coupled_to_seed=True,
        all_unlocked_initial_paging_values_sampled=True,two_stack_profiles=[0xBFFE,0x8002],
        full_seed_paging_stack_product_exhausted=False,actual_children_and_ports_executed=True,
        points=35,random_calls_per_case=70,byte_write_events_per_case=360,maximum_additional_stack_bytes=4,
        exact_registers_including_R=True,refresh_m1_base=3030,observed_m1_min=min(costs),observed_m1_max=max(costs),
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,hardware_bus_write_order_proved=False,
        original_coordinate_limits_preserved=True,independent_numeric_oracle=True,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionBankedBufferInitVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

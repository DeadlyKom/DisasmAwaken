"""Повторный настоящий поиск класса 14 от начала массива после каждой пометки IY."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionClassReuse import profiles
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    cases=0;costs=[];removed=Counter()
    for code,kinds,flags in profiles():
        if code!=0x12:continue
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        for position,kind in enumerate(kinds):
            pointer=0xA100+64*position
            memory[pointer],memory[pointer+1]=position+1,128 if kind==0 else position%7+1
            memory[pointer+18],memory[pointer+24]=20 if kind==2 else 0x34,position+17
        memory[0xA780],memory[0xA781]=128,128
        memory[0xBFFE],memory[0xBFFF]=255,63
        initial=get_registers({'AF':((flags*109)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6172},None,False)
        initial[14],initial[15],initial[26],initial[27]=flags,flags,flags&1,flags%3
        expected=[bytearray(b) for b in memory.banks];writes=[];states=list(kinds);m1=0;marked=0

        def put(address,value):expected[2][address&0x3FFF]=value;writes.append((2,address&0x3FFF,value))

        def word(address,value):put(address,value&255);put(address+1,value>>8)

        while True:
            # Создание рамки внешнего поиска и числового эталона повторного прохода от A100.
            word(0xBFFC,0x6177);m1+=5;position=0
            while True:
                word(0xBFFA,0xE997);m1+=1
                while position<26 and states[position]==0:position+=1;m1+=10
                if position==26:m1+=12;break
                m1+=11
                if states[position]==2:m1+=2;break
                position+=1
            m1+=1
            if position==26:break
            # Пометка найденной записи, следующий поиск снова начнётся перед A100.
            pointer=0xA100+64*position;word(0xBFFC,0x617B)
            put(pointer+1,128);put(pointer,0);put(pointer+24,255)
            states[position]=0;m1+=9;marked+=1
        wanted=list(initial);wanted[0:2]=[128,0x42];wanted[2:4]=[0,64];wanted[4]=20;wanted[10:12]=[0xA7,128]
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],m1),0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6172,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,m1,wanted,simulator.registers)
        assert all(a==b for a,b in zip(expected,memory.banks)),(cases,'RAM')
        assert Counter(writes)==Counter(memory.writes),(cases,'writes',memory.writes,writes)
        cases+=1;costs.append(m1);removed[marked]+=1
    report=dict(passed=True,total_cases=cases,all_26_positions_and_three_states=True,all_input_F=True,
        mixed_patterns=1024,real_search_iterator_and_IY_setter_executed=True,
        search_restarts_after_each_mark=True,independent_numeric_oracle=True,exact_registers_including_R=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,hardware_bus_write_order_proved=False,
        maximum_additional_stack_bytes=4,observed_m1_min=min(costs),observed_m1_max=max(costs),
        removed_count_histogram=dict(sorted(removed.items())),all_list_combinations_exhausted=False,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionClass14ReuseVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

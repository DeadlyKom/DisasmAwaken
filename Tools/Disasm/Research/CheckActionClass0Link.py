"""660E и общий хвост 661A, настоящий поток 10, поиск, подстановка и все физические эффекты."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceActionRecordFilters import Machine


def profiles():
    for override in range(256):
        for r in range(256):yield 0x660E,override,r,1,0,(r*37)&255,(override+r)%4,'all_override_R_pairs'
    for seed in range(65536):
        for override in (0,255):yield 0x660E,override,128,seed,0,seed&255,seed%4,'all_stream10_low_words'
    for fold in range(256):
        for seed in (0,1,0x7FFF,0x8000,0xFFFF):
            for override in (0,255):yield 0x660E,override,128,seed,fold,fold,fold%4,'stream10_fold_edges'
    for flags in range(256):
        for seed in (0,1,0x7FFF,0x8000,0xFFFF):
            for fold in (0,127,255):
                for style in range(4):yield 0x661A,255,(flags*109)&255,seed,fold,flags,style,'common_tail_all_F'


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    counts=Counter();entries=Counter();paths=Counter();max_depth=0;costs=[]
    for entry,override,r,seed,fold,flags,style,kind in profiles():
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        rows=() if style==0 else ((1,1),) if style==1 else ((1,0),(128,18),(1,16),(1,18)) if style==2 else ((1,0),)*26
        for index,(header,code) in enumerate(rows):
            pointer=0xA100+64*index;memory[pointer],memory[pointer+1],memory[pointer+18]=index+1,header,code
        marker=0xA100+64*len(rows);memory[marker],memory[marker+1]=128,128
        ix=0xA100+64*(serial%26);memory[ix+21]=override
        memory[ix+10],memory[ix+11]=(serial*37)&255,(serial*109)&255
        memory[0xEBE7],memory[0xEBE8],memory[0xEBE9]=seed&255,seed>>8,fold
        stack=0x8002 if serial&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'AF':((serial*73)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':ix,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,r,serial&1,serial%3
        model=Machine(memory.banks,initial)
        if entry==0x660E:model.class0()
        else:model.common_class_link()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(serial,hex(entry),override,r,seed,fold,style,model.path,
            [(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(model.banks,memory.banks)),(serial,hex(entry),'RAM',model.path)
        assert Counter(model.writes)==Counter(memory.writes),(serial,hex(entry),'writes',model.path)
        for depth in range(1,9):
            address=stack-depth;coordinate=(5 if address<0x8000 else 2,address&0x3FFF)
            if any(item[:2]==coordinate for item in memory.writes):max_depth=max(max_depth,depth)
        counts[kind]+=1;entries[hex(entry)]+=1;paths.update(model.path);costs.append(model.m1_count)
        if counts.total()%32768==0:print(str(counts.total())+' cases passed',flush=True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),cases_by_entry=dict(entries),paths=dict(paths),
        actual_override_generator_filters_iterator_and_index_executed=True,independent_numeric_parent_oracle=True,
        all_override_bytes_and_initial_R=True,all_stream10_low_words_at_fold_0=True,
        all_fold_bytes_at_five_word_edges=True,common_tail_all_input_F=True,zero_override_still_continues=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        maximum_additional_stack_bytes=max_depth,hardware_bus_stack_write_order_proved=False,
        complete_state_and_list_product_exhausted=False,random_distribution_and_period_proved=False,
        observed_m1_min=min(costs),observed_m1_max=max(costs),game_array_capacity_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert report['total_cases']==214528 and max_depth==8
    (ROOT/'Tools/Disasm/Reports/ActionClass0LinkVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

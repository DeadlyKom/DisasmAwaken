"""F51E..F57E, восемь входов выбора опоры, обновление класса 18 и обязательный сброс баз."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceActionRecordFilters import Machine

ENTRIES=(0xF51E,0xF527,0xF535,0xF53F,0xF541,0xF54B,0xF54D,0xF557)
LISTS=((),((1,0),(1,18)),((1,7),(1,18)),((1,5),(1,18)),
       ((1,0),(1,3),(1,18)),((1,0),),((128,0),(1,7),(128,3),(1,18)),
       ((1,5),(1,7),(1,0),(1,18),(1,18)))


def profiles():
    for entry in ENTRIES:
        for flags in range(256):
            for style,rows in enumerate(LISTS):yield entry,(flags*109)&65535,(flags*73)&255,flags,(style*37)&255,flags,rows,'all_entries_F_and_lists'
    for r in range(256):
        for gate in (0,1,79,80,81,127,128,255):
            for style in range(4):yield 0xF51E,1,r,gate,gate,r,LISTS[style],'all_R_gate_edges'
    for gate in range(256):
        for r in (0,100,127,128,227,228,229,253,254,255):
            for seed in (0,1,0x7FFF,0xFFFF):yield 0xF51E,seed,r,0,gate,gate,LISTS[(r+seed)%8],'all_gate_bytes'
    for word in range(65536):yield 0xF51E,word,228,0,80,word&255,LISTS[word%8],'all_stream2_low_words'
    for fold in range(256):
        for word in (0,1,0x7FFF,0x8000,0xFFFF):yield 0xF51E,word,228,fold,80,fold,LISTS[fold%8],'stream2_fold_edges'
    for word in range(65536):yield 0xF527,word,word&255,0,(word*37)&255,word&255,LISTS[word%8],'all_continuation_HL'
    for entry in (0xF535,0xF541,0xF54D):
        for position in range(26):
            for code in range(256):
                rows=((1,1),)*position+((1,code),(1,18))
                yield entry,0x1357,code,0,80,code,rows,'all_priority_classes_and_positions'
    for entry in (0xF53F,0xF54B,0xF557):
        for af in range(65536):yield entry,0x1357,af&255,0,80,af,LISTS[af%8],'all_selected_AF'


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    counts=Counter();entries=Counter();paths=Counter();max_depth=0;costs=[]
    for entry,word,r,fold,gate,af,rows,kind in profiles():
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        for index,(header,code) in enumerate(rows):
            pointer=0xA100+64*index;memory[pointer],memory[pointer+1],memory[pointer+18]=index+1,header,code
            for offset in (10,13,22):memory[pointer+offset]=(serial*37+index*109+offset)&255
        marker=0xA100+64*len(rows);memory[marker],memory[marker+1]=128,128
        memory[0x9BCD]=gate;memory[0xEBEA],memory[0xEBEB],memory[0xEBEC]=word&255,word>>8,fold
        for index,address in enumerate((0xE5B0,0xE5CF,0xE5EA)):
            value=(serial*(73+index*2)+index*109)&65535;memory[address],memory[address+1]=value&255,value>>8
        stack=0x8002 if serial&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'AF':af,'HL':word,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':(serial*109+0xDEF0)&65535,
            'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,r,serial&1,serial%3
        model=Machine(memory.banks,initial).preferred(entry)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(serial,hex(entry),word,r,fold,gate,af,model.path,
            [(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(model.banks,memory.banks)),(serial,hex(entry),'RAM',model.path)
        assert Counter(model.writes)==Counter(memory.writes),(serial,hex(entry),'write_multiplicity',model.path)
        for depth in range(1,7):
            address=stack-depth;coordinate=(5 if address<0x8000 else 2,address&0x3FFF)
            if any(item[:2]==coordinate for item in memory.writes):max_depth=max(max_depth,depth)
        counts[kind]+=1;entries[hex(entry)]+=1;paths.update(model.path);costs.append(model.m1_count)
        if counts.total()%32768==0:print(str(counts.total())+' cases passed',flush=True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),cases_by_entry=dict(entries),paths=dict(paths),
        all_eight_entries_and_input_F=True,all_initial_R_and_gate_bytes_at_boundaries=True,
        all_stream2_low_words_at_fold_0=True,all_fold_bytes_at_five_word_edges=True,all_continuation_HL=True,
        all_priority_class_codes_and_positions=True,all_AF_at_selected_reference_entries=True,
        actual_generator_search_iterator_index_conversion_and_base_reset_executed=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        maximum_additional_stack_bytes=max_depth,priority_0_then_7_then_5_preserved=True,
        class3_prevents_class18_update=True,only_first_class18_updated=True,bases_reset_on_all_returns=True,
        selected_AF_exchange_and_partial_effects_proved=True,independent_numeric_parent_oracle=True,
        hardware_bus_stack_write_order_proved=False,complete_state_and_list_product_exhausted=False,
        random_distribution_and_period_proved=False,observed_m1_min=min(costs),observed_m1_max=max(costs),
        game_array_capacity_proved=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==383744 and max_depth==6
    (ROOT/'Tools/Disasm/Reports/ActionPreferredRecordVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

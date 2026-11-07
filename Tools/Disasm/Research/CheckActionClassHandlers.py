"""Восемь исходных обработчиков классов, точные регистры, R, банки и все слова рамок."""
from collections import Counter,defaultdict
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionClassHandlers import ClassMachine,ENTRIES


def profiles():
    edges=(0,1,59,5254,41961,0x7FFF,0x8000,0xFFFF)
    for kind in ENTRIES:
        for override in range(1,255):
            for r in (0,112,255):yield kind,override,r,override*257,0,override*137&65535,0,(override*73)&255,override%4,'active_override'
        for override in (0,255):
            for r in range(256):
                for seed in edges:yield kind,override,r,seed,0,seed^0x5A5A,0,(r*37+seed)&255,(r+seed)%4,'all_R_zero_and_ff_override'
        for fold in range(256):
            for seed in (0,1,0x7FFF,0x8000,0xFFFF):
                for override in (0,255):yield kind,override,fold,seed,fold,seed,fold,fold,fold%4,'fold_edges'
    for kind in (1,5,6,8):
        for seed in range(65536):yield kind,255,seed&255,seed,0,seed^0x5A5A,0,seed&255,seed%4,'all_stream0_words'
    for seed in range(65536):
        override=0 if seed&1 else 255;r=(2-(14 if override==0 else 8))&127
        yield 3,override,r,seed,0,seed,0,64 if seed&1 else 255,seed%4,'all_stream8_words'
    for gate in range(256):
        for read_r in range(6):
            for override in (0,255):
                r=(read_r-(14 if override==0 else 8))&127
                for seed in (0,1,0x7FFF,0x8000,0xFFFF):
                    yield 3,override,r,seed,0,seed,(gate+seed)&255,gate,(gate+seed)%4,'all_special_gate_bytes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);counts=Counter();per_entry=Counter();paths=defaultdict(Counter);depths=Counter();cases=0
    for kind,override,r,seed,fold,seed8,fold8,gate,style,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        rows=() if style==0 else ((1,5),(1,6),(1,7),(1,14),(1,18)) if style==1 else (
            (1,0),(128,18),(1,16),(1,18)) if style==2 else ((1,0),)*26
        for index,(header,code) in enumerate(rows):
            pointer=0xA100+64*index;memory[pointer],memory[pointer+1],memory[pointer+18]=index+1,header,code
        marker=0xA100+64*len(rows);memory[marker],memory[marker+1]=128,128
        ix=0xA100+64*(cases%26)
        memory[ix+21],memory[ix+10],memory[ix+11],memory[ix+18]=override,(cases*37)&255,(cases*109)&255,kind
        for pointer,word,high in ((0xEBDE,seed,fold),(0xEBE1,seed8,fold8),(0xEBE7,(seed*17)&65535,fold)):
            memory[pointer],memory[pointer+1],memory[pointer+2]=word&255,word>>8,high
        memory[0x9BCD]=gate
        stack=0x8002 if cases&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        entry=ENTRIES[kind]
        initial=get_registers({'PC':entry,'SP':stack,'AF':(cases*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
        model=ClassMachine(memory.banks,initial);model.handle(kind)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF)
        memory.recording=False
        compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(cases,kind,profile,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,kind,profile,'RAM',model.path)
        for address in range(stack-10,stack):
            page=5 if address<0x8000 else 2
            if any(bank==page and offset==(address&0x3FFF) for bank,offset,_ in memory.writes):depths[kind]=max(depths[kind],stack-address)
        counts[profile]+=1;per_entry[kind]+=1;paths[kind].update(model.path);cases+=1
        if cases%65536==0:print(str(cases)+' cases passed',flush=True)
    assert cases==402384 and set(depths)==set(ENTRIES)
    assert paths[1]['class1_becomes_class0'] and paths[3]['class3_code26']
    assert paths[6]['class6_nonzero_common'] and paths[6]['class6_zero_secondary']
    result=dict(passed=True,total_cases=cases,cases_by_profile=dict(counts),
        cases_by_class={str(kind):per_entry[kind] for kind in ENTRIES},
        paths_by_class={str(kind):dict(paths[kind]) for kind in ENTRIES},
        maximum_stack_bytes_by_class={str(kind):depths[kind] for kind in ENTRIES},
        actual_override_random_streams_filters_and_iterator_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        full_stream0_words_at_fold0_classes=[1,5,6,8],full_stream8_words_at_fold0_class3=True,
        all_256_special_gate_bytes_at_six_low_r_values=True,zero_override_writes_and_continues_preserved=True,
        opposite_class6_predicate_preserved=True,all_state_list_products_exhausted=False,
        random_distribution_and_period_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClassHandlersVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for kind in ENTRIES:
        proof=dict(result,total_cases=per_entry[kind],class_code=kind,
                   combined_report='Tools/Disasm/Reports/ActionClassHandlersVerification.json')
        (ROOT/f'Tools/Disasm/Reports/ActionClass{kind}LinkVerification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key!='paths_by_class'},indent=2))


if __name__=='__main__':main()

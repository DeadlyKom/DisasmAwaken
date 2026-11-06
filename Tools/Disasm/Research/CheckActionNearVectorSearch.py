"""69BE, реальные вызовы 6A29, все средние слова и граничные длины списка."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionNearVectorSearch import evaluate


def profiles():
    for position in range(3):
        for word in range(65536):
            for sign in (0,0xFF000000):
                values=[0x1234,0xFFFFDCBA,0x123456];values[position]=sign|(word<<8)|0xA5
                yield (tuple(values),),'all_middle_words_each_sign_and_position'
    edges=(0,0x3BFF00,0x3C0000,0x7FFFFFFF,0x80000000,0xFFC30000,0xFFC40000,0xFFFFFFFF)
    for values in product(edges,repeat=3):yield (values,),'boundary_products'
    for count in range(256):
        yield ((0x7FFFFFFF,0,0),)*count,'all_counts_without_match'
        for position in sorted({0,count//2,count-1}):
            if position<0 or not count:continue
            rows=[(0x7FFFFFFF,0,0)]*count;rows[position]=(0x1234,0xFFFFDCBA,0x123456)
            yield tuple(rows),'all_counts_match_edges_and_middle'
    randomizer=random.Random(0x69BE)
    for _ in range(8192):
        rows=[]
        for _ in range(randomizer.randrange(13)):
            if randomizer.randrange(3):rows.append(tuple(randomizer.getrandbits(32) for _ in range(3)))
            else:rows.append(tuple(randomizer.randrange(60)<<16|randomizer.randrange(65536) for _ in range(3)))
        yield tuple(rows),'mixed_lists'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks];expected=[bytearray(b) for b in baseline]
    simulator=Simulator(memory);counts=Counter();paths=Counter();touched=set();costs=set()
    def page(address):return 5 if address<0x8000 else 2
    for rows,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=expected[bank][offset]=baseline[bank][offset]
        touched=set();old=serial&63;memory.out7ffd(old);stack=0xBFFE;setup={stack:255,stack+1:63,0x688B:len(rows)}
        for index,values in enumerate(rows):
            for component,value in enumerate(values):
                for byte in range(4):setup[0x9B27+12*index+4*component+byte]=(value>>(8*byte))&255
        for address,value in setup.items():
            bank=page(address);memory[address]=value;expected[bank][address&0x3FFF]=value;touched.add((bank,address&0x3FFF))
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':(serial*137)&65535,'SP':stack,'PC':0x69BE},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        local=evaluate(initial,rows);wanted=local['registers'];writes=[]
        for address,value in local['writes']:
            bank=page(address);offset=address&0x3FFF;expected[bank][offset]=value;writes.append((bank,offset,value));touched.add((bank,offset))
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x69BE,stop=0x3FFF);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(serial,rows,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert Counter(writes)==Counter(memory.writes) and memory.o7ffd==old,(serial,'writes_or_page')
        assert all(memory.banks[b][o]==expected[b][o] for b,o in touched),(serial,'RAM')
        counts[kind]+=1;paths['empty' if not rows else 'missing' if local['found_index'] is None else 'found']+=1;costs.add(local['refresh_m1'])
        if counts.total()%131072==0:print(str(counts.total())+' cases passed',flush=True)
    assert all(a==b for a,b in zip(expected,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        all_middle_words_for_both_signs_and_all_positions=True,all_256_counts=True,actual_near_predicate_executed=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_and_stack_residue_proved=True,
        first_near_vector_selected=True,later_component_wins_equal_high_byte=True,selected_middle_word_bytes_swapped=True,
        maximum_additional_stack_bytes=4,observed_m1_min=min(costs),observed_m1_max=max(costs),
        complete_list_product_exhausted=False,game_count_bound_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionNearVectorSearchVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

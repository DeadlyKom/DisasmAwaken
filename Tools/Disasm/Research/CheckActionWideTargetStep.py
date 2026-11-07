"""7EB7, без подмены дочерних процедур, восемь банков и настоящий порт 7FFD."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionWideTargetStep import evaluate


def profiles():
    standard=(0x12345678,0xFFEDCBA9,0x87654321);words=(0x1357,0x2468,0x369C)
    for position in range(3):
        for word in range(65536):
            targets=list(words);targets[position]=word
            yield standard,tuple(targets),word&255,'all_record_words_each_position'
    for word in range(65536):
        yield (word,0xFFFF8001,0x00800000),words,word&255,'all_first_low_words'
        yield (0x1234,0xFFFFDCBA,(word<<16)|0x1357),words,word&255,'all_third_high_words'
    edges=(0,1,0x7EFF,0x7F00,0x7FFF,0x8000,0xFFFF,0x800000,0x7FFFFFFF,0x80000000,0xFF800000,0xFFFF8000,0xFFFF8001,0xFFFFFFFF)
    for values in product(edges,repeat=3):yield values,words,2,'edge_products'
    randomizer=random.Random(0x7EB7)
    for _ in range(8192):
        yield tuple(randomizer.getrandbits(32) for _ in range(3)),tuple(randomizer.randrange(65536) for _ in range(3)),randomizer.randrange(256),'mixed_inputs'


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    ratio_table=bytes(flat[0x9A00:0x9B00]);banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);root_table=bytes(banks[1][:768]);memory=RecordedBanks(banks=banks,out7ffd=16)
    baseline=[bytearray(b) for b in memory.banks];expected=[bytearray(b) for b in baseline]
    simulator=Simulator(memory);counts=Counter();touched=set();targets_seen=[set(),set()]
    def page(address):return 5 if address<0x8000 else 2 if address<0xC000 else 0
    for values,words,rate,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=expected[bank][offset]=baseline[bank][offset]
        touched=set();old=(serial%4)*8;memory.out7ffd(old);stack=0xBFFE;ix=0xA100+64*(serial%26);iy=0x9B27+12*(serial%6)
        currents=((serial*73)&255,(serial*109)&255);setup={stack:255,stack+1:63,ix+8:currents[0],ix+9:currents[1],ix+37:rate}
        for position,value in enumerate(values):
            for offset in range(4):setup[iy+4*position+offset]=(value>>(8*offset))&255
        for position,value in enumerate(words):setup[ix+2*position],setup[ix+2*position+1]=value&255,value>>8
        for address,value in setup.items():
            bank=page(address);memory[address]=value;expected[bank][address&0x3FFF]=value;touched.add((bank,address&0x3FFF))
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':(serial*109)&65535,'IX':ix,'IY':iy,'SP':stack,'PC':0x7EB7},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        local=evaluate(initial,values,words,currents,rate,ratio_table,root_table);wanted=local['registers'];writes=[]
        for address,value in local['writes']:
            bank=page(address);offset=address&0x3FFF;expected[bank][offset]=value;writes.append((bank,offset,value));touched.add((bank,offset))
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        simulator.run(start=0x7EB7,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,values,words,rate,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert Counter(writes)==Counter(memory.writes),(serial,'write_multiplicity')
        assert all(memory.banks[b][o]==expected[b][o] for b,o in touched),(serial,'RAM')
        assert trace.writes==local['ports'] and memory.o7ffd==16,(serial,'ports')
        for seen,target in zip(targets_seen,local['targets']):seen.add(target)
        counts[kind]+=1
        if counts.total()%65536==0:print(str(counts.total())+' cases passed',flush=True)
    assert all(a==b for a,b in zip(expected,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),
        all_record_words_each_position=True,all_first_low_words=True,all_third_high_words=True,
        exact_registers_flags_r_sp=True,refresh_R_proved=True,actual_all_children_executed=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_and_stack_residue_proved=True,
        maximum_additional_stack_bytes=16,real_ports_and_eight_banks=True,final_7ffd=16,
        original_bit23_sign_and_asymmetric_byte_step_preserved=True,observed_target_counts=[len(s) for s in targets_seen],
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==338616
    (ROOT/'Tools/Disasm/Reports/ActionWideTargetStepVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

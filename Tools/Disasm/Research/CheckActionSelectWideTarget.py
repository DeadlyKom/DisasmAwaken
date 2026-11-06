"""7E9D, первый близкий либо первый элемент при ненулевом списке, полный вызов цепочки движения."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionWideTargetStep import evaluate as wide_step
from ReferenceActionNearVectorSearch import check_words
from ReferenceControlsPointRespawn import refresh


def profiles():
    for af in range(65536):yield (),af,'all_input_AF_empty'
    for count in range(1,256):
        for mode in ('first','last','fallback'):
            rows=[(0x7FFFFFFF,0,0)]*count
            if mode!='fallback':rows[0 if mode=='first' else count-1]=(0x1234,0xFFFFDCBA,0x123456)
            yield tuple(rows),count,'all_counts_'+mode
    randomizer=random.Random(0x7E9D)
    for _ in range(8192):
        rows=[]
        for _ in range(randomizer.randrange(13)):
            if randomizer.randrange(3):rows.append(tuple(randomizer.getrandbits(32) for _ in range(3)))
            else:rows.append(tuple(randomizer.randrange(60)<<16|randomizer.randrange(65536) for _ in range(3)))
        yield tuple(rows),randomizer.randrange(65536),'mixed_lists'


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    ratio_table=bytes(flat[0x9A00:0x9B00]);banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);root_table=bytes(banks[1][:768]);memory=RecordedBanks(banks=banks,out7ffd=16)
    baseline=[bytearray(b) for b in memory.banks];expected=[bytearray(b) for b in baseline]
    simulator=Simulator(memory);counts=Counter();paths=Counter();touched=set()
    def page(address):return 5 if address<0x8000 else 2 if address<0xC000 else 0
    for rows,af,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=expected[bank][offset]=baseline[bank][offset]
        touched=set();old=(serial%4)*8;memory.out7ffd(old);stack=0xBFFE;ix=0xA900
        words=((serial*73)&65535,(serial*109)&65535,(serial*137)&65535);currents=(serial&255,(serial*43)&255);rate=(serial*53)&255
        setup={stack:255,stack+1:63,0x688B:len(rows),ix+8:currents[0],ix+9:currents[1],ix+37:rate}
        for index,values in enumerate(rows):
            for component,value in enumerate(values):
                for byte in range(4):setup[0x9B27+12*index+4*component+byte]=(value>>(8*byte))&255
        for position,value in enumerate(words):setup[ix+2*position],setup[ix+2*position+1]=value&255,value>>8
        for address,value in setup.items():
            bank=page(address);memory[address]=value;expected[bank][address&0x3FFF]=value;touched.add((bank,address&0x3FFF))
        initial=get_registers({'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':(serial*109)&65535,'IX':ix,'IY':0x5C3A,'SP':stack,'PC':0x7E9D},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        operations=[];ports=[];wanted=list(initial)
        if rows:
            chosen=next((index for index,values in enumerate(rows) if check_words(values)[0]),None)
            iterations=chosen+1 if chosen is not None else len(rows);selected=chosen if chosen is not None else 0
            operations.extend(pair for _ in range(iterations) for pair in ((stack-2,0xAD),(stack-1,0x7E)))
            child=list(initial);child[10:12]=[(0x9B27+12*selected)>>8,(0x9B27+12*selected)&255]
            local=wide_step(child,rows[selected],words,currents,rate,ratio_table,root_table)
            wanted=local['registers'];operations.extend(local['writes']);ports=local['ports'];reason='first_near' if chosen is not None else 'fallback_first'
        else:
            wanted[0:2]=[0,0x44];wanted[10:12]=[0x9B,0x27];wanted[12]=stack+2;wanted[24]=0x3FFF
            wanted[15]=refresh(initial[15],5);reason='empty'
        writes=[]
        for address,value in operations:
            bank=page(address);offset=address&0x3FFF;expected[bank][offset]=value;writes.append((bank,offset,value));touched.add((bank,offset))
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        simulator.run(start=0x7E9D,stop=0x3FFF);memory.recording=False
        compared=(*range(15),*range(16,25),26,27) if rows else (*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,len(rows),reason,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert Counter(writes)==Counter(memory.writes),(serial,'write_multiplicity')
        assert all(memory.banks[b][o]==expected[b][o] for b,o in touched),(serial,'RAM')
        assert trace.writes==ports and memory.o7ffd==(16 if rows else old),(serial,'ports')
        counts[kind]+=1;paths[reason]+=1
    assert all(a==b for a,b in zip(expected,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        all_256_counts=True,all_input_AF_empty=True,empty_IY_set_to_first_vector=True,empty_refresh_m1=5,
        exact_nonempty_registers_except_R=True,nonempty_refresh_R_proved=False,
        actual_all_children_executed=True,first_near_or_first_fallback_preserved=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_and_stack_residue_proved=True,
        maximum_additional_stack_bytes=16,real_ports_and_eight_banks=True,
        complete_list_product_exhausted=False,game_count_bound_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==74493
    (ROOT/'Tools/Disasm/Reports/ActionSelectWideTargetVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

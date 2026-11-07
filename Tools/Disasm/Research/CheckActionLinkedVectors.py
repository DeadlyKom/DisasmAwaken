"""E794, два трёхсловных набора, особая связь 1A и отказ по полному байту 80."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsPointRespawn import refresh


def profiles():
    for axis in range(6):
        for value in range(65536):
            words=[0x1234,0x7FFF,0x8000,0x5678,0x9ABC,0xDEF0];words[axis]=value
            yield 1,0,tuple(words),False,'all_six_word_domains'
    for index in range(256):
        for kind in range(3):yield index,26 if kind==2 else 0,(0x1234,0x7FFF,0x8000,0x5678,0x9ABC,0xDEF0),kind==1,'all_pointers'
    for linked in range(256):yield 1,linked,(0x1234,0x7FFF,0x8000,0x5678,0x9ABC,0xDEF0),False,'all_link_codes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter()
    for index,linked,words,unavailable,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        ix=0xA100;pointer=0xA100+64*index;stack=0xBFFE
        if index<26:
            for offset,value in zip((0,2,4,26,28,30),words):memory[pointer+offset],memory[pointer+offset+1]=value&255,value>>8
            if unavailable:memory[pointer+27]=128
        memory[0xE796],memory[0xE797]=pointer&255,pointer>>8
        memory[ix+11]=linked;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xE794,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        wanted=list(initial);operations=[]
        high=memory[pointer+27]
        if linked==26:
            selected=0xA780;wanted[2:8]=[0,0,255,255,255,176]
            wanted[0:2]=[26,logical_flags(26)|16];m1=24;path='special_1A'
            assigned=((0xD9B6,0),(0xAF48,0),(0xAF56,0),(0xAF69,0),(0xD7C4,0xFFB0),(0xD7A2,0xFFFF))
        elif high==128:
            selected=pointer;wanted[0:2]=[128,0x41];m1=11;path='unavailable';assigned=()
        else:
            selected=pointer;wanted[0:2]=[high,logical_flags(high)|16]
            values=[memory[pointer+offset]+256*memory[pointer+offset+1] for offset in (0,2,4,26,28,30)]
            wanted[2:8]=[values[3]>>8,values[3]&255,values[5]>>8,values[5]&255,values[4]>>8,values[4]&255]
            assigned=tuple(zip((0xAF48,0xAF56,0xAF69,0xD9B6,0xD7C4,0xD7A2),values));m1=44;path='copied'
        wanted[10:12]=[selected>>8,selected&255]
        wanted[12],wanted[15],wanted[24]=stack+2,refresh(initial[15],m1),0x3FFF
        for address,value in assigned:operations.extend(((address,value&255),(address+1,value>>8)))
        expected=[bytearray(bank) for bank in memory.banks];writes=[]
        for address,value in operations:
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(70):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',index,linked))
        memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,path,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert memory.banks==expected and Counter(memory.writes)==Counter(writes),(cases,'RAM',path)
        counts[profile]+=1;paths[path]+=1;cases+=1
        if cases%131072==0:print(str(cases)+' linked vector cases passed',flush=True)
    assert cases==394240
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),all_six_word_domains=True,
        all_256_record_pointer_indices=True,all_256_current_link_codes=True,special_1A_ignores_prepared_pointer=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        cpu_stack_written=False,downstream_transform_executed=False,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkedVectorsVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

"""E761, полный индекс связи, специальный FF и три слова аргументов будущего расчёта."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceControlsPointRespawn import cp_flags,refresh


def profiles():
    for axis in range(3):
        for word in range(65536):
            values=[0x1234,0x7FFF,0x8000];values[axis]=word
            yield 1,tuple(values),1,'all_component_words'
    for index in range(256):
        for high in (1,128):yield index,(0x1234,0x7FFF,0x8000),high,'all_link_bytes'
    # Проверка полного байта доступности общего адреса A780 для особого FF и обычного индекса 1A.
    for index in (0x1A,0xFF):
        for high in range(256):yield index,(0x1234,0x7FFF,0x8000),high,'special_pointer_high_bytes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();special_highs={0x1A:set(),0xFF:set()}
    for index,values,requested_high,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        ix=0xA100;stack=0xBFFE;pointer=0xA780 if index==255 else 0xA100+64*index
        for axis,value in enumerate(values):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
        if index<26 or profile=='special_pointer_high_bytes':memory[pointer+1]=requested_high
        if profile=='special_pointer_high_bytes':
            assert pointer==0xA780
            special_highs[index].add(requested_high)
        memory[ix+11]=index;memory[stack],memory[stack+1]=255,63
        actual_values=[memory[ix+2*k]+256*memory[ix+2*k+1] for k in range(3)]
        high=memory[pointer+1]
        initial=get_registers({'PC':0xE761,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        wanted=list(initial);operations=[(0xE796,pointer&255),(0xE797,pointer>>8)]
        if index!=255:operations.extend(((stack-2,0x70),(stack-1,0xE7)))
        m1=11 if index==255 else 23
        if high==128:result_hl=pointer+1;path='unavailable'
        else:
            for address,value in zip((0xF1ED,0xF1F0,0xF1FE),actual_values):operations.extend(((address,value&255),(address+1,value>>8)))
            result_hl=actual_values[2];m1+=16;path='prepared'
        wanted[0:2]=[high,cp_flags(high,128)];wanted[6:8]=[result_hl>>8,result_hl&255]
        wanted[12],wanted[15],wanted[24]=stack+2,refresh(initial[15],m1),0x3FFF
        expected=[bytearray(bank) for bank in memory.banks];writes=[]
        for address,value in operations:
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(70):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',index))
        memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,index,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert memory.banks==expected and Counter(memory.writes)==Counter(writes),(cases,'RAM')
        counts[profile]+=1;paths[path]+=1;paths['special_ff' if index==255 else 'ordinary_index']+=1;cases+=1
    assert cases==197632
    assert all(values==set(range(256)) for values in special_highs.values())
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),all_three_component_word_domains=True,
        all_256_link_bytes=True,special_ff_maps_A780=True,real_index_conversion_executed=True,
        all_256_A780_high_bytes_for_ff_and_1A=True,special_ff_unavailable_ret_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        maximum_additional_stack_bytes=2,prepared_consumers_executed=False,
        all_input_products_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkedContextVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

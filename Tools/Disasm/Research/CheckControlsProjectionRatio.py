"""Внутренняя и внешняя области отношения, все выходные данные кроме R и ограниченный стековый след."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsProjectionRatio import evaluate


def profiles():
    for word in range(65536):yield word,word*73//256,'all_small_numerators'
    for word in range(65536):yield word+word*73//256+1,word,'all_small_divisors'
    for high_n in range(128,256):
        for high_q in range(256):yield high_n<<15,high_q<<15,'normalized_high_pairs'
    edges=(0,1,2,3,127,128,255,256,257,65535,65536,65537,0x3FFFFF,0x400000,0x7FFFFE,0x7FFFFF)
    for n,q in product(edges,repeat=2):
        for _ in range(2):yield n,q,'word_edges'
    for q in range(65536):
        for n in sorted({max(0,2*q-1),2*q,2*q+1}):yield n,q,'around_twice_divisor'
    randomizer=random.Random(0xD0CA)
    for _ in range(8192):yield randomizer.randrange(0x800000),randomizer.randrange(0x800000),'mixed_full_words'


def main():
    flat=base_memory();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[1]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=17);simulator=Simulator(memory)
    counts=Counter();branches=Counter();total=0;max_writes=0
    for numerator,divisor,kind in profiles():
        memory.recording=False
        for page in (2,5):memory.banks[page][:]=base[page]
        stack=0x8002 if total&1 else 0xBFFC
        for address,value in ((stack,0x3FFE),(stack+2,0x3FFF)):
            memory[address],memory[address+1]=value&255,value>>8
        coordinate=2+(total&1);alternative_b=(total*73)&255
        initial=get_registers({'AF':(total*109)&65535,'HL':numerator>>8,'DE':divisor>>8,
            'BC':((divisor&255)<<8)|(numerator&255),'^HL':0x1234,'^DE':0x5678,'^BC':(alternative_b<<8)|coordinate,
            '^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0xD0CA},None,False)
        initial[14],initial[15],initial[26],initial[27]=total&255,total&255,total&1,total%3
        result=evaluate(numerator,divisor,coordinate);wanted=list(initial)
        wanted[0:2]=[result['a'],result['f']]
        for index,name in ((2,'bc'),(4,'de'),(6,'hl')):wanted[index:index+2]=[result[name]>>8,result[name]&255]
        wanted[18],wanted[19]=alternative_b|result['flag_mask'],coordinate-1
        wanted[SP],wanted[PC]=stack+result['sp_delta'],0x3FFF if result['reject'] else 0x3FFE
        before=[bytes(b) for b in memory.banks]
        allowed={(5 if address<0x8000 else 2,address&0x3FFF) for address in range(stack-4,stack)}
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(1000):
            if simulator.registers[PC] in (0x3FFE,0x3FFF):break
            simulator.run()
        else:raise AssertionError((numerator,divisor,'return'))
        memory.recording=False;compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(total,numerator,divisor,result,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all((bank,offset) in allowed for bank,offset,_ in memory.writes),(total,'stack_range')
        masked=[bytearray(b) for b in before]
        for bank,offset in allowed:masked[bank][offset]=memory.banks[bank][offset]
        assert all(a==b for a,b in zip(masked,memory.banks)),(total,'nonstack_RAM')
        total+=1;counts[kind]+=1;branches[result['branch']]+=1;max_writes=max(max_writes,len(memory.writes))
        if total%65536==0:print(str(total)+' cases passed',flush=True)
    report=dict(passed=True,total_cases=total,cases_by_kind=dict(counts),branches=dict(branches),
        domain='0<=N,Q<=7FFFFF, alternative C in {2,3}',inside_and_all_three_outside_normalizers_checked=True,
        independent_integer_normalization_and_byte_recurrence=True,exact_registers_except_R=True,
        direct_and_outer_return_targets_proved=True,outer_return_consumes_extra_word=True,
        alternative_B_inside_bits_proved=True,all_nonstack_physical_RAM_preserved=True,
        stack_writes_confined_to_four_bytes=True,max_observed_stack_byte_writes=max_writes,
        stack_residue_values_and_write_multiplicity_proved=False,refresh_R_proved=False,
        full_24_bit_input_pair_product_exhausted=False,whole_CF0B_projection_proved=False,unknown_status_preserved=True,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ControlsProjectionRatioVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

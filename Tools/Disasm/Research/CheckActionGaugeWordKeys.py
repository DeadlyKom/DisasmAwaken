"""Полный домен слова для обоих входов, семи ограничений увеличения и всех пар запрет/опкод."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionGaugeWordKeys import evaluate


def profiles():
    for entry in (0x7680,0x76A3):
        for request in range(256):
            for opcode in range(256):yield entry,request,opcode,0x1357,0x88,'all_request_opcode_pairs'
    for word in range(65536):
        yield 0x76A3,0,58,word,0x88,'all_decrement_words'
        for limit in (0,1,0x88,0x7FFF,0x8000,0xFFFE,0xFFFF):yield 0x7680,0,58,word,limit,'all_increment_words_seven_limits'
    for limit in range(65536):yield 0x7680,0,58,(limit*73)&65535,limit,'all_limit_words'
    randomizer=random.Random(0x7680)
    for _ in range(8192):yield (0x7680,0x76A3)[randomizer.randrange(2)],randomizer.randrange(256),randomizer.randrange(256),randomizer.randrange(65536),randomizer.randrange(65536),'mixed_inputs'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks]
    simulator=Simulator(memory);counts=Counter();by_entry=Counter();paths=Counter();touched=set();costs=set()
    for entry,request,opcode,word,limit,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        stack=0xBFFE;old=serial&63;memory.out7ffd(old)
        setup={0x6F59:request,0x6E72:opcode,0xA78F:word&255,0xA790:word>>8,0x7693:limit&255,0x7694:limit>>8,
            0x669F:(serial*73)&255,stack:255,stack+1:63}
        for address,value in setup.items():memory[address]=value
        touched={(5 if a<0x8000 else 2,a&0x3FFF) for a in setup}
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        local=evaluate(initial,entry,request,opcode,word,limit);wanted=local['registers'];writes=[];expected={}
        for address,value in local['writes']:
            bank=5 if address<0x8000 else 2;offset=address&0x3FFF;writes.append((bank,offset,value));expected[bank,offset]=value
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(hex(entry),request,opcode,word,limit,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert Counter(writes)==Counter(memory.writes) and memory.o7ffd==old,(serial,'writes_or_page')
        assert all(memory.banks[b][o]==value for (b,o),value in expected.items()),(serial,'RAM')
        counts[kind]+=1;by_entry[hex(entry)]+=1;paths[hex(entry)+'_'+local['reason']]+=1;costs.add(local['refresh_m1'])
        if counts.total()%131072==0:print(str(counts.total())+' cases passed',flush=True)
    for address,value in setup.items():baseline[5 if address<0x8000 else 2][address&0x3FFF]=value
    for (bank,offset),value in expected.items():baseline[bank][offset]=value
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),cases_by_entry=dict(by_entry),paths=dict(paths),
        all_request_opcode_pairs_both_entries=True,all_decrement_words=True,all_increment_words_at_seven_limits=True,all_limit_words=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,no_cpu_stack_writes=True,
        increment_uses_sign_of_wrapped_difference=True,increment_ADD_keeps_SBC_sign_Z_and_PV=True,
        decrement_checks_low_bit4_for_negative_word=True,original_wraps_preserved=True,
        observed_m1=sorted(costs),complete_word_limit_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==729088
    (ROOT/'Tools/Disasm/Reports/ActionGaugeWordKeysVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

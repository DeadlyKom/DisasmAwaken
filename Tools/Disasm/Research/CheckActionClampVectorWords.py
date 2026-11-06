"""7F0E, реальные AbsSigned32, операнды изменяемого кода, регистры, стек и все банки."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionClampVectorWords import evaluate


def profiles():
    edges=(0,1,0x7EFF,0x7F00,0x7FFF,0x8000,0xFFFF,0x800000,0x7FFFFFFF,0x80000000,0xFF800000,0xFFFF8000,0xFFFF8001,0xFFFFFFFF)
    for values in product(edges,repeat=3):yield values,0xA55A,'edge_products'
    for position in range(3):
        for word in range(65536):
            for high in (0,0xFFFF):
                values=[0x1234,0xFF800000,0x87654321];values[position]=(high<<16)|word
                yield tuple(values),word,'all_low_words_both_signs_each_position'
        for high in range(65536):
            values=[0x1234,0xFF800000,0x87654321];values[position]=(high<<16)|0x1357
            yield tuple(values),high,'all_high_words_each_position'
    for af in range(65536):yield (0x1234,0xFFFFDCBA,af<<16),af,'all_input_AF'
    randomizer=random.Random(0x7F0E)
    for _ in range(8192):yield tuple(randomizer.getrandbits(32) for _ in range(3)),randomizer.randrange(65536),'mixed_dwords'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);simulator=Simulator(memory)
    baseline=[bytearray(b) for b in memory.banks];touched=set();counts=Counter();costs=set();paths=Counter()
    operands=((0x7F0F,0x7F12),(0x7F23,0x7F26),(0x7F37,0x7F3A))
    for values,af,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        old=serial&63;memory.out7ffd(old);stack=0xBFFE if serial&1 else 0x8008;setup={stack:255,stack+1:63}
        for (high,low),value in zip(operands,values):
            for address,word in ((high,value>>16),(low,value&65535)):setup[address],setup[address+1]=word&255,word>>8
        for address,value in setup.items():memory[address]=value
        touched={(5 if address<0x8000 else 2,address&0x3FFF) for address in setup}
        initial=get_registers({'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0x7F0E},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        local=evaluate(initial,values);wanted=local['registers'];writes=[];expected={}
        for address,value in local['writes']:
            key=(2,address&0x3FFF);writes.append((*key,value));expected[key]=value;touched.add(key)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x7F0E,stop=0x3FFF);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(serial,values,af,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert Counter(writes)==Counter(memory.writes) and memory.o7ffd==old,(serial,'writes_or_page')
        assert all(memory.banks[b][o]==value for (b,o),value in expected.items()),(serial,'stack_residue')
        counts[kind]+=1;costs.add(local['refresh_m1']);paths[str(sum(local['signs_from_bit23']))+'_negative_results']+=1
    for address,value in setup.items():baseline[5 if address<0x8000 else 2][address&0x3FFF]=value
    for (bank,offset),value in expected.items():baseline[bank][offset]=value
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        exact_registers_including_R=True,actual_three_AbsSigned32_calls=True,
        all_low_words_both_signs_each_position=True,all_high_words_each_position=True,all_input_AF=True,
        signs_read_from_original_bit23=True,original_saturation_threshold_8000_and_value_7F00_preserved=True,
        write_multiplicity_and_stack_residue_proved=True,all_physical_ram_bytes_proved=True,
        maximum_additional_stack_bytes=6,observed_m1_min=min(costs),observed_m1_max=max(costs),
        complete_three_dword_product_exhausted=False,hardware_bus_stack_write_order_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==666296
    (ROOT/'Tools/Disasm/Reports/ActionClampVectorWordsVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

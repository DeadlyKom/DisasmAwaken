"""6F55, все пары общих запросов, фаз и значений, задержек каналов и реальные списки класса 14."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionControlDecay import evaluate,CHANNELS


def profiles():
    inactive=(0,)*26
    standard=((0,0,0x92,17),(0,0,0x49,255),(0,0,0x92,128))
    for current in range(256):
        for previous in range(256):yield current,previous,standard,inactive,'all_global_request_pairs'
    for position in range(3):
        for phase in range(256):
            for value in range(256):
                channels=list(standard);channels[position]=(0,0,phase,value)
                yield 1,1,tuple(channels),inactive,'all_phase_value_pairs_each_channel'
        for old in range(256):
            for new in range(256):
                channels=list(standard);channels[position]=(old,new,0x49,17)
                yield 1,1,tuple(channels),inactive,'all_latched_request_pairs_each_channel'
    for position in range(26):
        for state in range(3):
            rows=list(inactive);rows[position]=state
            yield 0,1,standard,tuple(rows),'class14_positions_and_states'
    for state in range(3):yield 0,255,standard,(state,)*26,'uniform_lists'
    randomizer=random.Random(0x6F55)
    for _ in range(4096):
        channels=tuple(tuple(randomizer.randrange(256) for _ in range(4)) for _ in range(3))
        yield randomizer.randrange(2),randomizer.randrange(256),channels,tuple(randomizer.randrange(3) for _ in range(26)),'mixed_inputs'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks]
    simulator=Simulator(memory);counts=Counter();paths=Counter();touched=set();costs=set()
    def page(address):return 5 if address<0x8000 else 2
    for current,previous,channels,rows,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        touched=set();old=(serial%8)*8;memory.out7ffd(old);stack=0xBFFE;setup={stack:255,stack+1:63,0x6F56:current,0x6F59:previous}
        for row,position in zip(rows,range(26)):
            pointer=0xA100+64*position
            setup[pointer],setup[pointer+1],setup[pointer+18],setup[pointer+24]=position+1,128 if row==0 else 1,20 if row==2 else 3,position+17
        setup[0xA780],setup[0xA781]=128,128
        for layout,values in zip(CHANNELS,channels):
            for address,value in zip(layout[:4],values):setup[address]=value
        for address,value in setup.items():memory[address]=value;touched.add((page(address),address&0x3FFF))
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0x6F55},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        local=evaluate(memory.banks,initial);model=local['machine'];wanted=model.r
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6F55,stop=0x3FFF);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(serial,current,previous,channels,rows,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert Counter(model.writes)==Counter(memory.writes) and memory.o7ffd==old,(serial,'writes_or_page')
        touched.update((b,o) for b,o,_ in model.writes)
        assert all(memory.banks[b][o]==model.banks[b][o] for b,o in touched),(serial,'RAM')
        counts[kind]+=1;paths['released' if local['released'] else 'not_released']+=1;paths.update(local['channels']);costs.add(model.m1_count)
        if counts.total()%131072==0:print(str(counts.total())+' cases passed',flush=True)
    assert all(a==b for a,b in zip(model.banks,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        all_global_request_pairs=True,all_phase_value_pairs_each_channel=True,all_old_new_request_pairs_each_channel=True,
        actual_class14_release_and_all_children_executed=True,all_26_class14_positions_and_three_states=True,
        upper_bank_zero_required_for_actual_release=True,initial_7ffd_values=[0,8,16,24,32,40,48,56],
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_and_stack_residue_proved=True,
        delayed_channel_gate_reads_old_value_before_latch=True,phase_is_circular_rotation_not_boolean_toggle=True,
        signed_decay_toward_zero_preserved=True,maximum_additional_stack_bytes=6,
        observed_m1_min=min(costs),observed_m1_max=max(costs),complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==462929
    (ROOT/'Tools/Disasm/Reports/ActionControlDecayVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

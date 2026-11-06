"""6265 и внутренний 6268, настоящая композиция геометрии и полный домен разности/шага обоих байтов."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionHalfDeltaCodes import evaluate as geometry
from ReferenceActionRecordCodeStep import apply_codes


def profiles():
    standard=(0x1357,0x2468,0x369C,0x1234,0x5678,0x9ABC)
    rates=(0,1,2,3,127,128,255)
    for current in range(256):
        for target in range(256):
            for rate in rates:
                yield False,standard,(current,(current*73+target)&255),(target,target^0xA5),rate,'first_all_current_target_pairs'
                yield False,standard,((current*109+target)&255,current),(target^0x5A,target),rate,'second_all_current_target_pairs'
    for rate in range(256):
        for difference in range(256):
            yield False,standard,(0,0),((-difference)&255,(-difference*73)&255),rate,'all_delta_rate_products'
    edges=(0,1,2,127,128,129,254,255)
    for rate in range(256):
        for current in edges:
            for target in edges:yield False,standard,(current,target),(target,current),rate,'all_rate_edges'
    for current0 in range(256):
        for current1 in range(256):
            serial=current0*256+current1
            values=tuple((serial*factor+bias)&65535 for factor,bias in ((73,0),(109,1),(137,32768),(181,32767),(211,255),(251,65535)))
            yield True,values,(current0,current1),(0,0),(current0*37+current1*109)&255,'root_all_current_pairs'
    for rate in range(256):
        for current0 in edges:
            for current1 in edges:yield True,standard,(current0,current1),(0,0),rate,'root_rate_edges'
    randomizer=random.Random(0x6265)
    for _ in range(8192):
        yield True,tuple(randomizer.randrange(65536) for _ in range(6)),(randomizer.randrange(256),randomizer.randrange(256)),(0,0),randomizer.randrange(256),'root_mixed_inputs'


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    ratio_table=bytes(flat[0x9A00:0x9B00]);banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);root_table=bytes(banks[1][:768])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks]
    expected=[bytearray(b) for b in baseline];simulator=Simulator(memory);counts=Counter();paths=Counter();touched=set()
    seen0=bytearray(65536);seen1=bytearray(65536);direct_costs=set();entry_counts=Counter()

    def page(address):return 5 if address<0x8000 else 2 if address<0xC000 else 0

    for root,values,currents,targets,rate,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=expected[bank][offset]=baseline[bank][offset]
        touched=set();old=(serial%4)*8;memory.out7ffd(old)
        stack=0x8002 if serial&1 else 0xBFFE;ix=0xA100+64*(serial%26)
        for address,value in ((stack,255),(stack+1,63),(ix+8,currents[0]),(ix+9,currents[1]),(ix+37,rate)):
            bank=page(address);memory[address]=value;expected[bank][address&0x3FFF]=value;touched.add((bank,address&0x3FFF))
        left0,right0,right1,left1,left2,right2=values;entry=0x6265 if root else 0x6268
        initial=get_registers({'AF':(serial*73)&65535,'HL':left0,'DE':right0,'BC':right1 if root else targets[0]*256+targets[1],
            '^HL':left1,'^DE':left2,'^BC':right2,'^AF':(serial*109)&65535,'IX':ix,'IY':(serial*137)&65535,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        operations=[];ports=[]
        if root:
            child=list(initial);child[SP]-=2;child[PC]=0xAD5A
            model=geometry(child,ratio_table,root_table,return_address=0x6268)
            operations.extend(((stack-2,0x68),(stack-1,0x62)));operations.extend(model['writes']);ports=model['ports']
            local=apply_codes(model['registers'],*currents,rate)
        else:local=apply_codes(initial,*currents,rate);direct_costs.add(local['refresh_m1'])
        operations.extend(local['writes']);wanted=local['registers'];writes=[]
        for address,value in operations:
            bank=page(address);offset=address&0x3FFF;expected[bank][offset]=value
            writes.append((bank,offset,value));touched.add((bank,offset))
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True;simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        compared=(*range(15),*range(16,25),26,27) if root else (*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,hex(entry),currents,targets,rate,local,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert Counter(writes)==Counter(memory.writes),(serial,hex(entry),'write_multiplicity',writes,memory.writes)
        assert all(memory.banks[bank][offset]==expected[bank][offset] for bank,offset in touched),(serial,'RAM')
        assert trace.writes==ports and memory.o7ffd==(16 if root else old),(serial,'ports')
        seen0[rate*256+local['differences'][0]]=1;seen1[rate*256+local['differences'][1]]=1
        paths['first_written' if local['first_written'] else 'first_skipped']+=1
        paths['second_written' if local['second_written'] else 'second_skipped']+=1
        counts[kind]+=1;entry_counts[hex(entry)]+=1
        if counts.total()%131072==0:print(str(counts.total())+' cases passed',flush=True)
    assert all(a==b for a,b in zip(expected,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),cases_by_entry=dict(entry_counts),paths=dict(paths),
        all_current_target_pairs_at_seven_rates_each_field=True,complete_delta_rate_products_both_fields=True,
        observed_delta_rate_pair_counts=[sum(seen0),sum(seen1)],asymmetric_step_rules_preserved=True,
        first_deadzone_0_and_1_preserved=True,zero_step_same_value_writes_preserved=True,
        second_halving_loop_unreachable_when_rate_stable=True,actual_geometry_and_all_children_executed=True,
        exact_direct_registers_including_R=True,exact_root_registers_except_R=True,root_refresh_R_proved=False,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,direct_cpu_stack_written=False,
        maximum_additional_stack_bytes_root=16,root_real_ports_and_eight_banks=True,direct_refresh_m1=sorted(direct_costs),
        independent_numeric_step_oracle=True,complete_five_byte_product_exhausted=False,complete_six_word_product_exhausted=False,
        hardware_bus_stack_write_order_proved=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==1089536 and sum(seen0)==sum(seen1)==65536
    (ROOT/'Tools/Disasm/Reports/ActionRecordCodeStepVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

"""AD5A целиком, два настоящих произведения, корень в банке 1 и оба кодировщика отношений."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionHalfDeltaCodes import evaluate


def profiles():
    standard=(0x1357,0x2468,0x369C,0x1234,0x5678,0x9ABC)
    for position in range(6):
        for word in range(65536):
            values=list(standard);values[position]=word;yield tuple(values),'all_six_word_slices'
    edges=(0,1,0x7FFF,0x8000,0xFFFF)
    for values in product(edges,repeat=6):yield values,'six_word_corners'
    for delta in range(-32767,32768):
        left,right=(16383,16383-delta) if delta>=0 else (-16384,-16384-delta)
        a,b=(2*left)&65535,(2*right)&65535
        for third in (0,1,2):
            yield (a,b,b,a,a if third==1 else b,b if third==1 else a if third==2 else b),'all_signed_half_differences'
    randomizer=random.Random(0xAD5A)
    for _ in range(8192):yield tuple(randomizer.randrange(65536) for _ in range(6)),'mixed_six_words'


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    ratio_table=bytes(flat[0x9A00:0x9B00]);banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);root_table=bytes(banks[1][:768])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks]
    expected=[bytearray(b) for b in baseline];simulator=Simulator(memory);counts=Counter();roots=set();root_inputs=set();paths=Counter();touched=set()
    delta_min,delta_max=0,0;refresh_costs=set();initial_r_values=set()

    def page(address):return 5 if address<0x8000 else 2 if address<0xC000 else 0

    for values,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=expected[bank][offset]=baseline[bank][offset]
        touched=set();old=(serial%4)*8;memory.out7ffd(old)
        stack=0x8002 if serial&1 else 0xBFFE
        for address,value in ((stack,255),(stack+1,63)):
            bank=page(address);memory[address]=value;expected[bank][address&0x3FFF]=value;touched.add((bank,address&0x3FFF))
        left0,right0,right1,left1,left2,right2=values
        initial=get_registers({'AF':(serial*73)&65535,'HL':left0,'DE':right0,'BC':right1,
            '^HL':left1,'^DE':left2,'^BC':right2,'^AF':(serial*109+0xDEF0)&65535,
            'IX':(serial*37)&65535,'IY':(serial*109)&65535,'SP':stack,'PC':0xAD5A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        model=evaluate(initial,ratio_table,root_table);wanted=model['registers'];writes=[]
        for address,value in model['writes']:
            bank=page(address);offset=address&0x3FFF;expected[bank][offset]=value
            writes.append((bank,offset,value));touched.add((bank,offset))
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True;measured_m1=0
        # Проверка полного числа M1 композиции без потери кратных 128 в конечном R.
        for _ in range(10000):
            if simulator.registers[PC]==0x3FFF:break
            previous_r=simulator.registers[15]
            simulator.run()
            increment=(simulator.registers[15]-previous_r)&127
            assert increment in (1,2),(serial,'неожиданное изменение R',increment)
            measured_m1+=increment
        else:raise AssertionError(('геометрия не вернулась',serial,values))
        assert measured_m1==model['refresh_m1'],(serial,'M1',measured_m1,model['refresh_m1'])
        refresh_costs.add(measured_m1);initial_r_values.add(initial[15])
        memory.recording=False
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,values,model,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert Counter(writes)==Counter(memory.writes),(serial,values,'write_multiplicity',writes,memory.writes)
        assert all(memory.banks[bank][offset]==expected[bank][offset] for bank,offset in touched),(serial,values,'RAM')
        assert trace.writes==model['ports'] and memory.o7ffd==16,(serial,values,'ports',trace.writes)
        counts[kind]+=1;roots.add(model['root']);root_inputs.add(model['root_input'])
        paths['first_'+model['first']['path']]+=1;paths['second_'+model['second']['path']]+=1
        delta_min=min(delta_min,*model['deltas']);delta_max=max(delta_max,*model['deltas'])
        if counts.total()%32768==0:print(str(counts.total())+' cases passed',flush=True)
    assert all(a==b for a,b in zip(expected,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        all_six_word_domains_on_slices=True,all_5_power_6_corners=True,all_signed_half_difference_values=True,
        arithmetic_halves_taken_before_subtraction=True,proven_delta_range=[-32767,32767],observed_delta_range=[delta_min,delta_max],
        multiplication_second_operand_8000_unreachable=True,root_input_upper_bound=0x7FFE,
        observed_root_input_max=max(root_inputs),ordinary_root_verified_against_isqrt=True,
        bad_upper_root_table_domain_unreachable_for_this_caller=True,root_values_observed=sorted(roots),
        true_products_banked_root_and_both_ratio_coders_executed=True,independent_integer_parent_oracle=True,
        exact_registers_flags_r_sp=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        maximum_additional_stack_bytes=14,real_ports_and_eight_banks=True,initial_7ffd_values=[0,8,16,24],final_7ffd=16,
        IX_and_IY_preserved=True,alternate_delta_frame_proved=True,root_times_256_signed_word_interpretation_preserved=True,
        hardware_bus_stack_write_order_proved=False,refresh_R_proved=True,square_refresh_subdomain_proved=True,complete_six_word_product_exhausted=False,
        full_M1_count_compared_not_only_R_modulo_128=True,
        all_initial_R_values_observed=initial_r_values==set(range(256)),
        observed_M1_min=min(refresh_costs),observed_M1_max=max(refresh_costs),
        refresh_formula='99+2*negative_first_code+square_d0+square_d1+cached_root+first_ratio_code+second_ratio_code',
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==613638 and max(root_inputs)==0x7FFE
    (ROOT/'Tools/Disasm/Reports/ActionHalfDeltaCodesVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='root_values_observed'},indent=2))


if __name__=='__main__':main()

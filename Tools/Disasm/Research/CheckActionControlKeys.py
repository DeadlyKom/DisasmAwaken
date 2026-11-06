"""Шесть реальных клавиатурных входов, полный домен накопителя и значения каждого."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ActionControlKeyLayout import ENTRIES
from ReferenceActionControlKeys import evaluate


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks]
    simulator=Simulator(memory);counts=Counter();paths=Counter();touched=set();costs=set()
    for layout in ENTRIES:
        start,name,tag,channel,direction,step,limit,own,opposite,latch,address=layout
        for counter in range(256):
            for value in range(256):
                serial=counts.total();memory.recording=False
                for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
                stack=0xBFFE;old=serial&63;memory.out7ffd(old)
                setup={own:counter,opposite:(serial*73)&255,latch:(serial*109)&255,address:value,stack:255,stack+1:63}
                for pointer,byte in setup.items():memory[pointer]=byte
                touched={(5 if a<0x8000 else 2,a&0x3FFF) for a in setup}
                initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                    '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':start},None,False)
                initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
                local=evaluate(initial,layout,counter,value);wanted=local['registers'];writes=[];expected={}
                for pointer,byte in local['writes']:
                    bank=5 if pointer<0x8000 else 2;offset=pointer&0x3FFF;writes.append((bank,offset,byte));expected[bank,offset]=byte
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                simulator.run(start=start,stop=0x3FFF);memory.recording=False
                assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(hex(start),counter,value,
                    [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
                assert Counter(writes)==Counter(memory.writes) and memory.o7ffd==old,(serial,'writes_or_page')
                assert all(memory.banks[b][o]==byte for (b,o),byte in expected.items()),(serial,'RAM')
                counts[tag]+=1;paths[('overflow' if local['overflow'] else 'counter_only')+('_write' if local['written'] else '_preserve')]+=1;costs.add(local['refresh_m1'])
        print(name+' 65536 cases passed',flush=True)
    for pointer,byte in setup.items():baseline[5 if pointer<0x8000 else 2][pointer&0x3FFF]=byte
    for (bank,offset),byte in expected.items():baseline[bank][offset]=byte
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_entry=dict(counts),paths=dict(paths),
        complete_counter_value_products_all_six_entries=True,exact_registers_including_R=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,no_cpu_stack_writes=True,
        no_counter_overflow_no_value_write=True,original_sign_overflow_restart_preserved=True,
        opposite_counter_reset_C8_for_all_six_entries=True,all_64_paging_values_distributed=True,
        observed_m1=sorted(costs),initial_other_register_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==393216
    (ROOT/'Tools/Disasm/Reports/ActionControlKeysVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

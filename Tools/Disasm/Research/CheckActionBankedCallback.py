"""6CEF, точная граница косвенного JP, и 6D00, настоящий возврат через SelectMemoryPage."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks]
    simulator=Simulator(memory);counts=Counter();touched=set()
    for entry in (0x6CEF,0x6D00):
        for word in range(65536):
            for old in (0,16,32,35,56,59):
                serial=counts.total();memory.recording=False
                for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
                stack=0x8008 if serial&1 else 0xBFFE;memory.out7ffd(old)
                setup={stack:255,stack+1:63}
                for address,value in setup.items():memory[address]=value
                touched={(2,a&0x3FFF) for a in setup}
                initial=get_registers({'AF':word,'HL':word,'DE':0x2468,'BC':(word*109)&65535,
                    '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':word^0xA55A,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
                initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
                wanted=list(initial);writes=[];expected={}
                def put(address,value):
                    writes.append((2,address&0x3FFF,value));expected[2,address&0x3FFF]=value;touched.add((2,address&0x3FFF))
                if entry==0x6CEF:
                    wanted[0:2],wanted[16:18]=initial[16:18],initial[0:2];wanted[4:6]=[0x6D,0];wanted[10:12]=[0xA7,0x83]
                    wanted[12],wanted[24]=stack-2,word;wanted[15]=refresh(initial[15],16)
                    put(stack-2,0xF6);put(stack-1,0x6C);put(stack-4,initial[3]);put(stack-3,initial[2])
                    put(stack-2,0);put(stack-1,0x6D);page=19
                else:
                    wanted[0]=16;wanted[12],wanted[24]=stack+2,0x3FFF;wanted[15]=refresh(initial[15],9)
                    put(stack-2,5);put(stack-1,0x6D);put(stack-4,initial[3]);put(stack-3,initial[2]);page=16
                simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
                if entry==0x6CEF:
                    # Проверка только префикса и самого косвенного JP, произвольная цель не исполняется.
                    for _ in range(24):
                        if simulator.registers[24]==0x6CFF:break
                        simulator.run()
                    else:raise AssertionError('нет исходного JP (HL)')
                    simulator.run()
                else:simulator.run(start=entry,stop=0x3FFF)
                memory.recording=False
                assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(hex(entry),word,old,
                    [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
                assert Counter(writes)==Counter(memory.writes),(serial,'writes')
                assert all(memory.banks[b][o]==value for (b,o),value in expected.items()),(serial,'RAM')
                assert trace.writes==[(0x7FFD,page)] and memory.o7ffd==(old if old&32 else page),(serial,'ports')
                counts[hex(entry)]+=1
        print(hex(entry)+' '+str(counts[hex(entry)])+' cases passed',flush=True)
    for address,value in setup.items():baseline[2][address&0x3FFF]=value
    for (bank,offset),value in expected.items():baseline[bank][offset]=value
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_entry=dict(counts),
        every_HL_dispatch_target=True,every_AF_and_alternate_AF_value_in_dispatch=True,every_BC_value=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_and_stack_residue_proved=True,
        actual_SelectMemoryPage_executed=True,real_ports_and_lock_behaviour=True,initial_7ffd_values=[0,16,32,35,56,59],
        dispatch_stopped_after_indirect_jump=True,arbitrary_callback_not_executed=True,callback_semantics_proved=False,
        dispatch_refresh_m1=16,return_refresh_m1=9,maximum_additional_stack_bytes=4,
        complete_AF_alternate_AF_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==786432
    (ROOT/'Tools/Disasm/Reports/ActionBankedCallbackCombinedVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

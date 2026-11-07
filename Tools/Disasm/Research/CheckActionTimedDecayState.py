"""State07, полный декремент счётчика, деление байта и освобождение без временного стека."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from CheckActionMissileConsume import dec_flags
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);counts=Counter();cases=0
    for timer in range(256):
        for value in range(256):
            for carry in (0,1):
                memory.recording=False
                for page in (0,2,5):memory.banks[page][:]=baseline[page]
                ix=0xA100+64*(cases%26);stack=0xBFFE
                memory[ix+17],memory[ix+16]=timer,value;memory[stack],memory[stack+1]=255,63
                initial=get_registers({'PC':0xF66A,'SP':stack,'AF':0xA5FE|carry,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
                wanted=list(initial);new_timer=(timer-1)&255;operations=[(ix+17,new_timer)]
                if new_timer==0:
                    wanted[1]=dec_flags(timer,carry);wanted[24],wanted[12]=0x3FFF,stack+2;m1=10
                    operations.extend(((ix+1,128),(ix,0),(ix+24,255)));path='expired_reuse'
                elif value==0:
                    wanted[0:2]=[0,0x54];wanted[24]=0xF0F8;m1=7;path='zero_unchanged'
                else:
                    result=value>>1;wanted[0:2]=[result,logical_flags(result)|(value&1)]
                    wanted[24]=0xF0F8;m1=12;operations.append((ix+16,result));path='halve'
                wanted[15]=refresh(initial[15],m1);expected=[bytearray(bank) for bank in memory.banks];writes=[]
                for address,byte in operations:
                    bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                    expected[bank][address&0x3FFF]=byte;writes.append((bank,address&0x3FFF,byte))
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                for _ in range(30):
                    if simulator.registers[24]==wanted[24]:break
                    simulator.run()
                else:raise AssertionError(('нет выхода',timer,value,carry))
                memory.recording=False
                assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(timer,value,carry,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
                assert memory.banks==expected and Counter(memory.writes)==Counter(writes)
                counts[path]+=1;cases+=1
    assert cases==131072
    result=dict(passed=True,total_cases=cases,outcomes=dict(counts),all_timer_value_and_input_carry_products=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        actual_mark_record_child_executed=True,additional_stack_bytes=0,common_tail_executed=False,
        boundaries=[0x3FFF,0xF0F8],assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionTimedDecayStateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

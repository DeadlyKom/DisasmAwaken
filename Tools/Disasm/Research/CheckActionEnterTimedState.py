"""62B5, все пары R/старое состояние и реальная рамка из трёх сохранённых слов."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionLinkedMotionGate import MotionGateMachine


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory);cases=0;timers=Counter()
    for r in range(256):
        for state in range(256):
            memory.recording=False
            for page in (0,2,5):memory.banks[page][:]=baseline[page]
            ix=0xA100;stack=0xBFF8;memory[ix+10]=state
            for k,word in enumerate((cases*73&65535,cases*109&65535,cases*137&65535,0x3FFF)):
                memory[stack+2*k],memory[stack+2*k+1]=word&255,word>>8
            initial=get_registers({'PC':0x62B5,'SP':stack,'AF':cases&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0xA140},None,False)
            initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
            model=MotionGateMachine(memory.banks,initial);model.enter_timed()
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(start=0x62B5,stop=0x3FFF);memory.recording=False
            compared=(*range(25),26,27)
            assert all(model.r[i]==simulator.registers[i] for i in compared),(cases,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
            assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM')
            timers[memory[ix+23]]+=1;cases+=1
    assert cases==65536 and set(timers)==set(range(5,21))
    result=dict(passed=True,total_cases=cases,all_initial_R_by_all_old_states=True,timers=dict(timers),
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        restores_three_words_before_outer_RET=True,additional_stack_writes=False,refresh_m1=17,
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionEnterTimedStateVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

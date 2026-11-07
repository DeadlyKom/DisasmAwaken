"""EA00 и EA15, проверка полного класса и первого доступного байта списка A01C."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionRecordDistance import Recorded
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionRecordSearch import inc_flags
from ReferenceControlsPointRespawn import cp_flags,refresh

CLASSES=(0,4,5,8,1,9)


def main():
    memory=Recorded(flat_action());simulator=Simulator(memory);cases=0;counts=Counter();outcomes=Counter()
    def check(entry,code,flags,items):
        nonlocal cases
        memory.recording=False;ix=0xA100+64*(cases%26);stack=0xBFFE
        memory[ix+18]=code;memory[stack:stack+2]=[255,63]
        memory[0xA01C:0xA01C+len(items)]=items
        initial=get_registers({'PC':entry,'SP':stack,'AF':0xA500|flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            'IX':ix,'IY':0x5C3A,'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        wanted=list(initial);accepted=code in CLASSES
        compared=CLASSES.index(code)+1 if accepted else len(CLASSES)
        wanted[0:2]=[code,cp_flags(code,CLASSES[compared-1])];m1=2+2*compared;writes=[]
        if entry==0xEA15:
            writes=[(stack-2,0x18),(stack-1,0xEA)];m1+=2
            if not accepted:wanted[0:2]=[0,0x44];m1+=2;outcomes['unsupported_class']+=1
            else:
                cursor=0xA01C;m1+=1
                while memory[cursor]==255:cursor+=1;m1+=6
                value=memory[cursor];wanted[6:8]=[cursor>>8,cursor&255]
                if value==254:
                    wanted[0:2]=[254,cp_flags(254,254)];m1+=4;outcomes['terminator']+=1
                else:
                    wanted[0:2]=[value+1,inc_flags(value,1)];m1+=7;outcomes['candidate']+=1
        wanted[PC],wanted[SP],wanted[15]=0x3FFF,stack+2,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(300):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',entry,code,items))
        memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(entry,code,items,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert Counter(memory.writes)==Counter(writes) and all(memory[a]==v for a,v in writes)
        counts[hex(entry)]+=1;cases+=1
    # Проверка всех полных кодов класса и всех входных флагов, условные RET не используют прежние флаги.
    for code in range(256):
        for flags in range(256):check(0xEA00,code,flags,(254,))
    # Проверка раннего маркера, пропусков FF, нулевого индекса, последнего обычного байта FD и длинного пропуска.
    lists=((254,),(255,254),(0,254),(1,254),(253,254),(255,0,254),(255,255,253,254),
           (255,)*25+(254,),(255,)*25+(24,254),(127,128,254))
    for code in range(256):
        for items in lists:check(0xEA15,code,code^0xA5,items)
    for code in CLASSES:
        for value in range(256):check(0xEA15,code,value,(value,254))
    assert cases==69632 and counts['0xea00']==65536 and counts['0xea15']==4096
    result=dict(passed=True,total_cases=cases,cases_by_entry=dict(counts),outcomes=dict(outcomes),
        all_256_classes_by_256_input_flags=True,all_256_list_head_bytes_for_six_classes=True,
        exact_registers_flags_r_sp=True,all_ram_writes_compared=True,stack_bytes=2,
        all_candidate_indices_validated=False,all_possible_list_lengths_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionCandidateEligibilityVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

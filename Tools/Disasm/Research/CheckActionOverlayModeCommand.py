"""7480..74A2, все байтовые режимы и допуски, исходный код без сборки."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags


def comparison_flags(value,limit):
    result=(value-limit)&255
    return (result&128)|(limit&40)|(64 if result==0 else 0)|2|\
        (16 if (value^limit^result)&16 else 0)|(4 if (value^limit)&(value^result)&128 else 0)|(1 if value<limit else 0)


def main():
    baseline=flat_action();counts=Counter()
    def check(delay,equipment,mode):
        memory=Memory(baseline);memory[0xA85F]=delay;memory[0x9C25]=equipment;memory[0xAA9A]=mode
        memory[0xBFFE:0xC000]=[255,63];initial=get_registers({'PC':0x7480,'SP':0xBFFE,
            'AF':0xA5FF,'HL':0x1357,'DE':0x2468,'BC':0x369C,'^AF':0xDEF0,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        initial[14]=counts['cases']&255;initial[26]=counts['cases']&1;initial[27]=counts['cases']%3
        wanted=list(initial);wanted[PC]=0x3FFF;wanted[SP]=0xC000;expected=list(memory)
        if delay:
            wanted[:2]=[delay,and_flags(delay)];counts['delay_exit']+=1
        else:
            expected[0xA85F]=10
            if equipment==255:
                wanted[:2]=[0,0x50];counts['missing_equipment']+=1
            else:
                incremented=(mode+1)&255;result=incremented if incremented<4 else 1
                expected[0xAA9A]=result;expected[0xECA9:0xECAB]=[2,238]
                wanted[:2]=[result,comparison_flags(incremented,4)];wanted[6:8]=[238,2]
                counts['cycled']+=1
        sim=Simulator(memory);sim.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(30):
            if sim.registers[PC]==0x3FFF:break
            sim.run()
        else:raise AssertionError('нет возврата')
        memory.recording=False
        assert all(sim.registers[i]==wanted[i] for i in (*range(13),14,*range(16,24),PC,26,27)),(delay,equipment,mode,list(sim.registers),wanted)
        assert memory==expected
        assert not any(0xBFE0<=a<0xBFFE for a,v in memory.writes)
        counts['cases']+=1
    # Проверка всех значений задержки, полного кода оборудования и переполнения каждого режима.
    for delay in range(256):check(delay,254,2)
    for equipment in range(256):check(0,equipment,2)
    for mode in range(256):
        for equipment in (0,254,255):check(0,equipment,mode)
    result=dict(passed=True,total_cases=counts['cases'],counts=dict(counts),
        all_ram_checked=True,registers_except_R_and_T_checked=True,no_temporary_stack_writes=True,
        mode_255_wraps_to_zero=True,missing_equipment_still_sets_delay=True,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionOverlayModeCommandVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

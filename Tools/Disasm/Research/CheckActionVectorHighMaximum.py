"""699C, полный перебор трёх байтов, свёртка знака через CPL, максимум и точные AF/R."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh,cp_flags


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);memory[0xBFFE],memory[0xBFFF]=255,63
    baseline=[bytearray(b) for b in memory.banks];simulator=Simulator(memory)
    template=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,
        'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x699C},None,False)
    folded=tuple(value if value<128 else value^255 for value in range(256))
    flags=tuple(tuple(cp_flags(a,b) for b in range(128)) for a in range(128))
    count=0;costs=set()
    for first in range(256):
        memory.recording=False;memory[0x9B71]=first;x=folded[first]
        for second in range(256):
            memory.recording=False;memory[0x9B74]=second;y=folded[second];previous=max(x,y)
            prefix_m1=15+(first>>7)+(second>>7)+int(y>=x)
            for third in range(256):
                memory.recording=False;memory[0x9B77]=third;z=folded[third]
                # Расчёт математического максимума свёрнутых байтов, CPL не заменяется абсолютным значением.
                wanted=list(template);initial=list(template)
                initial[0:2]=[(first^second)&255,second]
                initial[14],initial[15],initial[26],initial[27]=first,((first*73)^(second*109)^third)&255,count&1,count%3
                wanted=list(initial);wanted[0:2]=[z,flags[z][previous]];wanted[7]=max(previous,z)
                m1=prefix_m1+(third>>7)+int(z>=previous)
                wanted[15]=refresh(initial[15],m1);wanted[SP],wanted[PC]=0xC000,0x3FFF
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                simulator.run(start=0x699C,stop=0x3FFF);memory.recording=False
                assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(first,second,third,m1,
                    [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
                assert not memory.writes,(first,second,third,'RAM_write')
                count+=1;costs.add(m1)
        if (first+1)%16==0:print(str(count)+' cases passed',flush=True)
    for address in (0x9B71,0x9B74,0x9B77):baseline[2][address&0x3FFF]=255
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=count,complete_three_byte_product_exhausted=True,
        independent_folded_maximum_oracle=True,CPL_not_NEG_preserved=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,
        no_memory_or_stack_writes_in_any_case=True,final_eight_banks_match_input_fixture=True,
        high_H_preserved=True,L_is_maximum=True,A_is_folded_third_byte=True,
        flags_from_comparison_of_third_with_previous_maximum=True,observed_m1=sorted(costs),
        game_units_and_role_proved=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert count==16777216
    (ROOT/'Tools/Disasm/Reports/ActionVectorHighMaximumVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

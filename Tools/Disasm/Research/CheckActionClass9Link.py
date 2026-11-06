"""65C6, особый код 0D сохраняет связь, остальные очищают её независимо от сравнения R с 70."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh,cp_flags


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory);count=0
    from itertools import chain
    profiles=chain(((value,r,(value+r)%26) for value in range(256) for r in range(256)),
                   ((value,(value*109+index)&255,index) for index in range(26) for value in range(256)))
    for value,r,index in profiles:
        ix=0xA100+64*index;memory.recording=False
        memory[ix+22]=value;memory[ix+10]=(count*37)&255;memory[ix+11]=(count*109)&255
        memory[0xBFFE],memory[0xBFFF]=255,63
        initial=get_registers({'AF':(count*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':ix,'IY':0x5C3A,'SP':0xBFFE,'PC':0x65C6},None,False)
        initial[14],initial[15],initial[26],initial[27]=count&255,r,count&1,count%3
        expected=[bytearray(b) for b in memory.banks];wanted=list(initial);writes=[]
        if value==13:a=13;flags=cp_flags(13,13);m1=7;updates=((ix+10,13),)
        else:
            a=refresh(r,6);flags=cp_flags(a,112);m1=12;updates=((ix+10,1),(ix+11,255))
        for address,byte in updates:expected[2][address&0x3FFF]=byte;writes.append((2,address&0x3FFF,byte))
        wanted[0:2]=[a,flags];wanted[15]=refresh(r,m1);wanted[SP],wanted[PC]=0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x65C6,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(value,r,index,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and memory.writes==writes
        count+=1
    report=dict(passed=True,total_cases=count,all_byte16_and_R_pairs=True,all_26_record_positions=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_order_and_multiplicity_proved=True,
        cpu_stack_written=False,code_13_preserves_linked_index=True,other_values_set_byte0A_1_and_linked_index_FF=True,
        R_comparison_affects_only_output_flags=True,read_R_after_m1=6,code13_refresh_m1=7,other_refresh_m1=12,
        general_game_meaning_of_bytes_0A_and_16_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionClass9LinkVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

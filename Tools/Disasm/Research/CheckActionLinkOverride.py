"""662B, FF запрещает копирование, любой иной байт записывается в LinkedIndex и выбирает код 02."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    count=0
    # Проверка всех сочетаний исходного байта и входного F, затем полного домена на каждом физическом IX.
    profiles=((value,flags,serial%26) for serial,(value,flags) in enumerate((v,f) for v in range(256) for f in range(256)))
    from itertools import chain
    profiles=chain(profiles,((value,(index*37+value)&255,index) for index in range(26) for value in range(256)))
    for value,flags,index in profiles:
        ix=0xA100+64*index;memory.recording=False
        memory[ix+21]=value;memory[ix+10]=(count*37)&255;memory[ix+11]=(count*109)&255
        memory[0xBFFE],memory[0xBFFF]=255,63
        initial=get_registers({'AF':((count*73)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':ix,'IY':0x5C3A,'SP':0xBFFE,'PC':0x662B},None,False)
        initial[14],initial[15],initial[26],initial[27]=count&255,count&255,count&1,count%3
        expected=[bytearray(b) for b in memory.banks];wanted=list(initial);writes=[]
        # Расчёт флагов INC для запрета и пары INC/DEC для копирования, Carry остаётся входным.
        if value==255:
            a=0;f=0x50|(flags&1);m1=4
        else:
            a=value;f=(value&0xA8)|(64 if value==0 else 0)|(16 if value&15==15 else 0)|(4 if value==127 else 0)|2|(flags&1);m1=10
            for address,byte in ((ix+11,value),(ix+10,2)):
                expected[2][address&0x3FFF]=byte;writes.append((2,address&0x3FFF,byte))
        wanted[0:2]=[a,f];wanted[15]=refresh(initial[15],m1);wanted[SP],wanted[PC]=0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x662B,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(count,value,flags,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and memory.writes==writes
        count+=1
    report=dict(passed=True,total_cases=count,all_override_bytes_and_input_F=True,all_26_record_positions=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_order_and_multiplicity_proved=True,
        cpu_stack_written=False,ff_is_no_override=True,non_ff_copied_to_linked_index=True,
        byte_0A_set_to_02_only_when_override_exists=True,general_game_meaning_of_byte_0A_and_source_15_proved=False,
        no_override_refresh_m1=4,override_refresh_m1=10,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkOverrideVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

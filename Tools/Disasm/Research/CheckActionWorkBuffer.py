"""Полное заполнение 3072 байтов через PUSH, все флаги, шесть обычных стеков, точные R/T."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);sim=Simulator(memory);cases=0
    for stack in (0xBFFE,0xBFFC,0x8CFE,0x9AFE,0xA0FE,0xFFFC):
        for flags in range(256):
            memory.recording=False
            for bank in (0,2):memory.banks[bank][:]=base[bank]
            memory.banks[2][:3072]=bytes((i*37+flags)&255 for i in range(3072))
            memory[stack],memory[stack+1]=255,63
            initial=get_registers({'AF':((flags*73+cases//256*41)&255)*256+flags,'HL':0x1357,'DE':0x2468,
                'BC':0x3600+((flags*19+cases//256*31)&255),'IX':0xABCD,'IY':0x5C3A,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':stack,'PC':0xD10A},None,False)
            initial[14],initial[15],initial[26],initial[27]=flags,flags,flags&1,flags%3
            expected=[bytearray(b) for b in memory.banks];writes=[]
            # Проверка единственного операнда CPU SP и полного диапазона нисходящих PUSH.
            expected[0][0x1129:0x112B]=bytes((stack&255,stack>>8))
            writes.extend(((0,0x1129,stack&255),(0,0x112A,stack>>8)))
            expected[2][:3072]=bytes([255])*3072
            writes.extend((2,i,255) for i in range(3072))
            wanted=list(initial);wanted[2]=0;wanted[6:8]=[255,255]
            wanted[SP],wanted[PC]=stack+2,0x3FFF;wanted[15]=refresh(initial[15],1639)
            sim.registers[:]=initial;memory.writes=[];memory.recording=True
            sim.run(start=0xD10A,stop=0x3FFF);memory.recording=False
            compared=(*range(16),*range(16,24),PC,26,27)
            assert all(wanted[i]==sim.registers[i] for i in compared),(hex(stack),flags,[(i,wanted[i],sim.registers[i]) for i in compared if wanted[i]!=sim.registers[i]])
            assert sim.registers[25]-initial[25]==18206
            assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(writes)==Counter(memory.writes)
            cases+=1
    report=dict(passed=True,total_cases=cases,all_flags_values=True,all_A_and_C_values_covered=True,
        cpu_stack_locations=6,buffer_start=0x8000,buffer_end_exclusive=0x8C00,filled_bytes=3072,
        original_write_value=255,exact_registers_flags_R_SP=True,all_physical_ram_bytes_proved=True,
        write_multiplicity_proved=True,saved_sp_operand=0xD129,refresh_m1=1639,uncontended_tstates=18206,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionWorkBufferVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

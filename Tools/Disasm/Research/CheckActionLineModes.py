"""Два настоящих подготовителя режимов линии, граница перед чтением индексов точек."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import cp_flags

ENTRIES=((0xDC2E,0xDC55),(0xDD7C,0xDDA3))


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);s=Simulator(m);counts=Counter()
    for entry,end in ENTRIES:
        for header in range(256):
            for count in range(2,16):
                m.recording=False;m[0xA0FF]=header
                serial=counts.total()
                initial=get_registers({'AF':serial&65535,'HL':0xA0FF,'DE':0x2468,'BC':count*256+(serial&255),'IX':0xABCD,'IY':0x5C3A,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':entry},None,False)
                initial[14],initial[26],initial[27]=serial&255,serial&1,serial%3
                mode=header&0x30
                opcode,branch,offset=(0xA1,0x30,0x18) if mode==0 else (0xB1,0x38,0x10) if mode==0x10 else (0xA9,0x38,0x10)
                flags=0x54 if mode==0 else cp_flags(mode,0x10)
                wanted=list(initial);wanted[0:2]=[offset,flags];wanted[2]=count-1;wanted[4:8]=[branch,opcode,0xA1,0]
                wanted[PC]=end
                expected=[bytearray(b) for b in m.banks];writes=[]
                for bank,index,value in ((2,0xD4E,opcode),(2,0xD4F,branch),(0,0x1E0F,offset)):
                    expected[bank][index]=value;writes.append((bank,index,value))
                s.registers[:]=initial;m.writes=[];m.recording=True
                for _ in range(20):
                    if s.registers[PC]==end:break
                    s.run()
                else:raise AssertionError('граница подготовки режима')
                m.recording=False
                compared=(*range(13),14,*range(16,24),PC,26,27)
                assert all(wanted[i]==s.registers[i] for i in compared),(hex(entry),header,count,[(i,wanted[i],s.registers[i]) for i in compared if wanted[i]!=s.registers[i]])
                assert all(a==b for a,b in zip(expected,m.banks)) and Counter(writes)==Counter(m.writes)
                counts[format(entry,'04X')]+=1
    report=dict(passed=True,total_cases=counts.total(),entries=dict(counts),all_header_bytes=True,counts_2_to_15=True,
        numeric_mode_bits_5_4=True,mode_20_and_30_both_xor=True,exact_registers_flags_except_R=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,no_cpu_stack_writes=True,
        full_parent_procedures_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLineModesVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

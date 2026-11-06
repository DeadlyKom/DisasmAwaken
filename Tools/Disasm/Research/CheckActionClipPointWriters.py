"""Четыре условных угла и общий писатель пары, перенос INC L и входной Carry сохраняются."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionVertexCodes import logic_flags
from ReferenceControlsPointRespawn import refresh

CORNERS=((0xC641,0),(0xC64C,255),(0xC657,0x5F00),(0xC662,0x5FFF))


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=banks,out7ffd=16);s=Simulator(m);counts=Counter()
    def check(entry,pair,offset,block,carry):
        m.recording=False;m[0x9BA3]=offset;m[0xCF03]=block;m[0xCF1B]=pair&255;m[0xCF1D]=pair>>8
        m[0xBFFE],m[0xBFFF]=255,63
        initial=get_registers({'AF':0xA55C|carry,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':entry},None,False)
        initial[15]=counts.total()&255
        wanted=list(initial);expected=[bytearray(b) for b in m.banks];writes=[]
        blocked=entry!=0xC6D3 and bool(block)
        if blocked:
            wanted[0:2]=[block,logic_flags(block)|16];m1=3
        else:
            following=(offset+2)&255;previous=(following-1)&255
            flags=(following&0xA8)|(64 if following==0 else 0)|(16 if previous&15==15 else 0)|(4 if previous==127 else 0)|(carry if entry==0xC6D3 else 0)
            wanted[0:2]=[following,flags];wanted[4:8]=[pair>>8,pair&255,0x90,following]
            for address,value in ((0x9000+offset,pair&255),(0x9000+((offset+1)&255),pair>>8),(0x9BA3,following)):
                expected[2][address&0x3FFF]=value;writes.append((2,address&0x3FFF,value))
            m1=14 if entry==0xC6D3 else 15
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        s.registers[:]=initial;m.writes=[];m.recording=True;s.run(start=entry,stop=0x3FFF);m.recording=False
        compared=(*range(16),*range(16,24),PC,26,27)
        assert all(wanted[i]==s.registers[i] for i in compared),(hex(entry),pair,offset,block,carry,[(i,wanted[i],s.registers[i]) for i in compared if wanted[i]!=s.registers[i]])
        assert all(a==b for a,b in zip(expected,m.banks)) and Counter(writes)==Counter(m.writes)
        counts[format(entry,'04X')]+=1
    # Проверка каждого упакованного конца ребра при обоих входных Carry.
    for pair in range(65536):
        for carry in (0,1):check(0xC6D3,pair,(pair*73)&255,0,carry)
    # Проверка всех сочетаний байта запрета углов и выходного смещения для каждого угла.
    for entry,pair in CORNERS:
        for block in range(256):
            for offset in range(256):check(entry,pair,offset,block,offset&1)
    report=dict(passed=True,total_cases=counts.total(),entries=dict(counts),all_endpoint_pairs_and_carry_values=True,
        all_corner_block_and_output_offset_pairs=True,exact_registers_flags_refresh_sp=True,
        every_physical_ram_byte_and_write_multiplicity_checked=True,blocked_path_no_writes=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipPointWritersVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

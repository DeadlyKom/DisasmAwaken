"""Четыре сравнения полных произведений и две разности координат, точный заём и флаги."""
from collections import Counter
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckSignedMultiply import sbc16_flags
from ReferenceControlsPointRespawn import refresh

PRODUCTS=((0xC66D,0xCF37,0xCF2F),(0xC681,0xCF37,0xCF2B),(0xC695,0xCF33,0xCF2F),(0xC6A9,0xCF33,0xCF2B))
DELTAS=((0xC6BD,0xCF1B,0xCF0B),(0xC6C8,0xCF1D,0xCF0D))


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=banks,out7ffd=16);s=Simulator(m);counts=Counter()
    def check(entry,first_address,second_address,first,second,wide):
        m.recording=False
        for address,value in ((first_address,first),(second_address,second)):
            for i in range(4 if wide else 2):m[address+i]=(value>>(8*i))&255
        m[0xBFFE],m[0xBFFF]=255,63
        serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':entry},None,False)
        initial[15]=serial&255
        wanted=list(initial)
        if wide:
            borrow=int((first&65535)<(second&65535));result=((first>>16)-(second>>16)-borrow)&65535
            wanted[1]=sbc16_flags(first>>16,second>>16,borrow);wanted[2:4]=[second>>24,(second>>16)&255]
        else:
            result=(first-second)&65535;wanted[1]=sbc16_flags(first,second,0);wanted[4:6]=[second>>8,second&255]
        wanted[6:8]=[result>>8,result&255];wanted[15]=refresh(initial[15],12 if wide else 7)
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        s.registers[:]=initial;m.writes=[];m.recording=True;s.run(start=entry,stop=0x3FFF);m.recording=False
        compared=(*range(16),*range(16,24),PC,26,27)
        assert all(wanted[i]==s.registers[i] for i in compared),(hex(entry),first,second,[(i,wanted[i],s.registers[i]) for i in compared if wanted[i]!=s.registers[i]])
        assert not m.writes;counts[format(entry,'04X')]+=1
    rng=random.Random(0xC66D)
    for entry,a,b in PRODUCTS:
        # Проверка каждого младшего слова с независимыми старшими частями и переходами заёма.
        for value in range(65536):check(entry,a,b,((value^0x8000)<<16)|value,(((value*109)&65535)<<16)|((value*73)&65535),True)
        for first in (0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            for second in (0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF):check(entry,a,b,first,second,True)
        for _ in range(4096):check(entry,a,b,rng.randrange(1<<32),rng.randrange(1<<32),True)
    for entry,a,b in DELTAS:
        # Проверка каждого слова первой координаты против нуля, единицы и знаковых границ.
        for value in range(65536):
            for second in (0,1,32768,65535):check(entry,a,b,value,second,False)
    report=dict(passed=True,total_cases=counts.total(),entries=dict(counts),exact_registers_flags_refresh_sp=True,
        no_ram_writes=True,low_word_borrow_propagates_to_high=True,high_subtraction_overflow_not_corrected=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipComparisonsVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

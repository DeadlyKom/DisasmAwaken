"""Четыре настоящих помощника числителя пересечения и полный ACTION-умножитель."""
from collections import Counter
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceActionFaceOrientation import multiply

DETAILS=((0xC477,0xCF37,0),(0xC496,0xCF33,95),(0xC4B5,0xCF2F,0),(0xC4D4,0xCF2B,255))


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);s=Simulator(m);counts=Counter();defects=0
    def check(entry,output,bound,coordinates):
        nonlocal defects
        m.recording=False
        for address,value in zip((0xCF0B,0xCF1B,0xCF0D,0xCF1D),coordinates):m[address],m[address+1]=value&255,value>>8
        m[0xBFFE],m[0xBFFF]=255,63
        initial=get_registers({'AF':counts.total()&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':entry},None,False)
        x1,x2,y1,y2=coordinates
        left,right,bc=((y1-bound)&65535,(x1-x2)&65535,bound) if entry<0xC4B5 else ((y1-y2)&65535,(x1-bound)&65535,y2)
        result=multiply(left,right,bc,0xABCD)
        wanted=list(initial);wanted[0:2]=result['af']
        for pos,value in ((2,result['bc']),(4,result['low']),(6,result['high']),(8,result['ix'])):wanted[pos:pos+2]=[value>>8,value&255]
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        expected=[bytearray(b) for b in m.banks];writes=[]
        def word(address,value):
            bank=2 if address<0xC000 else 0
            for delta,byte in ((0,value&255),(1,value>>8)):
                expected[bank][(address+delta)&0x3FFF]=byte;writes.append((bank,(address+delta)&0x3FFF,byte))
        word(0xBFFC,entry+23);word(0xBFFA,result['stack_af'][0]*256+result['stack_af'][1])
        word(output,result['low']);word(output+2,result['high'])
        s.registers[:]=initial;m.writes=[];m.recording=True
        for _ in range(290):
            if s.registers[PC]==0x3FFF:break
            s.run()
        else:raise AssertionError('возврат числителя')
        m.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(wanted[i]==s.registers[i] for i in compared),(hex(entry),coordinates,[(i,wanted[i],s.registers[i]) for i in compared if wanted[i]!=s.registers[i]])
        assert all(a==b for a,b in zip(expected,m.banks)) and Counter(writes)==Counter(m.writes)
        counts[format(entry,'04X')]+=1;defects+=int(result['defect'])
    rng=random.Random(0xC477)
    for entry,output,bound in DETAILS:
        for position in range(4):
            for value in (0,1,95,96,127,255,256,32767,32768,65535):
                coordinates=[0x1357,0x2468,0x369C,0x47AD];coordinates[position]=value;check(entry,output,bound,coordinates)
        for _ in range(4096):check(entry,output,bound,[rng.randrange(65536) for _ in range(4)])
        for coordinates in ((32768,0,256,0),(0,32768,256,0),(32768,0,32768,0),(255,32767,0,32768)):
            check(entry,output,bound,coordinates)
    report=dict(passed=True,total_cases=counts.total(),entries=dict(counts),multiply_exception_hits=defects,
        original_children_executed=True,exact_registers_flags_except_R=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        stack_extra_bytes=4,all_joint_inputs_exhausted=False,refresh_and_timing_independently_checked=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipProductsVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

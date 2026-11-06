"""Граница диспетчера C941 перед JP (HL), табличные обработчики не подменяются и не исполняются."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionVertexCodes import logic_flags
from ReferenceControlsPointRespawn import cp_flags


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);s=Simulator(m);cases=0
    for first in range(256):
        for second in range(256):
            m.recording=False
            m.banks[0][:]=base[0];m.banks[2][:]=base[2]
            p0=bytes((0x13,0x57,0x24,0x68,first));p1=bytes((0x9B,0xDF,0xAC,0xE0,second))
            for i,v in enumerate(p0):m[0xCF0B+i]=v
            for i,v in enumerate(p1):m[0xCF1B+i]=v
            m[0xBFFE],m[0xBFFF]=255,63
            initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':0xC941},None,False)
            expected=[bytearray(b) for b in m.banks];writes=[]
            def byte(a,v):
                bank=2 if a<0xC000 else 0;expected[bank][a&0x3FFF]=v;writes.append((bank,a&0x3FFF,v))
            def word(a,v):byte(a,v&255);byte(a+1,v>>8)
            byte(0xCF03,1)
            if first==0xF0:
                byte(0xCF0F,second);byte(0xCF1F,first)
                word(0xCF1B,int.from_bytes(p0[:2],'little'));word(0xCF0B,int.from_bytes(p1[:2],'little'))
                word(0xCF1D,int.from_bytes(p0[2:4],'little'));word(0xCF0D,int.from_bytes(p1[2:4],'little'))
                first_code,second_code=second,first
            else:first_code,second_code=first,second
            byte(0x9BA3,0);index=((~first_code)&240)|(second_code&15)
            pointer=expected[0][0xF00+index]+256*expected[0][0x1000+index]
            for address in (0xBFFC,0xBFFA,0xBFF8):word(address,0xC993)
            wanted=list(initial);wanted[0:2]=[index,0x90];wanted[4:8]=[0xC9,0x93,pointer>>8,pointer&255]
            if first==0xF0:wanted[2]=0xF0
            wanted[SP],wanted[PC]=0xBFF8,pointer
            s.registers[:]=initial;m.writes=[];m.recording=True
            for _ in range(60):
                # Остановка перед косвенным переходом, даже если цель совпадёт с текущим кодом.
                if s.registers[PC]==0xC992:
                    s.run();break
                s.run()
            else:raise AssertionError('граница JP')
            m.recording=False
            compared=(*range(13),14,*range(16,24),PC,26,27)
            assert all(wanted[i]==s.registers[i] for i in compared),(first,second,[(i,wanted[i],s.registers[i]) for i in compared if wanted[i]!=s.registers[i]])
            assert all(a==b for a,b in zip(expected,m.banks)) and Counter(writes)==Counter(m.writes)
            cases+=1
    # Проверка общего хвоста на рамке из двух фиктивных возвратов и внешнего адреса.
    for count in range(256):
        m.recording=False;m[0x9BA3]=count
        for a,v in ((0xBFFA,0x93),(0xBFFB,0xC9),(0xBFFC,0x93),(0xBFFD,0xC9),(0xBFFE,255),(0xBFFF,63)):m[a]=v
        initial=get_registers({'HL':0x1357,'BC':0x369C,'DE':0x2468,'SP':0xBFFA,'PC':0xC993},None,False)
        s.registers[:]=initial;m.writes=[];m.recording=True
        s.run(start=0xC993,stop=0x3FFF);m.recording=False
        assert s.registers[0:2]==[count,cp_flags(count,4)]
        assert s.registers[4:8]==[0xC9,0x93,0x13,0x57] and s.registers[SP]==0xC000 and not m.writes
    report=dict(passed=True,total_cases=cases+256,all_code_pairs_to_dispatch_boundary=True,return_tail_counts=256,
        exact_dispatch_registers_flags_except_R=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        child_handlers_executed=False,whole_clipping_procedure_proved=False,unknown_status_preserved=True,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipDispatchVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

"""Внутренний вход E655, слово DE над внешним возвратом, полный домен сохранённого слова."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionOffsetRestore import cp_flags
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    for value in range(65536):
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        memory[0xA112]=value>>8
        for address,word in ((0xBFFC,value),(0xBFFE,0x3FFF),(0xE68C,0x8001),(0xE692,0x7FFF),(0xE698,0xA55A)):
            memory[address],memory[address+1]=word&255,word>>8
        initial=get_registers({'AF':value,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xA100,'IY':0x5C3A,'SP':0xBFFC,'PC':0xE655},None,False)
        initial[14],initial[15],initial[26],initial[27]=value&255,value&255,value&1,value%3
        wanted=list(initial);wanted[0:2]=[value>>8,cp_flags(value>>8)];wanted[4:6]=[value>>8,value&255]
        expected=[bytearray(b) for b in memory.banks];writes=[]
        if value>>8==0x14:
            for address,word in zip((0xE5B3,0xE5D2,0xE5ED),(0x8001,0x7FFF,0xA55A)):
                expected[0][address&0x3FFF],expected[0][(address+1)&0x3FFF]=word&255,word>>8
                writes.extend(((0,address&0x3FFF,word&255),(0,(address+1)&0x3FFF,word>>8)))
            wanted[6:8]=[0xA5,0x5A]
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],13 if value>>8==0x14 else 6),0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0xE655,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),value
        assert all(a==b for a,b in zip(expected,memory.banks)) and memory.writes==writes,value
    report=dict(passed=True,total_cases=65536,all_saved_DE_words=True,all_class_codes=True,
        full_DE_cross_class_product_exhausted=False,exact_registers_including_R=True,
        all_physical_ram_bytes_proved=True,write_order_and_multiplicity_proved=True,
        cpu_stack_written=False,real_restorer_executed=True,matched_class_refresh_m1=13,other_class_refresh_m1=6,
        independent_numeric_oracle=True,irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordWarningReturnVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

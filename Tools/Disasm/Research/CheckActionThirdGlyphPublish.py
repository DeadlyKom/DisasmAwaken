"""Публикация Output0/4, Output1/4 и знака Output2 в физический вход третьего знака."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def quarter(word):
    high=word>>8;signed_high=high-256 if high&128 else high
    shifted_high=(signed_high//4)&255;value=(word>>2)&255
    flags=(shifted_high&128)|(64 if not shifted_high else 0)|(4 if shifted_high.bit_count()%2==0 else 0)|(
        value&0x28)|((word>>1)&1)
    return value,flags,(shifted_high<<8)|(word&255)


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    cases=0
    for serial in range(65792):
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        first=serial&65535;second=(serial*73+17)&65535;third=(serial*109+0xA55A)&65535
        flags=(serial&255)&251 if serial<65536 else serial&255
        for address,value in ((0xD9B6,first),(0xD7C4,second),(0xD7A2,third),(0xBFFE,0x3FFF)):
            memory[address],memory[address+1]=value&255,value>>8
        initial=get_registers({'AF':((serial*37)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6CB4},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        expected=[bytearray(b) for b in memory.banks];wanted=list(initial);writes=[]
        if not flags&4:
            x,_,_=quarter(first);y,f,hl=quarter(second)
            for address,value in ((0x9B85,x),(0x9B84,y),(0x9B86,third>>8)):
                expected[2][address&0x3FFF]=value;writes.append((2,address&0x3FFF,value))
            wanted[0:2]=[third>>8,f];wanted[6:8]=[hl>>8,hl&255]
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],1 if flags&4 else 22),0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6CB4,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(serial,wanted,simulator.registers)
        assert all(a==b for a,b in zip(expected,memory.banks)) and memory.writes==writes,serial
        cases+=1
    report=dict(passed=True,total_cases=cases,all_words_in_both_quarter_fields=True,all_input_F=True,
        full_input_word_product_exhausted=False,independent_numeric_oracle=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_order_and_multiplicity_proved=True,
        no_CPU_stack_writes=True,overflow_gate_refresh_m1=1,publish_refresh_m1=22,
        third_glyph_physical_fields=['X','Y','SignSource'],irq_executed=False,native_execution=False,
        assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionThirdGlyphPublishVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

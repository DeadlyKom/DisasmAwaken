"""4355, независимое целочисленное умножение вместо серийного умножителя, таблица страницы 9300."""
from collections import Counter
import json,math,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def table_values():
    result=[];states=[];word=0
    for _ in range(256):
        result.append(((word+128)>>8)&255);number=65536+word;product=number*0x100B2
        states.append((word,number,product));word=(product>>16)&65535
    return result,word,states


def main():
    raw=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();baseline=flat_action();baseline[0x41BD:0x43FA]=raw[:0x23D]
    memory=Memory(baseline);simulator=Simulator(memory);table,final_word,states=table_values()
    def cost(a,b):return sum(2 if i.bytes[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in decoder(baseline).disassemble(a,b,'h'))
    setup=cost(0x435C,0x4371)-1;tail=cost(0x4385,0x438E)
    m1=cost(0x4355,0x435C)+sum(setup+bool(word&128)+24*15+2*number.bit_count()+tail for word,number,_ in states)+1
    for flags in range(256):
        memory.recording=False;memory[:]=baseline;memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':((flags^165)<<8)|flags,'HL':0x1357,'DE':(flags<<8)|0x68,'BC':0x369C,
            '^AF':flags*257,'^HL':0x1234,'^DE':((flags^255)<<8)|0x78,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x4355},None,False)
        initial[14],initial[15],initial[26],initial[27]=flags^51,flags,flags&1,flags%3
        wanted=list(initial);expected=list(memory);expected[0x9300:0x9400]=table
        product=states[-1][2];wanted[0:8]=[final_word&255,0x50|((product>>15)&1),0,178,flags,0,final_word>>8,final_word&255]
        wanted[8:10]=[0x93,0];wanted[18:24]=[0,(product>>15)&255,flags^255,0,((product<<1)>>8)&255,(product<<1)&255]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(0x4355,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(flags,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==[(0x9300+i,value) for i,value in enumerate(table)],flags
    errors=[table[i]-(256*2**(i/256)-256) for i in range(256)]
    report=dict(passed=True,total_cases=256,physical_table_bytes=256,
        exact_recurrence='w[0]=0; T[n]=round_half_up(w[n]/256) mod 256; w[n+1]=floor((65536+w[n])*65714/65536) mod 65536',
        final_word=final_word,refresh_m1=m1,maximum_additional_stack_bytes=0,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,
        min_error_from_256_pow2_minus_256=min(errors),max_error_from_256_pow2_minus_256=max(errors),
        table_is_approximate_exponential=True,consumer_ratio_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionExponentialTableVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

"""438F, независимая сумма точных частных для двух страниц, без сборки и без вызова загрузчика."""
from collections import Counter
import json,math,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory,xor_flags
from ReferenceControlsPointRespawn import refresh
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def table_values():
    values=[0xF000];acc=0;quotients=[]
    for index in range(1,256):
        values.append((acc>>8)&65535)
        quotient=0xB8AA*65536//(0x8000*index+0x3AE9);quotients.append(quotient);acc=(acc+quotient)&0xFFFFFF
    return values,acc,quotients


def main():
    raw=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();baseline=flat_action()
    baseline[0x41BD:0x43FA]=raw[:0x23D];memory=Memory(baseline);simulator=Simulator(memory)
    values,acc,quotients=table_values();assert (acc,quotients[-1])==(0x7FFED,370)
    def cost(a,b):return sum(2 if i.bytes[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in decoder(baseline).disassemble(a,b,'h'))
    setup,after=cost(0x439B,0x43B3),cost(0x43C5,0x43CE)
    m1=cost(0x438F,0x439B)+sum(setup+16*14+2*(16-q.bit_count())+after for q in quotients)+1
    for flags in range(256):
        memory.recording=False;memory[:]=baseline;memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':((flags^0xA5)<<8)|flags,'HL':0x1357,'DE':0x2468,'BC':(flags<<8)|(flags^255),
            '^AF':flags*257,'^HL':0x1234,'^DE':0x5678,'^BC':((flags^85)<<8)|(flags^170),
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x438F},None,False)
        initial[14],initial[15],initial[26],initial[27]=flags^51,flags,flags&1,flags%3
        wanted=list(initial);expected=list(memory);writes=[]
        def byte(a,v):expected[a]=v;writes.append((a,v))
        # Создание эталона таблицы и сохранений двух слов на CPU-стеке из суммы, без воспроизведения двоичного делителя.
        byte(0x9100,0);byte(0x9200,0xF0);running=0
        for index,value in enumerate(values[1:],1):
            byte(0x9100+index,value&255);byte(0x9200+index,value>>8)
            writes.extend(((0xBFFD,0x91),(0xBFFC,index),(0xBFFB,(running>>8)&255),(0xBFFA,running&255)))
            expected[0xBFFD],expected[0xBFFC],expected[0xBFFB],expected[0xBFFA]=0x91,index,(running>>8)&255,running&255
            running=(running+quotients[index-1])&0xFFFFFF
        remainder=0xB8AA*65536%(0x8000*255+0x3AE9)
        wanted[0:8]=[acc>>16,0x50,0,127,(acc>>8)&255,acc&255,0x91,0]
        wanted[16:24]=[remainder>>16,xor_flags(quotients[-1]>>8),0,127,0xBA,0xE9,(remainder>>8)&255,remainder&255]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(0x438F,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(flags,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(flags,Counter(memory.writes)-Counter(writes),Counter(writes)-Counter(memory.writes))
    errors=[values[n]-256*math.log2(n) for n in range(1,256)]
    report=dict(passed=True,total_cases=256,physical_table_bytes=512,table_zero=0xF000,
        exact_formula='T[1]=0; T[n]=floor(sum(floor(0xB8AA*65536/(0x8000*i+0x3AE9)), i=1..n-1)/256)',
        final_accumulator=acc,refresh_m1=m1,maximum_additional_stack_bytes=4,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
        min_error_from_256_log2=min(errors),max_error_from_256_log2=max(errors),
        table_is_approximate_logarithm=True,zero_entry_is_special=True,consumer_ratio_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLogarithmTableVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

"""Реальная цепочка 9100 и продолжение 6BED, полные эффекты выборок и оборачивания C."""
from collections import Counter
import json
from CheckIntro import ROOT,original_memory,execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP


def main():
    flat=original_memory();generated=original_memory()
    # Получение действительной цепочки построителем до таблиц фаз и ожиданий IRQ.
    execute(generated,{'PC':0x6C9C},stop=0x6CF9)
    template=flat[0x6D78:0x6D7E]
    chain=template*64;chain[-1:]=[0xC3,0xED,0x6B]
    assert generated[0x9100:0x9282]==chain
    flat[0x9100:0x9282]=chain
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    fixtures=[(rows,column,pattern,stack) for rows in range(1,39) for column in (0,64,128,192)
        for pattern in range(4) for stack in (0x5FFE,0xA0FE,0xA2FC)]
    # Проверка нестандартных младших адресов, где 63 INC C теряют перенос в старший байт.
    fixtures += [(rows,column,pattern,0x5FFE) for rows in (2,5) for column in range(256) for pattern in (0,3)]
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory);cases=0;crossed=0
    for rows,column,pattern,stack in fixtures:
        memory.recording=False
        for bank in (0,2,5):memory.banks[bank][:]=base[bank]
        memory.banks[0][:]=bytes((i*29+pattern*61+17)&255 for i in range(0x4000))
        memory[stack],memory[stack+1]=255,63
        for index in range(256):memory[0x9300+index]=(index*37+pattern*53)&255
        for row in range(rows):
            for col in range(64):
                pointer=0xAD00+row*128+col*2
                memory[pointer]=(row*29+col*17+pattern*7)&255
                memory[pointer+1]=0xC0+((row*3+col*5)&63)
        flags=cases&255
        initial=get_registers({'AF':((cases*73)&255)*256+flags,'HL':0xAD00,
            'DE':0x2468,'BC':0x8000+column,'IX':0xAB00+rows,'IY':0x5C3A,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
            'SP':stack,'PC':0x6BE3},None,False)
        initial[14],initial[26],initial[27]=flags,flags&1,flags%3
        expected=[bytearray(b) for b in memory.banks];writes=[]

        def put(address,value):
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value
            writes.append((bank,address&0x3FFF,value))

        put(0x6BF3,stack&255);put(0x6BF4,stack>>8)
        destination=0x8000+column
        # Расчёт адреса выборки из старшего байта слова и табличной замены младшего байта.
        for row in range(rows):
            for col in range(64):
                low=(row*29+col*17+pattern*7)&255
                high=0xC0+((row*3+col*5)&63)
                mapped=(low*37+pattern*53)&255
                source=high*256+mapped
                value=memory[source]
                put(destination,value)
                if col!=63:
                    if destination&255==255:crossed+=1
                    destination=(destination&0xFF00)|((destination+1)&255)
            destination=(destination+1)&65535
        wanted=list(initial)
        wanted[0:8]=[value,0x42|(flags&1),destination>>8,destination&255,high,mapped,0x93,low]
        wanted[9]=0;wanted[SP],wanted[PC]=stack+2,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6BE3,stop=0x3FFF);memory.recording=False
        # Проверка всех регистров кроме R, временный SP восстановлен без записей в CPU-стек.
        compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(rows,column,pattern,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(rows,column,pattern,'RAM')
        assert Counter(writes)==Counter(memory.writes),(rows,column,pattern,'writes')
        cases+=1
    report=dict(passed=True,total_cases=cases,aligned_cases=1824,unaligned_cases=1024,
        rows_domain=[1,38],columns_per_row=64,lookup_values_are_permutations=True,
        actual_generator_chain_verified=True,generated_code_bytes=386,
        actual_continuation_executed=True,all_initial_flags_values=True,
        all_C_values_for_unaligned_cases=True,discarded_C_carries_observed=crossed,
        cpu_stack_locations=3,cpu_stack_written=False,all_registers_except_R=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        independent_numeric_oracle=True,arbitrary_aliases_proved=False,
        zero_row_count_256_rows_proved=False,assembly_executed=False,
        native_execution=False,irq_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroPointerSamplerVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

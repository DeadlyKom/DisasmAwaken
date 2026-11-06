"""Шестнадцать строк через EXX, реальная цепочка 7E00 и последовательные перекрытия текстуры."""
from collections import Counter
import json
from CheckIntro import ROOT,original_memory,execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP


def main():
    flat=original_memory();generated=original_memory()
    # Проверка цепочки, построенной исходной инициализацией до разворачивания текстуры.
    execute(generated,{'PC':0x66FB},stop=0x670D)
    chain=flat[0x6722:0x6729]*64+[0xC3,0xF3,0x66]
    assert generated[0x7E00:0x7FC3]==chain
    flat[0x7E00:0x7FC3]=chain
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory);cases=0;alias_cases=0
    for flags in range(256):
        for destination_page in (0x40,0x80,0x90,0xA0,0xB0):
            for offset in (0x8000,0x9F01,0xBF3F):
                memory.recording=False
                for bank in (0,2,5):memory.banks[bank][:]=base[bank]
                # Создание изменяющейся текстуры, в том числе с будущим перекрытием назначением B0..BF.
                memory.banks[2][0x3000:]=bytes((i*29+flags*73+17)&255 for i in range(4096))
                start=((0xD0 if cases&1 else 0xF0)<<8)+(0,0x40,0x80)[cases%3]
                stack=(0x6000,0x5BFE)[cases&1]
                memory[stack],memory[stack+1]=255,63
                memory[0x66EC],memory[0x66ED]=offset&255,offset>>8
                for row in range(16):
                    for col in range(64):
                        address=start+256*row+2*col
                        value=((0x30+((row*3+col*5)&15))<<8)|((row*29+col*17+flags)&255)
                        memory[address],memory[address+1]=value&255,value>>8
                initial=get_registers({'AF':((flags*19)&255)*256+flags,'HL':start,
                    'DE':0x2468,'BC':0xAB00+flags,'IX':0xCDEF,'IY':0x5C3A,
                    '^HL':0xFEDC,'^DE':destination_page*256+0x73,'^BC':0x7654,
                    '^AF':0x3210,'SP':stack,'PC':0x66E2},None,False)
                initial[14],initial[26],initial[27]=flags,flags&1,flags%3
                expected=[bytearray(b) for b in memory.banks];writes=[];written=set();alias=False

                def read(address):
                    bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                    return expected[bank][address&0x3FFF]

                def put(address,value):
                    bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                    expected[bank][address&0x3FFF]=value
                    writes.append((bank,address&0x3FFF,value));written.add(address)

                put(0x66F8,stack&255);put(0x66F9,stack>>8)
                # Расчёт каждой выборки по уже изменённой RAM, без снимка всех источников до переноса.
                for row in range(16):
                    for col in range(64):
                        raw=((0x30+((row*3+col*5)&15))<<8)|((row*29+col*17+flags)&255)
                        summed=(raw+offset)&65535;source=summed&0xBFFF
                        alias |= source in written
                        value=read(source)
                        put((destination_page+row)*256+0xC0+col,value)
                final_d=(destination_page+16)&255
                final_flags=(final_d&0xA8)|(0x40 if final_d==0 else 0)|(0x10 if final_d&15==0 else 0)|(4 if final_d==128 else 0)
                wanted=list(initial)
                wanted[0:2]=[value,final_flags]
                wanted[2]=0;wanted[6:8]=[((start>>8)+16)&255,start&255]
                wanted[18:24]=[offset>>8,offset&255,final_d,0,source>>8,source&255]
                wanted[SP],wanted[PC]=stack+2,0x3FFF
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                simulator.run(start=0x66E2,stop=0x3FFF);memory.recording=False
                # Проверка двух регистровых наборов, полного временного SP и кратности записей всех банков.
                compared=(*range(15),*range(16,25),26,27)
                assert all(wanted[i]==simulator.registers[i] for i in compared),(flags,destination_page,offset,
                    [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
                assert all(a==b for a,b in zip(expected,memory.banks)),(flags,destination_page,offset,'RAM')
                assert Counter(writes)==Counter(memory.writes),(flags,destination_page,offset,'writes')
                alias_cases+=alias;cases+=1
    report=dict(passed=True,total_cases=cases,rows_per_call=16,columns_per_row=64,
        actual_generator_chain_verified=True,generated_code_bytes=451,
        actual_continuation_executed=True,table_start_pages=[208,240],table_start_lows=[0,64,128],
        destination_start_pages=[64,128,144,160,176],source_offsets=[32768,40705,48959],
        source_words_high_domain=[48,63],all_initial_flags_values=True,
        sequential_source_alias_cases=alias_cases,cpu_stack_locations=2,cpu_stack_written=False,
        all_registers_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        independent_numeric_oracle=True,arbitrary_word_and_offset_domain_proved=False,
        assembly_executed=False,native_execution=False,irq_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroScrolledSamplerVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

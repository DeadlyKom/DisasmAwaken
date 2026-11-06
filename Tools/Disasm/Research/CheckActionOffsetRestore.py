"""Сохранение и временное деление трёх слов, полный восстановитель E685, все 16-битные значения."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh

ACTIVE=(0xE5B3,0xE5D2,0xE5ED)
ORIGINAL=(0xE68C,0xE692,0xE698)


def cp_flags(value):
    result=(value-0x14)&255
    return 2|(result&128)|(64 if result==0 else 0)|(16 if (value^0x14^result)&16 else 0)|(
        4 if (value^0x14)&(value^result)&128 else 0)|int(value<0x14)


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory);cases=0

    def begin(code,serial):
        memory.recording=False
        for bank in (0,2,5):memory.banks[bank][:]=base[bank]
        memory[0xA112]=code;memory[0xBFFE],memory[0xBFFF]=255,63
        initial=get_registers({'AF':((serial*73)&255)*256+(serial&255),'HL':0x1357,
            'DE':0x2468,'BC':0x369C,'^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,
            '^AF':0x3210,'IX':0xA100,'IY':0x5C3A,'SP':0xBFFE,'PC':0xE685},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        return initial

    def execute(initial,wanted,expected,writes,start,stop):
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=start,stop=stop);memory.recording=False
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(hex(start),cases,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(hex(start),cases,'RAM')
        assert memory.writes==writes,(hex(start),cases,'write_order',memory.writes,writes)

    # Проверка всех исходных слов, два других слова являются независимыми перестановками того же домена.
    for word in range(65536):
        values=(word,(word*73+17)&65535,word^65535)
        initial=begin(0x14,word)
        for address,value in zip(ACTIVE,values):memory[address],memory[address+1]=value&255,value>>8
        expected=[bytearray(b) for b in memory.banks];writes=[]

        def put(address,value):expected[0][address&0x3FFF]=value;writes.append((0,address&0x3FFF,value))

        def put_word(address,value):put(address,value&255);put(address+1,value>>8)

        put_word(0xE605,0xBFFE)
        # Числовое арифметическое деление, знаковый бит копируется без округления к нулю.
        for source,destination,value in zip(ACTIVE,ORIGINAL,values):
            put_word(destination,value)
            put_word(source,(value>>1)|(value&0x8000))
        last_half=(values[2]>>1)|(values[2]&0x8000);low=last_half&255
        flags=(low&0xA8)|(64 if low==0 else 0)|(4 if low.bit_count()%2==0 else 0)|(values[2]&1)
        wanted=list(initial);wanted[0:2]=[0x14,flags];wanted[6:8]=[last_half>>8,last_half&255]
        wanted[15],wanted[PC]=refresh(initial[15],27),0xE58E
        execute(initial,wanted,expected,writes,0xE55C,0xE58E)
        previous=list(simulator.registers);previous[PC]=0xE685
        writes=[]
        for address,value in zip(ACTIVE,values):put_word(address,value)
        wanted=list(previous);wanted[0:2]=[0x14,0x42];wanted[6:8]=[values[2]>>8,values[2]&255]
        wanted[15],wanted[SP],wanted[PC]=refresh(previous[15],11),0xC000,0x3FFF
        execute(previous,wanted,expected,writes,0xE685,0x3FFF)
        cases+=1
    # Проверка точного полного кода класса, остальные 255 значений не записывают слова.
    for code in range(256):
        initial=begin(code,code);expected=[bytearray(b) for b in memory.banks];writes=[]
        wanted=list(initial);wanted[0:2]=[code,cp_flags(code)]
        if code==0x14:
            for address in ACTIVE:
                for delta in (0,1):expected[0][(address+delta)&0x3FFF]=0;writes.append((0,(address+delta)&0x3FFF,0))
            wanted[6:8]=[0,0]
        wanted[15]=refresh(initial[15],11 if code==0x14 else 4)
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        execute(initial,wanted,expected,writes,0xE685,0x3FFF)
        cases+=1
    report=dict(passed=True,total_cases=cases,all_word_values_in_each_field=True,
        paired_halving_and_restore_cases=65536,all_256_class_codes=True,
        actual_preparation_prefix_executed=True,prefix_entry=0xE55C,prefix_stop=0xE58E,
        whole_E55C_function_proved=False,whole_restorer_proved=True,
        exact_arithmetic_signed_halving=True,original_offsets_restored=True,
        all_registers_including_R=True,prefix_refresh_m1=27,matched_class_refresh_m1=11,other_class_refresh_m1=4,
        all_physical_ram_bytes_proved=True,write_order_and_multiplicity_proved=True,
        cpu_stack_written=False,independent_numeric_oracle=True,
        all_three_word_combinations_exhausted=False,irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionOffsetRestoreVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

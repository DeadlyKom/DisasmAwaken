"""Полные флаги, альтернативные пары, стек и R BCD-вывода при любых тетрадах."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusicGateTicks import Memory
from CheckMusic import Simulator,get_registers
from ReferenceControlsBcdExact import evaluate


def profiles():
    # Проверка каждого входного байта и каждой экранной колонки настоящего вывода тетрады.
    for value in range(256):
        for column in range(256):yield 0xF188,value,column,0x1357,0x2468,0x369C,'all_nibble_bytes_and_columns'
    # Проверка всех масок продолжения и каждого байта в каждой из четырёх пар, включая не-BCD тетрады.
    for pair in range(4):
        for byte in range(256):
            for mask in range(256):
                values=[0x12,0x34,0x56,0x78];values[pair]=byte
                yield 0xF142,None,None,(values[1]<<8)|values[0],(values[3]<<8)|values[2],(mask<<8)|0x9C,'all_pair_masks_and_bytes'
    randomizer=random.Random(0xF142)
    # Проверка смешанных содержимых пар и фоновых байтов.
    for _ in range(4096):yield 0xF142,None,None,randomizer.randrange(65536),randomizer.randrange(65536),randomizer.randrange(65536),'mixed_counters'


def main():
    base=base_memory();memory=Memory(base);simulator=Simulator(memory);counts=Counter();touched=set();costs=set()
    for entry,value,column,hl,de,bc,kind in profiles():
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=base[address]
        # Создание независимого фона всех затрагиваемых строк без изменения кода и шрифтовой таблицы.
        for high in range(0x51,0x57):memory[high<<8:(high+1)<<8]=[(low*73+serial*31+high)&255 for low in range(256)]
        stack=(0x9008,0xBFFE)[serial&1];memory[stack:stack+2]=[255,63]
        initial=get_registers({'HL':hl,'DE':de,'BC':bc if column is None else (bc&0xFF00)|column,'AF':((value if value is not None else serial)&255)*256+(serial&255),
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted,writes,m1=evaluate(memory,initial,value,column);before=list(memory)
        for address,result in writes:before[address]=result
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,hex(entry),value,column,hl,de,bc,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==before and Counter(writes)==Counter(memory.writes),(serial,'RAM_or_multiplicity')
        touched={address for address,_ in writes};counts[kind]+=1;costs.add(m1)
        if counts.total()%65536==0:print(str(counts.total())+' cases passed',flush=True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),exact_registers_including_R=True,
        all_nibble_bytes_and_columns=True,all_pair_masks_and_each_byte_each_position=True,non_BCD_tetrads_preserved=True,
        every_flat_RAM_byte_proved=True,write_multiplicity_proved=True,original_children_without_stubs=True,
        observed_m1_min=min(costs),observed_m1_max=max(costs),complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ControlsBcdExactVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

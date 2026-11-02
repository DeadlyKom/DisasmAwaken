"""DAB9, пропуск младшего байта, маска старшего и прямой допуск ниже 0A."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh,cp_flags


def logical_flags(a):
    return (a&0xA8)|(0x40 if a==0 else 0)|(4 if a.bit_count()%2==0 else 0)


def main():
    memory=Memory(base_memory())
    simulator=Simulator(memory)
    memory[0xBFFE:0xC000]=[0xFF,0x3F]
    counts,outcomes=Counter(),Counter()

    def check(iy,kind):
        other=(iy+3)&65535
        a=memory[0x7002]&127
        b=memory[(other+2)&65535]&127
        middle_a,middle_b=memory[0x7001],memory[(other+1)&65535]
        # Сравнение двух усечённых 15-битовых ключей независимым числовым выражением.
        accepted=a<10 or a*256+middle_a>=b*256+middle_b
        if a<10:
            value,flags,m1=a|1,logical_flags(a|1),14
            outcome='direct'
        elif a>b:
            value,flags,m1=a,cp_flags(a,b),15
            outcome='high_accept'
        elif a<b:
            value,flags,m1=0,0x44,16
            outcome='high_reject'
        elif middle_a<middle_b:
            value,flags,m1=0,0x44,22
            outcome='middle_reject'
        else:
            value,flags,m1=middle_a|1,logical_flags(middle_a|1),22
            outcome='middle_accept'
        initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0x7000,'IY':iy,'SP':0xBFFE,'PC':0xDAB9},None,False)
        initial[14],initial[15],initial[26],initial[27]=a,(a+b)&255,a&1,b%3
        wanted=list(initial)
        wanted[0:2]=[value,flags]
        wanted[4:6]=[b,3]
        wanted[10:12]=[other>>8,other&255]
        wanted[SP],wanted[15]=0xC000,refresh(initial[15],m1)
        simulator.registers[:]=initial
        before=list(memory)
        memory.writes=[]
        memory.recording=True
        for _ in range(24):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',iy,a,b))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (iy,a,b,middle_a,middle_b,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert (simulator.registers[1]&0x40==0)==accepted
        assert memory==before and not memory.writes
        counts[kind]+=1
        outcomes[outcome]+=1

    # Проверка каждой пары сырых старших байтов, включая оба значения игнорируемого бита 7.
    for raw_a in range(256):
        for raw_b in range(256):
            for middle_a,middle_b in ((0,255),(255,0),(127,127)):
                memory[0x7000:0x7003]=[raw_b^255,middle_a,raw_a]
                memory[0x7103:0x7106]=[raw_a^255,middle_b,raw_b]
                check(0x7100,'high_pairs')
    # Проверка всех пар средних байтов при равных старших и отсутствии прямого допуска.
    for a in range(256):
        for b in range(256):
            memory[0x7000:0x7003]=[a^255,a,10]
            memory[0x7103:0x7106]=[b^255,b,138]
            check(0x7100,'middle_pairs')
    # Проверка каждого входного IY с оборачиванием индексов по слову, память таблиц и кода не меняется.
    for iy in range(65536):
        check(iy,'all_iy')
    result=dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),outcomes=dict(outcomes),
        all_raw_high_pairs=True,all_middle_pairs=True,all_iy_words=True,
        low_byte_ignored=True,high_bit_7_ignored=True,direct_threshold=10,
        exact_registers_flags_r_and_sp=True,every_ram_byte_checked=True,no_memory_writes=True,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsComponentCompareVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()

"""Сохранение геометрии, фильтр закрытия списка и пять HALT исходных команд меню."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put


def main():
    _,_,base=make_context()
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    saves=closes=hides=0
    def fixture():
        memory=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=0x10)
        simulator=Simulator(memory);simulator.registers[:]=initial
        put(memory,0x7FFE,[255,63]);return memory,simulator,simulator.registers
    # Проверка всех физических точек окончания таблицы и байтов текущей геометрии, SavedX допускает #80.
    for length,seed in product(range(47),range(16)):
        memory,simulator,r=fixture();data=[]
        for index in range(length):
            record=[(index*71+seed*19+j*37)&255 for j in range(16)]
            if record[0]==128:record[0]=129
            data.extend(record)
        data.extend([128]+[0xCC]*15);put(memory,0xF0FD,data)
        expected=data.copy()
        for index in range(length):expected[index*16+8:index*16+12]=data[index*16:index*16+4]
        simulator.run(start=0xA7B7,stop=0x3FFF)
        assert memory[0xF0FD:0xF0FD+len(data)]==expected
        assert (r[A],r[F],r[D],r[E],r[SP])==(128,0x42,0,16,0x8000)
        assert r[8]*256+r[9]==0xF0FD+16*length
        for reg in (*range(2,4),*range(6,8),*range(10,12),*range(16,24)):assert r[reg]==initial[reg]
        saves+=1
    # Проверка каждого флагового байта и смешанных списков, удаление исполняет реальный фиксированный LDIR.
    patterns=[(flag,) for flag in range(256)]
    patterns += [tuple(((i*step+seed)&255) for i in range(n))
                 for n,step,seed in product((0,2,7,46),(1,13,71),(0,0x20,0x60,0xC0))]
    for flags in patterns:
        memory,simulator,r=fixture();pointers=[0x7000+8*i for i in range(len(flags))]
        for i,(pointer,flag) in enumerate(zip(pointers,flags)):
            put(memory,pointer,[0x21,i,0]);memory[0xF0FD+16*i+4]=flag
        raw=[b for p in pointers for b in (p&255,p>>8)]+[1,1]+[0xA5]*256
        put(memory,0xF3DE,raw);put(memory,0x9CA6,[0xDE,0xF3]);memory[0x9A82]=0x5A
        expected=[p for p,flag in zip(pointers,flags) if flag&0xC0 and flag&0x60!=0x60]
        simulator.run(start=0xA781,stop=0x3FFF)
        actual=[];pos=0xF3DE
        while memory[pos+1]!=1:
            actual.append(memory[pos]+256*memory[pos+1]);pos+=2;assert len(actual)<=len(flags)
        assert actual==expected
        assert memory[0x9A89:0x9A8B]==[0x58,0x9A]
        assert memory[0x9A82]==(0 if len(expected)!=len(flags) else 0x5A)
        assert r[SP]==0x8000 and r[8]*256+r[9]==0xF3DE+2*len(expected)
        for reg in (*range(2,4),*range(10,12),*range(16,24)):assert r[reg]==initial[reg]
        closes+=1
    # Проверка пяти исходных HALT с явным пробуждением, без подмены команды RET.
    for flags in range(256):
        memory,simulator,r=fixture();r[F]=flags;r[PC]=0xA770;wakes=0
        while r[PC]!=0x3FFF:
            if 0xA77B<=r[PC]<=0xA77F:
                assert memory[r[PC]]==0x76;r[PC]+=1;wakes+=1
            else:simulator.run()
        assert wakes==5 and memory[0x9A89:0x9A8B]==[0x58,0x9A] and memory[0x9CAA]==1
        assert (r[A],r[F],r[H],r[L],r[SP])==(1,flags,0x9A,0x58,0x8000)
        for reg in (*range(2,6),*range(8,12),*range(16,24)):assert r[reg]==initial[reg]
        hides+=1
    report=dict(passed=True,method='original_menu_commands_geometry_copy_close_filter_and_explicit_halt_wakeups',
                save_geometry_cases=saves,close_filter_cases=closes,hide_cases=hides,
                all_flag_bytes=True,actual_remove_code_executed=True,halt_wakeup_is_fixture=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MenuCommandsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

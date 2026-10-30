"""Все 768 знакомест, физический банк 3, атрибуты и настоящий финальный указатель."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckInsetFrame import bitmap_address


def main():
    source,_,base=make_context();base=[bytearray(bank) for bank in base]
    memory=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=0x10)
    simulator=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    screen=[(i*73+(i>>8)*19+17)&255 for i in range(8192)]
    background=[(i*41+(i>>5)*7+91)&255 for i in range(16384)]
    cases=copied=retained=high_owner=0
    # Проверка каждого байта цвета, всех байтов владельца и обеих форм номера индексной пары.
    for value in range(256):
        for old in (0,8,0x10,0x18):
            memory.banks=[bank.copy() for bank in base];memory.memory=[None,memory.banks[5],memory.banks[2],None]
            memory.out7ffd(old);simulator.registers[:]=initial
            trace=PortTrace(simulator);simulator.set_tracer(trace)
            memory.banks[3][:]=bytes(background)
            put(memory,0x4000,screen);put(memory,0x7FFE,[255,63])
            memory[0x6306]=old;put(memory,0x6307,[255,191]);memory[0x6548]=0xA5;memory[0x9B16]=1
            memory[0x9D48]=value
            owners=[(i*13+value)&255 for i in range(768)];owners[-1]=value&1
            indices=[(i*71+value*11)&255 for i in range(256)]
            for i in range(128):
                indices[2*i+1]=255 if (i+value)%3==0 else 0
            indices[:2]=[40,0]
            put(memory,0x8500,indices);put(memory,0x8600,owners)
            expected=screen.copy();local_copy=local_keep=0
            for cell,owner in enumerate(owners):
                # Поиск физического проверяемого байта, RLCA для владельцев выше 128 меняет чётность смещения.
                index=((owner-1)&255);index=((index<<1)|(index>>7))&255
                valid=owner!=0 and indices[(index+1)&255]!=255
                row,column=divmod(cell,32)
                if valid:
                    expected[0x1800+cell]=value;local_keep+=1
                else:
                    for line in range(8):expected[bitmap_address(row*8+line,column)-0x4000]=background[8*cell+line]
                    expected[0x1800+cell]=background[0x1800+cell];local_copy+=1
            expected=pointer_image(expected,source,255,191)
            simulator.run(start=0x9D25,stop=0x3FFF);r=simulator.registers
            assert memory[0x4000:0x6000]==expected,(value,old)
            final=(old&0xF8)|0x10;flags=(final&0xA8)|(4 if not final.bit_count()%2 else 0)
            assert (r[A],r[F],r[SP],memory[0x6306],memory.o7ffd)==(0x10,flags,0x8000,0x10,0x10)
            assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C])==(0x8900,0x5800,0xD800)
            last_attribute=value if owners[-1] else background[0x1AFF]
            assert (r[22]*256+r[23],r[20]*256+r[21],r[18],r[19])==(0x5B00,0xDB00,0x85,last_attribute)
            assert r[8:12]==initial[8:12] and memory[0x9B16]==0 and memory[0x6548]==0
            assert memory[0x8600:0x8900]==owners and memory.banks[3]==bytearray(background)
            assert trace.writes==[(0x7FFD,(old&0xF8)|0x13),(0x7FFD,final),(0x7FFD,0x10)]
            for page in (1,4,6,7):assert memory.banks[page]==base[page]
            cases+=1;copied+=local_copy;retained+=local_keep;high_owner+=sum(owner>128 for owner in owners)
    report=dict(passed=True,method='original_background_restore_768_cells_eight_banks_attributes_and_pointer',
                cases=cases,copied_cells=copied,retained_cells=retained,owner_above_128_checks=high_owner,
                color_values=256,owner_values=256,banks_modeled=8,original_pointer_code_executed=True,
                final_pointer_owner_zero_and_valid=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/RestoreBackgroundVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

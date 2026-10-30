"""Цепочка перестроения с реальными экранными банками и явно синтетическими обёртками рисования."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,PC,SP
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
    cases=refused=draw_calls=enabled_calls=moves=0
    scenarios=list(product((0,1,2,7,46),(0,1,0x40,0xE0),(0,1,255),(0,)))
    scenarios += [(7,value,0,0) for value in range(256)]
    scenarios += [(7,value,0,value) for value in (1,2,128,255)]
    for length,seed,hidden,active in scenarios:
        memory.banks=[bank.copy() for bank in base];memory.memory=[None,memory.banks[5],memory.banks[2],None]
        memory.out7ffd(0x10);simulator.registers[:]=initial;r=simulator.registers
        trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.banks[3][:]=bytes(background)
        put(memory,0x4000,screen);put(memory,0x7FFE,[255,63]);put(memory,0x6307,[255,191])
        memory[0x6306]=0x10;memory[0x6548]=0xA5;memory[0x9B16]=0x5A
        memory[0x9E78]=active;memory[0x9CAA]=hidden;memory[0x9A82]=0
        colors=[seed,(seed*13+5)&255,(seed*71+3)&255]
        for address,value in zip((0x99C2,0x99C4,0x99C6),colors):memory[address]=value
        pointers=[0x7000+8*i for i in range(length)]
        flags=[(seed+i*17)&255 for i in range(length)]
        for index,(pointer,flag) in enumerate(zip(pointers,flags)):
            # Синтетическая обёртка моделирует только LD HL,index и возврат, графики и callback в ней нет.
            put(memory,pointer,[0x21,index,0,0xAF,0xC9]);memory[0xF0FD+16*index+4]=flag
        raw=[b for pointer in pointers for b in (pointer&255,pointer>>8)]+[1,1]+[0xA5]*256
        put(memory,0xF3DE,raw);put(memory,0x9CA6,[0xDE,0xF3])
        index_tail=memory[0x8580:0x8600]
        expected_order=list(range(length))
        for position in range(max(0,length-1)):
            if flags[expected_order[position]]&0xE0==0x40:
                expected_order.insert(0,expected_order.pop(position));moves+=1
        calls=[];enabled=[];r[PC]=0x9C77
        for _ in range(300000):
            if r[PC]==0x3FFF:break
            if r[PC] in pointers:
                sp=r[SP];next_pointer=0xF3DE+2*(len(calls)+1)
                assert memory[sp:sp+4]==[0x21,0x9D,next_pointer&255,next_pointer>>8]
                index=pointers.index(r[PC]);calls.append(index)
                if memory[r[PC]]==0x21:enabled.append(index)
            simulator.run()
        else:raise AssertionError('Перестроение не завершилось')
        assert r[SP]==0x8000
        if active:
            assert not calls and not trace.writes and memory[0x4000:0x6000]==screen
            assert (r[A],memory[0x9A82],memory[0x9B16])==(active,0,0x5A)
            for reg in (*range(2,12),*range(16,24)):assert r[reg]==initial[reg]
            refused+=1
        else:
            assert calls==expected_order and enabled==([] if hidden else expected_order)
            actual=[memory[0xF3DE+2*i]+256*memory[0xF3DE+2*i+1] for i in range(length)]
            assert actual==[pointers[i] for i in expected_order]
            assert memory[0xF3DE+2*length:0xF3DE+2*length+2]==[1,1]
            assert memory[0x8500:0x8580]==[255]*128 and memory[0x8580:0x8600]==index_tail
            assert memory[0x8600:0x8900]==[0]*768 and memory[0x9A82]==1
            color=colors[0]|((colors[1]<<3)|(colors[1]>>5))&255|((colors[2]>>2)|(colors[2]<<6))&255
            assert memory[0x9D48]==color
            expected=screen.copy()
            for cell in range(768):
                row,column=divmod(cell,32)
                for line in range(8):expected[bitmap_address(row*8+line,column)-0x4000]=background[8*cell+line]
                expected[0x1800+cell]=background[0x1800+cell]
            expected=pointer_image(expected,source,255,191)
            assert memory[0x4000:0x6000]==expected
            assert list(memory.banks[7][:6912])==screen[:6912]
            assert (r[A],r[F],memory[0x6306],memory[0x9B16])==(0x10,0x0C,0x10,0)
            assert trace.writes==[(0x7FFD,p) for p in (0x17,0x18,0x1B,0x18,0x10)]
        draw_calls+=len(calls);enabled_calls+=len(enabled);cases+=1
    report=dict(passed=True,method='original_rebuild_sort_paging_and_background_with_synthetic_draw_wrappers',
                cases=cases,active_refusals=refused,draw_wrapper_calls=draw_calls,enabled_wrapper_calls=enabled_calls,
                reference_group_moves=moves,group_mask=0xE0,front_group=0x40,last_item_not_sorted=True,
                actual_begin_end_background_code_executed=True,draw_wrappers_are_synthetic=True,
                dynamic_draw_frames_verified=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/RebuildInterfaceVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

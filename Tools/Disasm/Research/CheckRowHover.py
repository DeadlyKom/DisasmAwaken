"""Настоящие обработчики наведения, XOR-ядро, указатель и управляемое изменение PointerY между проверками."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckRowHighlight import make_context,band_parameters,rotate3
from CheckSelectionBand import xor_band


def main():
    station,_,base=make_context()
    initial=get_registers({'SP':0x7FFE,'HL':0x7583,'DE':0x4003,'BC':0x36C9,
                           'IX':0xF37D,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=changed=unchanged=late_failed=late_changed=0
    screen=[(i*73+(i>>8)*19+17)&255 for i in range(8192)]

    def execute(start,x,y,width,height,offset,pointer_y,previous,last,active,late=None,seed=True):
        nonlocal cases,changed,unchanged,late_failed,late_changed
        memory=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=0x10)
        simulator=Simulator(memory);trace=PortTrace(simulator);simulator.set_tracer(trace)
        put(memory,0xF37D,[x&255,y,width,height,0x26])
        put(memory,0x9CA6,[0,0xE0]);put(memory,0xE000,[0,0x70,0x83,0x75,1,1] if last else [0x83,0x75,0,0x70,1,1])
        # Создание допустимого владельца Item40 для видимых ячеек, Flags #26 запрещает обе краевые формы.
        put(memory,0x8500,[40,0]);put(memory,0x8600,[0]*768)
        for cell_y in range(max(0,y),min(24,y+height)):
            for cell_x in range(max(0,x),min(32,x+width)):
                memory[0x8600+32*cell_y+cell_x]=1
        pointer_x=8*max(x,0)+2
        memory[0x6306]=0x10;put(memory,0x6307,[pointer_x,pointer_y]);memory[0x6548]=0xA5
        memory[0x757A]=previous
        scene=screen.copy()
        def invert(target,row):
            params=band_parameters(x&255,y,width,offset,row)
            if params is not None:xor_band(target,*params)
        if seed and previous!=255:invert(scene,previous)
        put(memory,0x4000,scene)
        def run(entry,prev,inject=False):
            put(memory,0x7FFE,[255,63]);simulator.registers[:]=initial;r=simulator.registers
            r[A],r[D],r[E]=prev,(8 if start==0xA311 else 64),offset
            if inject:
                simulator.run(start=entry,stop=0xA337 if start==0xA311 else 0xA364)
                assert r[PC] in (0xA337,0xA364)
                memory[0x6308]=late
                simulator.run(stop=0x3FFF)
            else:simulator.run(start=entry,stop=0x3FFF)
            assert r[SP]==0x8000
            return r
        if active:run(0x6413,previous)
        initial_image=pointer_image(scene,station,pointer_x,pointer_y) if active else scene.copy()
        assert memory[0x4000:0x6000]==initial_image
        memory[0x9B16]=0x5A;trace.writes.clear()
        base_y=(8*y+offset)&255
        extent=min((rotate3(height)-offset-5)&0xF8,64) if start==0xA311 else 64
        first_hit=pointer_y>=base_y and pointer_y-base_y<extent
        first_row=(pointer_y-base_y)//8 if first_hit else None
        update=last and first_hit and previous!=first_row
        r=run(start,previous,update and late is not None)
        expected=scene.copy()
        if update:
            if previous!=255:invert(expected,previous)
            final_y=pointer_y if late is None else late
            second_hit=final_y>=base_y and final_y-base_y<extent
            result=(final_y-base_y)//8 if second_hit else extent
            if second_hit:invert(expected,result)
            expected=pointer_image(expected,station,pointer_x,final_y)
            assert (r[A],r[F],memory[0x9B16],memory[0x6548])==(result,0,0,0)
            if start==0x7573:assert memory[0x757A]==result
            if late is not None:
                late_failed+=not second_hit;late_changed+=second_hit and result!=first_row
            changed+=1
        else:
            expected=initial_image
            assert r[F]&0x40 and memory[0x9B16]==0x5A and not trace.writes
            if not last or not first_hit:assert r[A]==0
            else:assert r[A]==previous
            assert memory[0x757A]==previous
            unchanged+=1
        assert memory[0x4000:0x6000]==expected,(start,x,y,width,height,pointer_y,previous,last,active,late)
        assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
        for page in (3,4,6,7):assert memory.banks[page]==base[page]
        cases+=1
        return memory,simulator,run,invert

    # Проверка обоих общих входов и меню с настоящими кодом указателя, таблицей владельцев и списком рисования.
    for start,(x,y,width,height),pointer_y,previous,last,active in product(
            (0xA311,0xA341,0x7573),((0,0,9,9),(-3,1,9,9),(28,15,9,9),(31,22,2,2)),
            (0,3,11,59,123,179,191),(255,0,1,7,64),(False,True),(False,True)):
        execute(start,x,y,width,height,3,pointer_y,previous,last,active)
    # Изменение входной памяти между двумя проверками, это управляемая инъекция, а не исполнение IRQ.
    for start,previous,active,late in product((0xA311,0xA341,0x7573),(255,0,7,64),(False,True),(3,19,191)):
        execute(start,0,0,9,9,3,11,previous,True,active,late)
    # Проверка следующего реального вызова меню после сохранения высоты 64 вместо номера строки.
    for active in (False,True):
        memory,simulator,run,invert=execute(0x7573,0,0,9,9,3,11,255,True,active,191)
        assert memory[0x757A]==64
        memory[0x6308]=3
        r=run(0x7573,64)
        expected=screen.copy();invert(expected,64);invert(expected,0)
        assert memory[0x4000:0x6000]==pointer_image(expected,station,2,3)
        assert (r[A],r[F],memory[0x757A])==(0,0,0)
        assert expected!=screen
        cases+=1;changed+=1
    report=dict(passed=True,method='original_hover_cursor_and_banked_xor_with_explicit_late_pointer_mutation',
                cases=cases,changed=changed,unchanged=unchanged,late_hit_failures=late_failed,
                late_different_rows=late_changed,pointer_owner_fixture=40,banks_modeled=8,
                cached_height_then_residual_band_cases=2,
                original_pointer_code_executed=True,irq_executed=False,hardware_race_timing_verified=False,
                native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/RowHoverVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

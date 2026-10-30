"""Развилка действия меню, явный договор RepaintAndFlag и исходное удаление элементов."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put


def main():
    _,_,base=make_context()
    initial=get_registers({'SP':0x7FFE,'HL':0x7583,'DE':40,'BC':0x36C9,
                           'IX':0xF37D,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    targets=(0xA770,0xA781,0xA7B7,0xA7E0,0xA7E3,0xA7E9,0xA7EF,0xCBA9)
    cases=dispatched=empty=early=row_checks=0
    rows={}
    def fixture():
        memory=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=0x10)
        simulator=Simulator(memory);simulator.registers[:]=initial;r=simulator.registers
        put(memory,0x7FFE,[255,63]);put(memory,0x9CA6,[0,0xE0])
        put(memory,0x7000,[0x21,40,0]);put(memory,0xE000,[0,0x70,1,1]+[0xA5]*256)
        memory[0x9A82]=0x5A;return memory,simulator,r
    inputs=list(product(range(256),(0,1),(0,7,64,255)))
    inputs+=list(product((0,1,2,0x80,255),(0,1),range(256)))
    for selector,carry,previous in inputs:
        memory,simulator,r=fixture();memory[0x757A]=previous;memory[0x6308]=11;memory[0xAEC7]=3
        r[PC]=0x753C;visited_repaint=0
        for _ in range(2000):
            if r[PC]==0x3FFF or r[PC] in targets:break
            if r[PC]==0xCBEB:
                # Подмена только договора перерисовки, байты исходной развилки и удаления не меняются.
                r[A],r[F]=selector,carry
                sp=r[SP];r[PC]=memory[sp]+256*memory[sp+1];r[SP]+=2;visited_repaint+=1
            else:simulator.run()
        else:raise AssertionError('Развилка меню не завершилась')
        assert visited_repaint==1
        if carry:
            assert r[PC]==0x3FFF and memory[0xE000:0xE004]==[0,0x70,1,1]
            assert (r[A],r[F])==(selector,carry);early+=1
        elif selector==1:
            assert memory[0xE000:0xE002]==[1,1] and memory[0x9A82]==0
            if previous==255:
                assert r[PC]==0x3FFF and r[A]==0 and r[F]&0x40;empty+=1
            else:
                expected=targets[previous] if previous<7 else 0xCBA9
                assert r[PC]==expected
                if previous>=7:assert r[H]*256+r[L]==0x7492
                rows[str(previous)]=f'{expected:04X}';dispatched+=1
        else:
            assert r[PC]==0x3FFF and memory[0xE000:0xE004]==[0,0x70,1,1]
            assert not r[F]&0x40
        assert r[SP]==(0x8000 if r[PC]==0x3FFF else 0x7FFE)
        cases+=1
    # Проверка всех пар пиксельных Y, сравниваются лишь целые номера восьмипиксельных строк.
    for pointer_y,top in product(range(256),repeat=2):
        memory,simulator,r=fixture();memory[0x6308]=pointer_y;memory[0xAEC7]=top
        simulator.run(start=0xC85E,stop=0x3FFF)
        match=pointer_y//8==top//8
        assert memory[0xE000:0xE004]==([1,1,0xA5,0xA5] if match else [0,0x70,1,1])
        assert r[SP]==0x8000 and r[D]*256+r[E]==40 and r[H]*256+r[L]==0x7583
        assert r[3]==pointer_y//8 and bool(r[F]&0x40)==match
        row_checks+=1
    report=dict(passed=True,method='original_menu_dispatch_with_explicit_repaint_contract_and_real_remove_code',
                dispatch_cases=cases,command_transfers=dispatched,empty_selection_returns=empty,
                repaint_carry_returns=early,row_comparison_cases=row_checks,
                selected_targets=rows,repaint_is_explicit_stub=True,command_bodies_executed=False,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MenuDispatchVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='selected_targets'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

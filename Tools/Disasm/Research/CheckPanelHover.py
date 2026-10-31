"""Семь физических обёрток наведения, полный bitmap полосы и настоящего указателя."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,PC,SP
from CheckRowHighlight import make_context,band_parameters,rotate3
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckSelectionBand import xor_band
from PanelHoverFacts import PANELS


def main():
    station,_,banks=make_context();initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0xF37D,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    baseline=[(i*73+(i>>8)*19+17)&255 for i in range(8192)];cases=changed=unchanged=0;counts={}
    for address,name,index,draw,area,row_name,operand,pixel,_ in PANELS:
        counts[name]=0;x,y,width,height=6,2,11,9;offset=area&255
        extent=area>>8 if pixel else min((rotate3(height)-offset-5)&0xF8,((area>>8)*8)&255)
        for last in (False,True):
            for previous in (255,0,64):
                for py in range(192):
                    page=0x10 if py&1 else 0x18;m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
                    put(m,0xF37D,[x,y,width,height,0x26]);put(m,0x9CA6,[0,0xE0]);entries=[0x5F00,draw] if last else [draw,0x5F00]
                    put(m,0xE000,b''.join(p.to_bytes(2,'little') for p in entries)+bytes([1,1]));put(m,0x8500,[40,0]);put(m,0x8600,bytes(768))
                    # Владелец указателя нулевой, корректность ненулевого владельца проверяется отдельной моделью указателя.
                    put(m,0x6307,[50,py]);m[0x6306]=page;m[0x6548]=0xA5;m[0x9B16]=0x5A;m[operand]=previous
                    scene=baseline.copy()
                    def invert(image,row):
                        params=band_parameters(x,y,width,offset,row)
                        if params is not None:xor_band(image,*params)
                    if previous!=255:invert(scene,previous)
                    expected=scene.copy();base_y=y*8+offset;hit=base_y<=py<base_y+extent;row=(py-base_y)//8 if hit else None;update=last and hit and row!=previous
                    if update:
                        if previous!=255:invert(expected,previous)
                        invert(expected,row);expected=pointer_image(expected,station,50,py)
                    put(m,0x4000,scene);put(m,0x7FFE,[255,63]);s.registers[:]=initial;r=s.registers;r[PC]=address
                    for _ in range(30000):
                        if r[PC]==0x3FFF:break
                        s.run()
                    else:raise AssertionError(('instruction_limit',name,last,previous,py,hex(r[PC])))
                    assert m[0x4000:0x6000]==expected,(name,last,previous,py,'bitmap')
                    assert m[operand]==(row if update else previous),(name,last,previous,py,'row')
                    assert bool(r[F]&0x40)==(not update) and r[SP]==0x8000
                    assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and m[0x6306]==page and m.o7ffd==page
                    if update:assert (r[A],r[F])==(row,0)
                    else:assert not trace.writes and m[0x9B16]==0x5A
                    cases+=1;changed+=update;unchanged+=not update;counts[name]+=1
    report=dict(passed=True,cases=cases,changed_cases=changed,unchanged_cases=unchanged,per_wrapper=counts,
                every_pointer_y_0_191=True,previous_rows=[255,0,64],last_draw_handler_gate=True,
                bitmap_and_attributes_compared=True,real_pointer_and_banked_xor=True,
                late_pointer_change_not_injected_here=True,late_change_core_report='RowHoverVerification.json',
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/PanelHoverVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

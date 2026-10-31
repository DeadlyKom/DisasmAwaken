"""Исходный общий выход прокрутки с сохранённой парой координат на стеке."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,SP,D,E
from CheckRowHighlight import make_context
from CheckScreenUpdate import put,PortTrace,pointer_image


def main():
    station,_,banks=make_context();initial=get_registers({'SP':0x7FFC,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    baseline=[(i*73+(i>>8)*19+17)&255 for i in range(8192)];cases=0
    for page in (0x10,0x18):
        for x in (0,7,248,255):
            for y in range(192):
                m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);s.set_tracer(PortTrace(s))
                put(m,0x4000,baseline);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));m[0x6306]=page
                put(m,0x6307,[10,20]);m[0x6548]=1;m[0x9B16]=1;put(m,0x7FFC,[x,y,255,63]);s.registers[:]=initial
                s.run(start=0xA1CD,stop=0x3FFF);r=s.registers
                assert m[0x6307:0x6309]==[x,y] and m[0x9B16]==0 and m[0x6548]==0
                assert m[0x4000:0x6000]==pointer_image(baseline,station,x,y)
                assert (r[D],r[E])==(y,x) and r[A:F+1]==initial[A:F+1] and r[2:4]==initial[2:4] and r[6:12]==initial[6:12] and r[18:24]==initial[18:24]
                assert r[SP]==0x8000 and m[0x6306]==page and m.o7ffd==page;cases+=1
    report=dict(passed=True,cases=cases,all_pointer_y_0_191=True,pointer_x=[0,7,248,255],saved_xy_popped_before_return=True,
                bitmap_and_attributes_compared=True,real_resume_pointer=True,owner_zero_fixture=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ScrollPointerExitVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

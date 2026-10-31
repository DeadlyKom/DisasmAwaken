"""Действие просмотра, снятие bit7, оба шага координаты и отключение периодического callback."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,D,E,PC,SP
from Analyze import payload
from CheckRowHighlight import make_context
from CheckScreenUpdate import put,PortTrace
from CheckWorldSignature import logical_flags


def main():
 _,_,banks=make_context();raw=payload(6);banks[4][:len(raw)]=list(raw);initial=get_registers({'SP':0x7FFE,'HL':0x6877,'DE':26,'BC':0x36C9,'AF':0x5A5D,'IX':0xF29D,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=closed=increment=decrement=accepted=0
 # Проверка всех селекторов, двух строк и граничных координат с реальными дочерними процедурами.
 for selector in range(256):
  for same_row in (False,True):
   for third in (0,511,512,543,4095,4096,65535):
    page=0x18 if selector&1 else 0x10;m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[A]=selector;r[PC]=0x683A
    put(m,0x6878,[26,0]);put(m,0x5F00,[0x21,63,0,0xC9]);put(m,0x9CA6,[0,0xB4]);put(m,0xB400,[0,0x5F,0x77,0x68,1,1]+[0]*128);put(m,0xF29D,[0,0,24,12,6,5]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x6307,[50,3 if same_row else 80]);m[0xAEC7]=3;m[0xAECB]=0;m[0xAEBB]=3;m[0x6306]=page;m[0x9E78]=0;m[0xCA20]=6;m[0x9A82]=0xA7;m[0x6548]=1;m[0x9B16]=0;put(m,0x9A90,[0x58,0x9A]);put(m,0x9A8D,[255,255]);put(m,0x9A89,[0xEA,0x68]);m.banks[4][0xDC4:0xDC6]=list(third.to_bytes(2,'little'));put(m,0x7FFE,[255,63])
    s.run(start=0x683A,stop=0x3FFF);effective=selector&127;close=same_row and effective!=1
    if close:
     assert m[0xB400:0xB404]==[0,0x5F,1,1] and m[0x9A89:0x9A8B]==[0x58,0x9A] and r[H]*256+r[L]==0x9A58 and trace.writes==[];expected=third;closed+=1
    else:
     delta=-32 if effective==1 else 32;total=(third+delta)&65535;expected=total if 512<=total<4096 else third;final=(page&0xF8)|0x10
     assert r[H]*256+r[L]==total and r[D]*256+r[E]==third and (r[A],r[F])==(final,logical_flags(final))
     assert trace.writes==[(0x7FFD,(page&0xF8)|0x14),(0x7FFD,final)] and m[0x9A89:0x9A8B]==[0xEA,0x68];increment+=delta>0;decrement+=delta<0;accepted+=512<=total<4096
    assert int.from_bytes(m.banks[4][0xDC4:0xDC6],'little')==expected and r[SP]==0x8000 and r[8:12]==initial[8:12]
    cases+=1
 report=dict(passed=True,cases=cases,all_selector_bytes=True,bit7_removed_by_real_repaint_entry=True,close_cases=closed,increment_cases=increment,decrement_cases=decrement,accepted_coordinate_cases=accepted,real_list_close_banking_and_adjust=True,wrapped_sum_and_range_checked=True,native_execution=False,irq_executed=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewActionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Развилки действия описания с реальным списком и подсчётом, выход к договору прокрутки."""
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
from CheckTextPagination import reference
from CheckPreviewDescriptions import selected


def main():
 _,_,banks=make_context();raw=payload(6);banks[4][:len(raw)]=list(raw);initial=get_registers({'SP':0x7FFE,'HL':0x6945,'DE':27,'BC':0x36C9,'AF':0x5A5D,'IX':0xF2AD,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=early=single=closed=scroll=0
 # Проверка всех селекторов и обеих строк при настоящих списке, закрытии и счётчике D3D.
 for selector in range(256):
  for same_row in (False,True):
   m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[A]=selector;r[PC]=0x6916
   put(m,0x6946,[27,0]);put(m,0x5F00,[0x21,63,0,0xC9]);put(m,0x9CA6,[0,0xB4]);put(m,0xB400,[0,0x5F,0x45,0x69,1,1]+[0]*128);put(m,0xF2AD,[0,0,24,12,6,5]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x6307,[50,3 if same_row else 80]);m[0xAEC7]=3;m[0xAECB]=0;m[0xAEBB]=3;m[0x6306]=0x10
   m[0x9E78]=0;m[0xCA20]=6;m[0x9A82]=0xA7;m[0x6548]=1;m[0x9B16]=0;put(m,0x9A90,[0x58,0x9A]);put(m,0x9A8D,[255,255]);put(m,0x6933,[5,0xA5]);put(m,0x692B,[0x7E,0x5A]);put(m,0xA235,[0x91,0x82]);put(m,0xA265,[0x73,0x64]);m[0x6906]=0;m[0xAEAB]=80;m[0xAEB3]=168;m.banks[4][0x2146]=0;m.banks[4][0x2148]=0;put(m,0x7FFE,[255,63])
   snapshot=bytearray(m[0:65536]);snapshot[0xC000:]=bytes(m.banks[4]);start=selected(snapshot,0,0);oracle=reference(0xA82D,list(snapshot[start:]),list(snapshot[0x8900:0x8A00]),0x3600,168,80,0,origin=(3,3));count=oracle[6]*256+oracle[7]
   for _ in range(150000):
    if r[PC] in (0xA1D6,0x3FFF):break
    s.run()
   else:raise AssertionError(('instruction_limit',selector,same_row,hex(r[PC])))
   if selector&128:
    assert r[PC]==0x3FFF and (r[A],r[F])==(selector,(selector&0xA8)|1) and m[0x9A82]==0xA7;early+=1
   elif selector==1:
    assert r[PC]==0x3FFF and r[A]==0 and r[F]==0x42;single+=1
   elif same_row:
    assert r[PC]==0x3FFF and m[0xB400:0xB404]==[0,0x5F,1,1] and m[0x9A82]==0 and r[D]*256+r[E]==27;closed+=1
   else:
    assert r[PC]==0xA1D6 and (r[A],r[H]*256+r[L],r[SP])==(8,0xA505,0x7FFC)
    assert m[0x692B:0x692D]==list(count.to_bytes(2,'little')) and m[0xA235:0xA237]==list(count.to_bytes(2,'little')) and m[0xA265:0xA267]==[0x52,0x69]
    assert trace.writes==[(0x7FFD,0x14),(0x7FFD,0x10)];scroll+=1
   assert m[0x6933:0x6935]==[5,0xA5]
   if r[PC]==0x3FFF:assert r[SP]==0x8000 and m[0x692B:0x692D]==[0x7E,0x5A] and m[0xA235:0xA237]==[0x91,0x82] and m[0xA265:0xA267]==[0x73,0x64]
   cases+=1
 report=dict(passed=True,dispatch_cases=cases,all_selector_bytes=True,early_bit7_cases=early,selector_one_returns=single,row_close_cases=closed,scroll_dispatch_cases=scroll,real_repaint_list_close_and_d3d_count=True,scroll_stopped_at_entry=True,child_scroll_report='ScrollWindowVerification.json',count_independently_calculated=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/DescriptionActionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

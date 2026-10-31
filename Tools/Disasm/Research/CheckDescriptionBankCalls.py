"""Станционные обёртки D3D с реальными OUT и независимой пагинацией описаний."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from Analyze import payload
from CheckRowHighlight import make_context
from CheckScreenUpdate import put,PortTrace
from CheckTextPagination import reference
from CheckPreviewDescriptions import selected,paint_positions
from CheckWorldSignature import logical_flags


def main():
 _,_,banks=make_context();raw=payload(6);banks[4][:len(raw)]=list(raw);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);counts=prints=glyphs=0
 for entry in (0x6952,0x6963):
  for selector in (0,1,255):
   for index in range(4 if selector==1 else 7):
    for page in (0x10,0x18):
     for width,height in ((96,13),(168,80),(224,160)):
      for scroll in ((0,1,255,0xA501) if entry==0x6952 else (0,)):
       m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[H]=scroll>>8;r[L]=scroll&255;m[0x6306]=page;m[0x6906]=selector;put(m,0x692B,[0x7E,0x5A]);put(m,0x7FFE,[255,63]);m.banks[4][0x2146]=(index-3)&255;m.banks[4][0x2148]=3;m[0xAEAB]=height;m[0xAEB3]=width;m[0xAEBB]=5;m[0xAEBF]=0;m[0xAEC7]=3;m[0xAECB]=0;m[0xBD26]=0
       snapshot=bytearray(m[0:65536]);snapshot[0xC000:]=bytes(m.banks[4]);text=selected(snapshot,selector,index);positions=[];counting=entry==0x6963
       oracle=reference(0xA82D if counting else 0xA843,list(snapshot[text:]),list(snapshot[0x8900:0x8A00]),0x3600|((index-3)&255) if counting else 0x0800,width,height,0 if counting else scroll&255,initial_d=scroll>>8,positions=positions,origin=(5,3));offset,cx,cy,_,_,bc,d,e,_=oracle;screen,painted=paint_positions(snapshot,positions,width,height,(5,3));glyphs+=painted
       s.run(start=entry,stop=0x3FFF);final=(page&0xF8)|0x10
       assert (r[H]*256+r[L],r[D],r[E],r[2]*256+r[3],r[A],r[F],m[0x6320],m[0x6321],r[SP])==(text+offset,d,e,bc,final,logical_flags(final),cx,cy,0x8000)
       assert bytes(m[0x4000:0x5B00])==screen and bytes(m.banks[4])==snapshot[0xC000:] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
       assert bytes(m[0x692B:0x692D])==((d*256+e).to_bytes(2,'little') if counting else bytes([0x7E,0x5A]))
       assert trace.writes==[(0x7FFD,(page&0xF8)|0x14),(0x7FFD,final)] and m.o7ffd==final and m[0x6306]==final
       counts+=counting;prints+=not counting
 report=dict(passed=True,count_cases=counts,print_cases=prints,independent_glyphs=glyphs,real_banking_and_d3d_callees=True,wrapped_index_sum=True,row_count_operand_written_only_by_counter=True,final_af_is_page_selection=True,full_bitmap_attributes_and_d3d_bank_compared=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/DescriptionBankCallsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

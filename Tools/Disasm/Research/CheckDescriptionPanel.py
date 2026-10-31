"""Панель описания, прямой и последовательный условный вход, реальные рамка и банковый текст."""
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
from CheckPreviewDescriptions import selected,paint_positions
from CheckWorldSignature import logical_flags


def main():
 _,_,banks=make_context();raw=payload(6);banks[4][:len(raw)]=list(raw);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=direct=listed=glyphs=0
 for selector in (0,1,255):
  for index in range(4 if selector==1 else 7):
   for page in (0x10,0x18):
    for x,y,w,h in ((1,2,24,12),(2,1,16,5)):
     for flags in (0,1):
      for scroll in (0,1,0x100,0xA5FF):
       m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[PC]=0x693E if scroll&1 else 0x6945;m[0x6306]=page;put(m,0x7FFE,[255,63]);put(m,0x6946,[27,0]);record=0xF0FD+16*27;put(m,record,[x,y,w,h,flags,m[record+5]]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x6933,scroll.to_bytes(2,'little'));m[0x6906]=selector;put(m,0x9CA6,[0,0xB4]);put(m,0xB400,[0x45,0x69,1,1]);m.banks[4][0x2146]=(index-3)&255;m.banks[4][0x2148]=3
       expected=None;caption_alt=None;wakes=0
       for _ in range(240000):
        pc=r[PC]
        if pc==0x3FFF:break
        if pc==0x694B:
         caption_alt=list(r[16:18]);snapshot=bytearray(m[0:65536]);snapshot[0xC000:]=bytes(m.banks[4]);start=selected(snapshot,selector,index);width,height=snapshot[0xAEB3],snapshot[0xAEAB];origin=(snapshot[0xAEBB]+256*snapshot[0xAEBF],snapshot[0xAEC7]+256*snapshot[0xAECB]);positions=[]
         oracle=reference(0xA843,list(snapshot[start:]),list(snapshot[0x8900:0x8A00]),0x0800,width,height,scroll&255,initial_d=scroll>>8,positions=positions,origin=origin);offset,cx,cy,_,_,bc,d,e,_=oracle;screen,painted=paint_positions(snapshot,positions,width,height,origin);glyphs+=painted;expected=(start+offset,d,e,bc,cx,cy,screen,bytes(m.banks[4]))
        if pc==0xC089 and m.o7ffd&7==0:assert m[pc]==0x76;r[PC]+=1;wakes+=1
        else:s.run()
       else:raise AssertionError(('instruction_limit',selector,index,page,scroll,hex(r[PC])))
       assert expected is not None;hl,d,e,bc,cx,cy,screen,bank=expected;final=(page&0xF8)|0x10
       assert (r[H]*256+r[L],r[D],r[E],r[2]*256+r[3],r[A],r[F],m[0x6320],m[0x6321])==(hl,d,e,bc,final,logical_flags(final),cx,cy)
       assert bytes(m[0x4000:0x5B00])==screen and bytes(m.banks[4])==bank and r[16:18]==caption_alt and r[18:24]==initial[18:24] and r[8:12]==initial[8:12] and r[SP]==0x8000 and wakes==1
       assert trace.writes==[(0x7FFD,(page&0xF8)|0x14),(0x7FFD,final)] and m.o7ffd==final and m[0x6306]==final;cases+=1;listed+=bool(scroll&1);direct+=not bool(scroll&1)
 # Точный отсутствие-поиска путь условного входа, список содержит другой обработчик со старшим байтом меньше 69.
 for flags in range(256):
  m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);put(m,0x9CA6,[0,0xB4]);put(m,0xB400,[0,0x5F,1,1]);put(m,0x7FFE,[255,63]);before=bytes(m[0x4000:0x5B00]);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[F]=flags;s.run(start=0x693E,stop=0x3FFF)
  assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E],r[SP])==(1,1,0x1357,0x6945,0x8000) and bytes(m[0x4000:0x5B00])==before and r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
 # Отключённый рисователь и два пустых входа события не меняют память и регистры.
 for entry in (0x6945,0x6913,0x693D):
  for flags in range(256):
   m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10)
   if entry==0x6945:m[entry]=0xC9
   put(m,0x7FFE,[255,63]);before=[bytes(b) for b in m.banks];s=Simulator(m);s.registers[:]=initial;r=s.registers;r[F]=flags;s.run(start=entry,stop=0x3FFF)
   assert [bytes(b) for b in m.banks]==before and r[A]==initial[A] and r[F]==flags and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
 report=dict(passed=True,cases=cases,direct_cases=direct,listed_fallthrough_cases=listed,independent_glyphs=glyphs,unlisted_cases=256,disabled_entry_cases=256,empty_event_entry_cases=512,real_caption_and_description_callees=True,caption_uses_separate_proved_contract=True,description_bitmap_and_attributes_independently_compared=True,banking_and_registers_checked=True,explicit_halt_wakeups=cases,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/DescriptionPanelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

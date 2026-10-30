"""Выбор ближайшей точки с реальными перерисовками карты и двух соседних панелей."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckMapSectorTables import reference as sector_reference
from CheckVisibleMapPoints import reference as visible_reference
from CheckMapDistanceMinimum import distance

WINDOW=(0xAEBB,0xAEC7,0xAEBF,0xAECB,0xAEB3,0xAEAB,0xBD26,0x6320,0x6321)


def main():
 station,map_source,banks=make_context();initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=wakeups=root_cases=0;chosen_counts=set()
 for ox,oy in ((0,0),(0x0100,0),(0x0300,0),(0x12FC,0x34FC),(0x4B00,0x3800)):
  tables=bytearray(1024)
  for base,hx,hy in ((0,ox>>8,oy>>8),(256,((ox>>8)+1)&255,oy>>8),(512,ox>>8,((oy>>8)+1)&255),(768,((ox>>8)+1)&255,((oy>>8)+1)&255)):tables[base:base+256]=sector_reference(hx,hy)[0]
  output,_,_,_=visible_reference(tables,ox&255,oy&255,80,72,bytes([0xA7])*512)
  assert output[257]!=0
  for pointer in ((16,24),(48,50),(95,95),(0,0)):
   for with_info in (False,True):
    for with_variants in (False,True):
     m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);m[0x6306]=0x10;s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
     put(m,0x6DA9,[11,0]);put(m,0xF1AD,[1,1,12,12,0,0]);put(m,0x7690,[19,0]);put(m,0xF0FD+19*16,[16,0,16,24,0,13]);put(m,0x788D,[20,0]);put(m,0xF0FD+20*16,[21,15,9,9,0,14])
     put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x6307,pointer);put(m,0x7FFE,[255,63]);s.registers[:]=initial;r=s.registers;r[B],r[C],r[D],r[E]=1,1,12,12;s.run(start=0xC233,stop=0x3FFF)
     # Подготовка уже согласованных экранных таблиц и отсечения, исходные запросы этих таблиц равны нулю.
     m.out7ffd(0x11);m[0x6306]=0x11;put(m,0x7FFE,[255,63]);s.registers[:]=initial;r[D],r[E]=8,8;s.run(start=0xC49B,stop=0x3FFF)
     put(m,0x7FFE,[255,63]);s.registers[:]=initial;r[H],r[L]=71,79;r[D]=r[E]=0;s.run(start=0xD0C3,stop=0x3FFF);m.out7ffd(0x10);m[0x6306]=0x10
     put(m,0x6300,[ox&255,oy&255,ox>>8,oy>>8,80,72]);m.banks[1][0x3200:0x3600]=list(tables);m[0x6D75]=m[0x6D7B]=m[0x6D90]=0
     put(m,0x983F,bytes([0xF0])*4+bytes([0]));old=bytes([0xF0])*4+bytes([0]);put(m,0x9844,old);put(m,0x988E,[0,0]);m[0x990A]=0x80;m[0x993D]=0xFF;m[0x99A3]=0x80;put(m,0x6309,[0x3D,0x99])
     put(m,0x9A8D,[255,255]);put(m,0x9A90,[0x58,0x9A]);m[0x6548]=1;m[0x9B16]=0;m[0x99B4]=1
     entries=[0x6DA8]+([0x768F] if with_info else [])+([0x788C] if with_variants else []);put(m,0x9CA6,[0,0xB4]);put(m,0xB400,b''.join(a.to_bytes(2,'little') for a in entries)+bytes([1,1])+bytes(130));put(m,0x4000,bytes([0x96])*6912)
     # Независимый выбор ближайшей записи с сохранением первого кандидата при равных квадратах расстояний.
     px,py=pointer;outside=px<16 or py<24 or px-16>79 or py-24>71;choice=None;minimum=65535
     if not outside:
      for i in range(0,256,2):
       if output[257+i]==0:break
       q,_,_=distance((output[i]-(px-16))&255,(output[i+1]-(py-24))&255)
       if q<minimum:minimum=q;choice=i
      link=output[256+choice]+256*output[257+choice];page=link>>8;at=link-0xF200
      first=((((oy>>8)+int(page not in (0xF2,0xF3)))&255)<<8)|(((ox>>8)+int(page not in (0xF2,0xF4)))&255)
      second=tables[at]+256*tables[(at&0x300)|((at+1)&255)];expected=first.to_bytes(2,'little')+second.to_bytes(2,'little')+bytes([0]);chosen_counts.add(max(((first>>8)^(first&255)^(second>>8)^(second&255))&7,1)-1)
     else:expected=old
     put(m,0x7FFE,[255,63]);s.registers[:]=initial;r=s.registers;root=ox in (0x0100,0x0300);r[PC]=0x6C0D if root else 0x6D0D
     if root:r[A]=1;r[H],r[L]=0x6D,0xA8;r[D],r[E]=0,11;m[0xCA20]=6;m[0x9E78]=0;root_cases+=1
     trace.writes.clear();wakes=0;saved=None;selected=False;restored=False
     for step in range(800000):
      pc=r[PC]
      if pc==0x3FFF:break
      if pc==0x6D21:
       assert bytes(m[0x9844:0x9849])==expected;selected=True
       if choice is not None:assert m.banks[1][0x3E8:0x3EA]==list((0xF600+choice).to_bytes(2,'little'))
      if pc==0x6D2C:saved=bytes(m[a] for a in WINDOW)
      if pc==0x6D35:assert bytes(m[a] for a in WINDOW)==saved;restored=True
      halt=(pc in (0xC4E5,0xC14B) and m.o7ffd&7==1) or (pc==0xC089 and m.o7ffd&7==0)
      if halt:assert m[pc]==0x76;r[PC]+=1;wakes+=1
      else:s.run()
     else:raise AssertionError(('instruction_limit',ox,oy,pointer,with_info,with_variants,hex(r[PC])))
     assert selected and restored and bytes(m[0x9844:0x9849])==expected and r[SP]==0x8000 and r[10:12]==initial[10:12] and m[0x6306]==m.o7ffd==0x10 and m[0x6D75]==m[0x6D90]==0
     if with_variants:
      tail=0xB400+2*(len(entries)-1);assert m[tail]+256*m[tail+1]==0x788C
     ports=[v for port,v in trace.writes if port==0x7FFD]
     if not root:assert ports[:4]==[0x11,0x10,0x17,0x18]
     assert ports[-1]==0x10
     cases+=1;wakeups+=wakes
 report=dict(passed=True,cases=cases,root_dispatch_selection_cases=root_cases,selected_counts=sorted(chosen_counts),information_panel_presence=[False,True],variant_panel_presence=[False,True],outside_pointer_preserves_selection=True,text_window_restored_after_information_panel=True,variant_panel_may_replace_final_text_window=True,method='original_selection_scene_and_optional_panels_with_independent_nearest_point_key_and_call_state_checks',whole_bitmap_independent_oracle=False,calls_stubbed=False,explicit_halt_wakeups=wakeups,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapSelectionPanelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

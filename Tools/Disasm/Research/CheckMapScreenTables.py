"""Четыре исходные страницы адресов строк, горизонтальных байтов и одноразрядных масок карты."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context


def reference(memory,x,y):
 px,py=(x+8)&255,(y+16)&255;high=memory[0x8200+py];low=memory[0x8300+py]|memory[0x8400+px]
 column=low&31;low&=224;rows_high=[];rows_low=[]
 for _ in range(256):
  rows_high.append(high);rows_low.append(low);high=(high+1)&255
  if high&7==0:
   total=low+32;low=total&255
   if total<256:high=(high-8)&255
 return bytes(rows_high+rows_low+[(column+i//8)&255 for i in range(256)]+[128>>(i&7) for i in range(256)]),high*256+low,column


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 coords=sorted({(x,y) for x in range(256) for y in (0,1,7,175,191,240,255)}|{(x,y) for y in range(256) for x in (0,1,7,247,248,255)})
 cases=0
 # Проверка таблиц и их граничных байтов для всех входных координат по каждой оси.
 for x,y in coords:
  expected,de,column=reference(memory,x,y);sim.registers[:]=initial;r=sim.registers;r[D],r[E]=y,x
  memory[0xEDFF:0xF201]=bytes([0xA7])*1026;memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=0xC49B,stop=0x3FFF)
  assert bytes(memory[0xEE00:0xF200])==expected and memory[0xEDFF]==memory[0xF200]==0xA7
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0xF000,de,0,0xC9,column+32,0x42,0x8000)
  assert r[16:18]==[0x80,0xA3] and r[18:24]==initial[18:24] and r[8:12]==initial[8:12];cases+=1
 report=dict(passed=True,cases=cases,method='original_map_screen_tables_against_independent_address_walk_column_and_masks',
  output_bytes_per_case=1024,all_coordinate_bytes_on_each_axis=True,
  out_of_screen_inputs_preserve_actual_lookup_bytes=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapScreenTablesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

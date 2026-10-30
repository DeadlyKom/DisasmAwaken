"""Исходный DrawItem01, полное заполнение и десять глифов с независимой пиксельной сверкой."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckScreenUpdate import put
from CheckInsetFrame import bitmap_address


def main():
 station,_,banks=make_context();banks=[bytearray(b) for b in banks]
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 draws=disabled=0
 cases=[([0x22,1,0x10,0x10],mode) for mode in range(256)]
 for field in range(4):
  for value in range(256):
   counter=[0x22,1,0x10,0x10];counter[field]=value;cases.append((counter,0x81))
 for counter,mode in cases:
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x10)
  put(memory,0x7FFE,[255,63]);put(memory,0xA6EF,[1,0]);put(memory,0x983B,counter);memory[0x99B4]=mode
  put(memory,0xF10D,[2,3,20,2]);put(memory,0x4000,bytes([0x96])*8192)
  expected=bytearray([0x96])*8192
  for y in range(24,40):
   for column in range(2,22):expected[bitmap_address(y,column)-0x4000]=255
  ordered=[counter[1],counter[0],counter[2],counter[3]]
  codes=[0x30+(ordered[0]>>4),0x30+(ordered[0]&15),0x30+(ordered[1]>>4),0x30+(ordered[1]&15),58,
   0x30+(ordered[2]>>4),0x30+(ordered[2]&15),58,0x30+(ordered[3]>>4),0x30+(ordered[3]&15)]
  cursor=3
  for code in codes:
   for row,bits in enumerate(station[0x2A00+8*code:0x2A08+8*code]):
    for bit in range(8):
     x=16+cursor+bit
     if bits&(128>>bit):expected[bitmap_address(24+row,x>>3)-0x4000]^=128>>(x&7)
   cursor+=station[0x2900+code]
  sim.registers[:]=initial;r=sim.registers;r[PC]=0xA6EE;seen=[]
  for _ in range(30000):
   if r[PC]==0x3FFF:break
   if r[PC]==0xAE8D:seen.append(r[A])
   sim.opcodes[memory[r[PC]]]()
  else:raise AssertionError(('limit',counter,mode))
  assert seen==codes and bytes(memory[0x4000:0x6000])==expected,(counter,mode,seen,codes)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(1,20,counter[1],counter[3],0,0x45,0x8000)
  assert memory[0x99B4]==mode and memory[0x6320]==cursor and memory[0x6321]==0
  assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];draws+=1
 # Проверка отключения обёртки исходным RET, вся функция пропускается до загрузки индекса.
 for value in range(256):
  memory[0xA6EE]=0xC9;memory[0x99B4]=value;put(memory,0x7FFE,[255,63]);sim.registers[:]=initial
  sim.run(start=0xA6EE,stop=0x3FFF);r=sim.registers
  assert r[:12]==initial[:12] and r[16:24]==initial[16:24] and r[SP]==0x8000 and memory[0x99B4]==value;disabled+=1
 report=dict(passed=True,drawing_cases=draws,disabled_cases=disabled,
  method='original_counter_draw_fill_and_glyphs_against_independent_pixels',all_four_counter_bytes=True,all_fill_modes=True,
  glyph_calls_observed=True,bitmap_and_attributes_checked=True,calls_stubbed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/CounterDrawVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Все записи D0C3, включая зависимость старшего бита половины Y от вычитания в половине X."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context


class WrittenMemory(bytearray):
 track=False
 def __setitem__(self,index,value):
  if self.track:
   assert isinstance(index,int);self.writes.add(index&65535)
  super().__setitem__(index,value)


def expected(memory,max_x,max_y,min_x,min_y):
 writes={}
 def put(address,value,width=1):
  for offset in range(width):writes[address+offset]=(value>>(8*offset))&255
 def group(addresses,value):
  for address in addresses:put(address,value)
 put(0xDAD7,max_y*256+max_x,2);put(0xDAB6,min_y*256+min_x,2);put(0xDACC,max_y*256+min_x,2);put(0xDAC1,min_y*256+max_x,2)
 group((0xD90D,0xD9DA,0xD9ED,0xDA29,0xDA87),max_y);put(0xD468,max_y+1)
 group((0xD8EE,0xD98F,0xD9A2,0xDA3A,0xDA98),min_y)
 group((0xD940,0xD997,0xD9E2,0xDA84,0xDA95,0xDAA7),max_x);put(0xD44D,max_x+1)
 group((0xD921,0xD98C,0xD9D7,0xDA26,0xDA37,0xDA49),min_x)
 group((0xDFBE,0xE0ED,0xE112),max_y);group((0xE078,0xE1DB),(max_x+1)&255)
 half_x=((max_x+1)&255)//2;half_y=(((max_y+1)&255)>>1)|(128 if half_x<2 else 0)
 group((0xE109,0xDFBF,0xE00A,0xE017,0xE021,0xE071,0xE1BA,0xE089,0xE1F3,0xE07E,0xE1E8,0xDFC2,0xDFC1,0xE0E4),half_x)
 group((0xE173,0xE22A,0xE0C3),(half_x-2)&255);group((0xDFC0,0xE006,0xE094,0xE1BE),half_y)
 last_y=(max_y+1)&255;upper=memory[0xEE00]*256+memory[0xEF00];lower=memory[0xEE00+last_y]*256+memory[0xEF00+last_y]
 put(0xDFBC,lower,2);put(0xDFBA,upper,2)
 group((0xE11A,0xE273,0xE5DC),memory[0xF000]);group((0xE0F5,0xE25B,0xE5EE,0xE62C),memory[0xF000+max_x])
 return writes,half_y,upper


def main():
 _,source,banks=make_context();memory=WrittenMemory(65536);memory.writes=set();memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 cases=injected=0;addresses=None
 # Проверка всех 65536 верхних границ при нулевом минимуме, затем всех 65536 минимальных пар при заданном максимуме.
 for vary_max in (True,False):
  for pair in range(65536):
   max_x,max_y=(pair&255,pair>>8) if vary_max else (239,175);min_x,min_y=(0,0) if vary_max else (pair&255,pair>>8)
   writes,half_y,upper=expected(memory,max_x,max_y,min_x,min_y);sim.registers[:]=initial;r=sim.registers;r[H],r[L]=max_y,max_x;r[D],r[E]=min_y,min_x;r[F]=pair&255
   memory.writes.clear();memory.track=True;sim.run(start=0xD0C3,stop=0x3FFF);memory.track=False
   assert memory.writes==set(writes),(pair,vary_max,memory.writes^set(writes))
   assert all(memory[a]==value for a,value in writes.items()),(pair,vary_max)
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[SP])==(0xF000+max_x,upper,0x3600+max_x,memory[0xF000+max_x],0xB0|((max_y+1)&1),0x8000)
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[14]==initial[14]
   cases+=1;injected+=bool(half_y&128);addresses=sorted(writes)
 report=dict(passed=True,cases=cases,distinct_written_bytes=len(addresses),target_bytes=addresses,half_y_high_bit_from_half_x_subtract_cases=injected,
  method='original_D0C3_all_maximum_and_minimum_byte_pairs_independent_write_catalog_and_exact_registers',
  half_x_formula='((max_x+1) AND 255) SHR 1',half_y_formula='(((max_y+1) AND 255) SHR 1) OR (128 if half_x<2 else 0)',
  screen_table_builder_input_DE=0,geometry_validity_of_all_input_pairs_asserted=False,
  configured_clipping_execution_tested=False,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapRasterSetupVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in report.items() if k!='target_bytes'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

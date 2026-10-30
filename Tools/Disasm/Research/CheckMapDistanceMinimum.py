"""Сравнение квадрата байтового расстояния с самомодифицируемым минимумом, без подмены SumSquares8."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckSignedMultiply import sbc16_flags
from CheckWorldSignature import logical_flags


def distance(dx,dy):
 x=dx if dx<128 else 256-dx;y=dy if dy<128 else 256-dy
 return x*x+y*y,x*x,y*y


def main():
 _,source,_=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0xB200,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);cases=accepted=ties=0
 def check(dx,dy,minimum):
  nonlocal cases,accepted,ties
  total,xsquare,ysquare=distance(dx,dy);target_x=(dx*37+dy)&255;target_y=(dy*53+dx)&255
  # Подготовка независимой пары координат с заданными оборачиваемыми разностями.
  memory[0xB1FF:0xB203]=bytes([0xA7,(target_x+dx)&255,(target_y+dy)&255,0x5A]);points=bytes(memory[0xB1FF:0xB203])
  memory[0xC668:0xC66A]=minimum.to_bytes(2,'little');sim.registers[:]=initial;r=sim.registers;r[D],r[E]=target_y,target_x
  sim.run(start=0xC653,stop=0x3FFF)
  won=total<minimum;flags=sbc16_flags(total,minimum,0);a=xsquare>>8
  if won:flags=(flags&0xC4)|(a&0x28)|1
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[SP])==(0xB201,target_y*256+target_x,0x36C9,a,flags,0x8000),(dx,dy,minimum,list(r),flags)
  assert memory[0xC668:0xC66A]==(total if won else minimum).to_bytes(2,'little') and memory[0xB1FF:0xB203]==points
  assert r[16:24]==[ysquare>>8,logical_flags(ysquare&255),0,0xBE,minimum>>8,minimum&255,(total if won else (total-minimum)&65535)>>8,(total if won else (total-minimum)&65535)&255]
  assert r[8:12]==initial[8:12] and r[14]==initial[14]
  cases+=1;accepted+=won;ties+=total==minimum
 # Проверка всех 65536 разностей X/Y и соседних значений текущего минимума.
 for dx in range(256):
  for dy in range(256):
   total,_,_=distance(dx,dy)
   for minimum in sorted({0,1,(total-1)&65535,total,(total+1)&65535,65535}):check(dx,dy,minimum)
 # Проверка полного слова минимума для нулевого, малого и предельного расстояния.
 for dx,dy in ((0,0),(1,0),(128,128)):
  for minimum in range(65536):check(dx,dy,minimum)
 report=dict(passed=True,cases=cases,accepted_cases=accepted,equal_distance_rejected_cases=ties,
  method='original_C653_and_SumSquares8_all_wrapped_delta_pairs_minimum_boundaries_and_all_minimum_words_three_distances',
  signed_byte_absolute_value_preserved=True,delta_minus_128_magnitude_128=True,maximum_distance_squared=32768,
  strict_unsigned_comparison=True,point_pointer_advances_one_byte=True,exact_main_and_alternate_flags_checked=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapDistanceMinimumVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Выбор первого ближайшего из не более шести вариантов, настоящий помощник и сумма квадратов."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckMapDistanceMinimum import distance
from CheckSignedMultiply import sbc16_flags
from CheckWorldSignature import logical_flags


def main():
 _,source,_=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);rng=random.Random(0xC5E8);cases=ties=0
 pointer_operands=(0xC6CA,0xC6E7,0xC704,0xC721,0xC73E,0xC75B)
 pointers=tuple(0xB200+4*i for i in range(6))
 for operand,pointer in zip(pointer_operands,pointers):memory[operand:operand+2]=pointer.to_bytes(2,'little')

 def check(count,origin,pointer_xy,points):
  nonlocal cases,ties
  target=(pointer_xy-(8*((origin+0x0404)&65535)+0x0603))&65535;tx,ty=target&255,target>>8
  n=count if 1<=count<=5 else 6;best=65535;chosen=None
  for i,(x,y) in enumerate(points[:n]):
   old_min=best;q,xsquare,ysquare=distance((x-tx)&255,(y-ty)&255);won=q<best
   flags=sbc16_flags(q,best,0)
   if won:best=q;chosen=i;flags=(flags&0xC4)|((xsquare>>8)&0x28)|1
   elif q==best:ties+=1
  if n<6:flags=0x42|int(won)
  expected_b=0 if n<6 else (count-5)&255
  # Подготовка исходных точек, текущего указателя и нарочно постороннего старого минимума.
  for address,(x,y) in zip(pointers,points):memory[address-1:address+3]=bytes([0xA7,x,y,0x5A])
  snapshot=bytes(memory[0xB1FF:0xB218]);memory[0x6307:0x6309]=pointer_xy.to_bytes(2,'little');memory[0xC668:0xC66A]=bytes([0x34,0x12]);memory[0x9848]=0xA7
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=origin>>8,origin&255;r[A]=count
  sim.run(start=0xC5E8,stop=0x3FFF)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(pointers[n-1]+1,target,expected_b,chosen,chosen,flags,0x8000),(count,origin,pointer_xy,points,list(r),flags)
  assert memory[0x9848]==chosen and memory[0xC668:0xC66A]==best.to_bytes(2,'little') and memory[0xB1FF:0xB218]==snapshot
  alt_hl=q if won else (q-old_min)&65535
  assert r[16:24]==[ysquare>>8,logical_flags(ysquare&255),0,0xBE,old_min>>8,old_min&255,alt_hl>>8,alt_hl&255]
  assert r[8:12]==initial[8:12] and r[14]==initial[14]
  for operand,pointer in zip(pointer_operands,pointers):assert memory[operand:operand+2]==pointer.to_bytes(2,'little')
  cases+=1

 # Проверка всех кодов количества, случайных точек, равенства и первого/последнего лучшего варианта.
 for count in range(256):
  for i in range(128):
   origin=rng.randrange(65536);pointer_xy=rng.randrange(65536)
   points=[(rng.randrange(256),rng.randrange(256)) for _ in range(6)]
   if i==0:points=[(0,0)]*6
   if 1<=i<=6:
    target=(pointer_xy-(8*((origin+0x0404)&65535)+0x0603))&65535;points=[((target+1)&255,target>>8)]*6;points[i-1]=(target&255,target>>8)
   check(count,origin,pointer_xy,points)
 # Проверка каждого слова входного origin, включая связь координат через полный перенос 16 бит.
 for origin in range(65536):check(6,origin,(origin*257+0xA7)&65535,[(0,0),(255,255),(128,128),(127,127),(0,255),(255,0)])
 report=dict(passed=True,cases=cases,tied_candidate_comparisons=ties,all_count_bytes=True,all_origin_words=True,
  method='original_C5E8_C653_SumSquares8_exact_minimum_variant_registers_flags_and_source_points',
  count_zero_or_above_six_processes_six=True,word_carries_in_target_preserved=True,first_equal_candidate_kept=True,
  input_pointer_tables_synthetic=True,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/NearestMapVariantVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

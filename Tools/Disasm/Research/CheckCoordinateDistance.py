"""Полная исходная цепочка разностей, квадратов, деления на 9 и корня до записи 9908."""
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckSignedMultiply import signed
from CheckSignedDivision import expected as division
from CheckSeededRoot import reference as root
from CheckWorldSignature import logical_flags
from CheckMarketAccess import add16_flags


def reference(source,x0,y0,x1,y1,alt_carry):
 dx=abs(signed((x1-x0)&65535));dy=abs(signed((y1-y0)&65535))
 if not (dx|dy):return 0,0x44,0,y0,None
 def squared(value):return value*256 if value==32768 else value*value
 if dy>=256:
  value=squared(dy);hi=value>>16
  return 255,logical_flags((hi>>8)|(hi&255)),dx,value&65535,None
 if dx>=256:
  value=squared(dx);hi=value>>16
  return 255,logical_flags((hi>>8)|(hi&255)),0,value&65535,None
 total=dx*dx+dy*dy
 if total>65535:return 255,add16_flags(dy*dy,dx*dx,0x44),dx,dx*dx,None
 q=total//9;value=math.isqrt(q);_,_,_,bc,de=root(source,q,9)
 _,_,alt_flags,_,_,_=division(total,9,0,alt_carry,0)
 alt=(source[0x2C00+(q>>8)],0xA8 if source[0x2B00+(q>>8)]==255 else 0xA9) if q>=256 else (q&255,alt_flags)
 return max(value,1),logical_flags(value) if value else 0,bc,de,alt


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^AF':0x69CF},None,False)
 cases=overflow=zero=0
 def check(x0,y0,x1,y1):
  nonlocal cases,overflow,zero
  sim.registers[:]=initial;r=sim.registers;r[B],r[C],r[D],r[E]=y0&255,x0&255,y0>>8,x0>>8
  r[18],r[19],r[20],r[21]=y1&255,x1&255,y1>>8,x1>>8
  r[17]=0xCE|((x0^y1)&1);before=r.copy();memory[0x7FFE:0x8000]=bytes([255,63])
  sim.run(start=0xE7BA,stop=0xE7C2)
  assert r[SP]==0x7FF6 and bytes(memory[0x7FF6:0x8000])==bytes([0x9C,0x36,0x3A,0x5C,0x68,0x24,0x57,0x13,255,63])
  sim.run(start=0xE7C2,stop=0x3FFF)
  value,flags,bc,de,alt=reference(source,x0,y0,x1,y1,before[17]&1)
  assert (r[A],r[F],r[B]*256+r[C],r[D]*256+r[E],memory[0x9908])==(value,flags,bc,de,value),(x0,y0,x1,y1,list(r),(value,flags,bc,de,alt))
  assert r[H:L+1]==initial[H:L+1] and r[8:12]==initial[8:12] and r[18:24]==before[18:24] and r[SP]==0x8000
  assert (r[16],r[17])==(alt if alt is not None else tuple(before[16:18]))
  cases+=1;overflow+=value==255;zero+=value==0
 # Проверка всех малых пар модулей с переносом координат через границу слова в обоих направлениях.
 for dx in range(256):
  for dy in range(256):
   check(0xFFF0,0x1234,(0xFFF0+dx)&65535,(0x1234+dy)&65535)
   check(0x00F0,0xFEDC,(0x00F0-dx)&65535,(0xFEDC-dy)&65535)
 # Проверка больших модулей, переполнения разности и обоих положений кода 8000.
 for x in (0,1,255,256,257,32767,32768,32769,65280,65535):
  for y in (0,1,255,256,257,32767,32768,32769,65280,65535):
   check(0,0,x,y);check(0x9123,0xA456,(0x9123+x)&65535,(0xA456+y)&65535)
 report=dict(passed=True,cases=cases,overflow_returns=overflow,zero_returns=zero,
  method='complete_original_coordinate_distance_with_real_multiply_division_and_seeded_root',
  frame_checked=True,coordinate_wrap_checked=True,output_byte_9908_checked=True,
  quotient_is_at_most_7281=True,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/CoordinateDistanceVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Два исходных производителя произведений, реальный генератор и перспектива."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewMatrixComposeOracle import OUTPUT
from PreviewVertexGroupOracle import group,WORD_TARGETS,BYTE_TARGETS
from PreviewVertexProductsOracle import general,planar
PRODUCT_BYTES=(0xD910,0xD911,0xD913,0xD914,0xD916,0xD917,0xD953,0xD955,0xD956)


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=vertices=0;entries=collections.Counter()
 def word(pointer,value):m[pointer]=value&255;m[pointer+1]=value>>8
 def check(entry,coefficients,factors,mask,base,exponent,centres=(0,0)):
  nonlocal cases,vertices
  words,thirds=(general if entry==0xD8BE else planar)(coefficients,factors);offset=4+5*(cases%10);buffer=bytes((j*37+cases*11)&255 for j in range(272));expected=group(words,thirds,mask,base,exponent,centres,offset,buffer)
  m.recording=False;m[0xC5F0:0xC700]=buffer;m[0xD90D]=offset;word(0xDBB6,0xA55A);word(0xDBC0,0xC35A)
  if entry==0xD8BE:
   for row in range(3):
    for column in range(3):m[OUTPUT[row][column]]=coefficients[row][column]
  else:
   for pointer,value in zip((0xD861,0xD869,0xD871,0xD87B),coefficients):m[pointer]=value
  for pointer in PRODUCT_BYTES:m[pointer]=0xA5
  for pointer,value in zip((0xDA16,0xDA38,0xDAF6,0xDAE7,0xDBA5),(*base,*centres)):word(pointer,value)
  for pointer in (0xDA20,0xDA3B,0xDAF9):m[pointer]=6-exponent
  s.registers[:]=initial;r=s.registers;r[B],r[C],r[D]=factors;r[9]=mask;m.recording=True;m.writes=[];s.run(start=entry,stop=0x3FFF)
  assert bytes(m[0xC5F0:0xC700])==expected['buffer'],(entry,coefficients,factors,mask,expected)
  assert (r[A],r[F],r[H]*256+r[L],r[B]*256+r[C],r[D]*256+r[E],r[8]*256+r[9],r[10]*256+r[11],r[SP])==(*expected['af'],expected['stack'],expected['bc'],expected['de'],expected['ix'],expected['iy'],0x8000)
  assert tuple(r[16:24])==(*expected['alt_af'],expected['alt_bc']>>8,expected['alt_bc']&255,expected['alt_de']>>8,expected['alt_de']&255,expected['alt_hl']>>8,expected['alt_hl']&255)
  assert [m[p]+256*m[p+1] for p in (0xD910,0xD913,0xD916)]==list(words) and [m[p] for p in (0xD956,0xD955,0xD953)]==list(thirds)
  assert m[0xDA11:0xDA13]==[254,127] and m[0xD90D]==expected['stack']&255 and m[0x7FFE:0x8000]==[255,63]
  for index,pointer in WORD_TARGETS.items():assert m[pointer]+256*m[pointer+1]==expected['words'][index]
  for index,pointer in BYTE_TARGETS.items():assert m[pointer]==expected['thirds'][index]
  success=expected['last_success'] or (0xA55A,0xC35A);assert (m[0xDBB6]+256*m[0xDBB7],m[0xDBC0]+256*m[0xDBC1])==success
  allowed=set(PRODUCT_BYTES)|{0xDA11,0xDA12,0xD90D}|{p+j for p in WORD_TARGETS.values() for j in range(2)}|set(BYTE_TARGETS.values())|{0x7FFC,0x7FFD}
  for index,outcome in enumerate(expected['reasons']):
   stack=0xC600+offset+5*index;allowed.update(range(stack-4,stack))
   if outcome=='accepted':allowed.update(range(stack-6,stack-4));allowed.update((0xDBB6,0xDBB7,0xDBC0,0xDBC1))
  assert set(p for p,v in m.writes)==allowed
  assert m[0x7FFC]+256*m[0x7FFD]==(0xD905 if entry==0xD8BE else 0xD87F)
  cases+=1;vertices+=len(expected['vertices']);entries[format(entry,'04X')]+=1
 # Проверка каждого байта коэффициентов общей матрицы и каждого угла исходной короткой синусоиды.
 sine=raw[0x400:0x500]
 for value in range(256):
  for mask in (0,1,129,24,165,255):
   coefficients=tuple(tuple((value+row*53+column*17)&255 for column in range(3)) for row in range(3));factors=(value,value^255,(value*37)&255)
   check(0xD8BE,coefficients,factors,mask,(1500,10,65530),3,(0x8C00,0x5000))
   sin=sine[value];cos=sine[(value+64)&255];check(0xD85E,(cos,sin,sin,cos),factors,mask,(1500,10,65530),3,(0x8C00,0x5000))
 rng=random.Random(0xD8BE)
 for entry in (0xD8BE,0xD85E):
  for _ in range(1024):
   coefficients=tuple(tuple(rng.randrange(256) for j in range(3)) for i in range(3)) if entry==0xD8BE else tuple(rng.randrange(256) for i in range(4))
   check(entry,coefficients,tuple(rng.randrange(256) for i in range(3)),rng.randrange(256),tuple(rng.randrange(65536) for i in range(3)),rng.randrange(1,7),tuple(rng.randrange(65536) for i in range(2)))
 report=dict(passed=True,cases=cases,entries=dict(entries),projected_vertices=vertices,all_general_coefficient_bytes_sampled=True,all_original_planar_angles=True,all_nine_product_operands_checked=True,real_lookup_group_projection_and_cpu_return=True,all_registers_and_memory_write_boundaries_checked=True,whole_physical_model_walk_not_executed=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewVertexProductsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

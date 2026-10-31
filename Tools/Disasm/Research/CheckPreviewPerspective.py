"""Исходная перспектива, независимое деление и физические записи через рабочий SP."""
from pathlib import Path
import collections,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,PC,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewPerspectiveOracle import project,registers


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0xC604,'HL':0x3FFF,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;reasons=collections.Counter();exponents=collections.Counter()
 def word(pointer,value):m[pointer]=value&255;m[pointer+1]=value>>8
 def check(vertex,base,exponent,centres=(0,0)):
  nonlocal cases
  expected=project(vertex,base,exponent,centres);stack=0xC604+5*(cases%11);old=bytes((j*37+cases*11)&255 for j in range(8))
  m.recording=False;m[stack-6:stack+2]=old
  # Подготовка только исходных операндов реального проектора, сам делитель не подменяется.
  for pointer,value in zip((0xDA16,0xDA38,0xDAF6,0xDAE7,0xDBA5),(*base,*centres)):word(pointer,value)
  for pointer in (0xDA20,0xDA3B,0xDAF9):m[pointer]=6-exponent
  s.registers[:]=initial;r=s.registers;r[A]=vertex[0];r[E]=vertex[1];r[D]=vertex[2];r[SP]=stack;m.recording=True;m.writes=[]
  s.run(start=0xDA14,stop=0x3FFF)
  actual=(m[stack-2]+256*m[stack-1],m[stack-4]+256*m[stack-3])
  assert actual==(expected['first'],expected['second']),(vertex,base,exponent,centres,expected,actual)
  assert r[SP]==stack+5 and r[H]*256+r[L]==0x3FFF
  assert (r[B],r[C],r[D],r[E])==(0x36,0xC9,vertex[2],vertex[1]) and r[8:12]==initial[8:12]
  assert bytes(m[stack-6:stack-4])==old[:2] and bytes(m[stack:stack+2])==old[6:8]
  targets=set(range(stack-4,stack))
  if expected['valid']:
   targets.update(range(stack-6,stack-4));targets.update((0xDBB6,0xDBB7,0xDBC0,0xDBC1))
   assert m[0xDBB6]+256*m[0xDBB7]==expected['second'] and m[0xDBC0]+256*m[0xDBC1]==stack-6 and len(m.writes)==10
  else:assert len(m.writes)==4
  assert {pointer for pointer,value in m.writes}==targets
  # После заключительного EXX рабочий HL' содержит следующий адрес выходного стека.
  assert r[22]*256+r[23]==stack+5
  context=registers(vertex,base,exponent,centres,stack,old[0]+256*old[1])
  assert (r[A],r[F])==context['af'],(vertex,base,exponent,centres,expected,tuple(r[:8]),context)
  assert tuple(r[16:18])==context['alt_af'],(vertex,base,exponent,centres,expected,tuple(r[16:24]),context)
  assert (r[18]*256+r[19],r[20]*256+r[21])==(context['alt_bc'],context['alt_de']),(vertex,base,exponent,centres,expected,tuple(r[16:24]),context)
  cases+=1;reasons[expected['reason']]+=1;exponents[exponent]+=1
 # Проверка всех слов глубины при нулевых локальных координатах.
 for depth in range(65536):check((0,0,0),(depth,0,0),1)
 # Проверка всех слов первой координаты на трёх знаменателях и второй координаты на знаменателе 3.
 for depth in (1,256,32767):
  for coordinate in range(65536):check((0,0,0),(depth,coordinate,0),1)
 for coordinate in range(65536):check((0,0,0),(3,0,coordinate),1)
 # Проверка знакового расширения каждого локального байта при всех шести масштабах.
 for exponent in range(1,7):
  for value in range(256):
   for vertex in ((value,0,0),(0,value,0),(0,0,value)):
    for base in ((1500,0,0),(0,0,0),(32767,32767,32768),(65535,65535,65535)):check(vertex,base,exponent,(0x8C00,0x5000))
 rng=random.Random(0xDA14)
 for _ in range(4096):check(tuple(rng.randrange(256) for j in range(3)),tuple(rng.randrange(65536) for j in range(3)),rng.randrange(1,7),tuple(rng.randrange(65536) for j in range(2)))
 report=dict(passed=True,cases=cases,reasons=dict(reasons),exponents=dict(exponents),all_depth_words=True,all_first_axis_words_at_depths=[1,256,32767],all_second_axis_words_at_depth=3,all_local_bytes_at_six_scales=True,independent_signed_division_and_rejection_formula=True,exact_output_words_and_write_boundaries=True,real_working_sp_and_indirect_continuation=True,main_bc_de_hl_and_index_context_checked=True,exact_af_and_alternate_registers_checked=True,whole_vertex_group_not_executed=True,irq_executed=False,native_execution=False,assembly_executed=False,original_projection_sha256=hashlib.sha256(raw[0x1A14:0x1BD9]).hexdigest())
 (ROOT/'Tools/Disasm/Reports/PreviewPerspectiveVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

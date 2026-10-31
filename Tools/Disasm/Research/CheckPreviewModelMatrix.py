"""Проверка исходной матрицы EF5E, табличной арифметики и отражения переполнений."""
from pathlib import Path
import collections,json,math,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,PC,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewModelMatrixOracle import TARGETS,matrix,corrected


def main():
 raw=payload(6);sine=raw[0x400:0x500]
 # Проверка каждого исходного байта синусоиды, округление до ближайшего с ограничением модуля 127.
 assert sine==bytes(max(-127,min(127,round(128*math.sin(i*math.pi/128))))&255 for i in range(256))
 m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;branches=collections.Counter()
 def check(angles,flags):
  nonlocal cases
  expected=matrix(angles,flags,sine);m.recording=False;m[0xC21E:0xC221]=angles;m[0xCEFA]=flags
  for target in TARGETS:m[target]=0xA5
  s.registers[:]=initial;m.recording=True;m.writes=[];s.run(start=0xEF5E,stop=0x3FFF);r=s.registers
  assert tuple(m[p] for p in TARGETS)==expected['values'],(angles,flags,tuple(m[p] for p in TARGETS),expected)
  assert (r[A],r[F],r[H]*256+r[L],r[SP])==(*expected['af'],expected['hl'],0x8000),(angles,flags,r[:12],expected)
  assert r[16:24]==initial[16:24]
  if expected['shortcut']:
   assert r[B]==angles[1] and r[C:E+1]==initial[C:E+1] and r[8:12]==initial[8:12]
   assert set(p for p,v in m.writes)==set(TARGETS)
  else:
   assert (r[B]*256+r[C],r[D]*256+r[E],r[8]*256+r[9],r[10]*256+r[11])==(expected['bc'],expected['de'],expected['ix'],expected['iy'])
   assert set(p for p,v in m.writes)==set(TARGETS)|{0x7FFC,0x7FFD}
   assert m[0x7FFC:0x7FFE]==[0x47,0xF0]
  assert m[0x7FFE:0x8000]==[255,63]
  cases+=1;branches['shortcut' if expected['shortcut'] else 'general']+=1
 # Проверка всех углов упрощённой ветви и независимости от остальных битов признаков.
 for angle in range(256):
  for flags in (1,3,129,255):check((angle^91,angle,angle^173),flags)
 # Проверка всех одноосных углов, смешанных граничных значений и фиксированной случайной выборки.
 for axis in range(3):
  for angle in range(256):
   angles=[0,0,0];angles[axis]=angle;check(angles,(angle*2)&254)
 for first in (0,1,63,64,65,127,128,129,191,192,193,255):
  for second in (0,1,63,64,65,127,128,129,191,192,193,255):
   for third in (0,1,63,64,65,127,128,129,191,192,193,255):check((first,second,third),128)
 rng=random.Random(0xEF5E)
 for _ in range(4096):check(tuple(rng.randrange(256) for j in range(3)),rng.randrange(128)*2)
 # Проверка точных значений и флагов четырёх коррекций на всех байтовых парах.
 correction_cases=0
 for entry,stop,subtract in ((0xEFE0,0xEFEB,False),(0xF005,0xF010,True),(0xF022,0xF02D,True),(0xF047,0xF052,False)):
  for a in range(256):
   for b in range(256):
    r=s.registers;r[:]=initial;r[A]=a;r[8]=b;m.recording=False;s.run(start=entry,stop=stop)
    assert (r[A],r[F])==corrected(a,b,subtract),(hex(entry),a,b,r[A],r[F],corrected(a,b,subtract))
    correction_cases+=1
 report=dict(passed=True,matrix_cases=cases,branches=dict(branches),correction_cases=correction_cases,all_byte_pairs_in_four_corrections=True,sine_bytes_checked=256,sine_formula='clamp(round(128*sin(2*pi*i/256)),-127,127)',independent_numeric_matrix_and_register_oracle=True,all_nine_coefficient_operands_checked=True,exact_stack_writes_checked=True,all_preserved_context_checked=True,irq_executed=False,native_execution=False,assembly_executed=False,full_frame_semantics_proved=False)
 (ROOT/'Tools/Disasm/Reports/PreviewModelMatrixVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

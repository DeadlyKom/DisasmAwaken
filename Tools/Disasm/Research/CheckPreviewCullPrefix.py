"""Проверка трёх предварительных знаковых тестов и общего расчёта глубины с радиусом."""
from pathlib import Path
import json,sys,random,collections
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,PC,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckPreviewTransform import adc16


def main():
 m=Memory([0]*65536);raw=payload(6);m[0xC000:0xC000+len(raw)]=raw
 s=Simulator(m);initial=get_registers({'SP':0xCDC9,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 paths=collections.Counter();outcomes=collections.Counter();cases=0
 def check(depth,exponent,size,coordinates):
  nonlocal cases
  radius=size<<(exponent-1);expected,flags=adc16(depth,radius,0);m.recording=False
  def word(ptr,value):m[ptr]=value&255;m[ptr+1]=value>>8
  word(0xEEEF,0x7FFE);word(0xDA16,depth)
  for ptr,value in zip((0xEB7F,0xEBA0,0xEB8D),coordinates):word(ptr,value)
  s.registers[:]=initial;r=s.registers;r[PC]=0xED62;r[H]=radius>>8;r[L]=radius&255;r[A]=6-exponent;r[2]=exponent;r[3]=size;m.recording=True;m.writes=[];path='all_three'
  for _ in range(80):
   pc=r[PC]
   if pc in (0xEDB0,0xECAE):break
   if pc==0xED7B and r[F]&128:path='first_negative'
   if pc==0xED8F and r[F]&128:path='second_negative'
   s.run()
  else:raise AssertionError('Не завершён предварительный блок отсечения')
  assert r[PC]==(0xECAE if flags&128 else 0xEDB0)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[2],r[3],r[A],r[F],r[SP])==(expected,radius,exponent,size,6-exponent,flags,0x7FFE)
  expected_index=list(initial[8:12])
  if not flags&128:expected_index[1]=size
  assert r[8:12]==expected_index and r[16:24]==initial[16:24]
  assert len(m.writes)=={'first_negative':4,'second_negative':6,'all_three':8}[path]
  assert dict(m.writes)=={0x7FFA:radius&255,0x7FFB:radius>>8,0x7FFC:size,0x7FFD:exponent}
  paths[path]+=1;outcomes['rejected_by_depth_plus_radius_sign' if flags&128 else 'continued_to_cone_tests']+=1;cases+=1
 # Проверка каждого слова преобразованной глубины при допустимом размере и показателе масштаба.
 for depth in range(65536):check(depth,depth%6+1,(depth*73)&255,((depth*53+19)&65535,(depth*89+31)&65535,(depth*113+47)&65535))
 # Проверка независимо изменяемых координат при той же формуле общего выхода.
 rng=random.Random(0xED62)
 for _ in range(4096):check(rng.randrange(65536),rng.randrange(1,7),rng.randrange(256),tuple(rng.randrange(65536) for j in range(3)))
 assert all(paths[name] for name in ('first_negative','second_negative','all_three'))
 report=dict(passed=True,cases=cases,all_depth_words=True,paths=dict(paths),outcomes=dict(outcomes),only_final_depth_plus_radius_controls_exit=True,preliminary_coordinates_do_not_affect_final_registers=True,exact_four_stack_scratch_bytes=True,sp_restored_from_original_operand=True,next_cone_tests_not_executed=True,original_instructions_unchanged=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewCullPrefixVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

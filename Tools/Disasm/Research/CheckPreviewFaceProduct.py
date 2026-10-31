"""Исходный E869, полный результат, флаги, три арифметические ветви и край минус 32768."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckWorldSignature import logical_flags
from PreviewFaceProductOracle import product


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=extremes=0;branches=collections.Counter()
 def check(first,second):
  nonlocal cases,extremes
  expected=product(first,second);s.registers[:]=initial;r=s.registers;r[H],r[L]=first>>8,first&255;r[D],r[E]=second>>8,second&255;m.recording=True;m.writes=[];s.run(start=0xE869,stop=0x3FFF)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[8]*256+r[9],r[SP])==(expected['hl'],expected['de'],expected['bc'],*expected['af'],expected['ix'],0x8000),(first,second,r[:12],expected)
  assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
  sign=(first>>8)^(second>>8);assert set(m.writes)=={(0x7FFC,logical_flags(sign)),(0x7FFD,sign)} and len(m.writes)==2
  cases+=1;extremes+=expected['extreme_multiplier_lost'];branches['long' if expected['large'] else ('byte' if abs(first-65536 if first&32768 else first)<256 and abs(second-65536 if second&32768 else second)<256 else 'mixed')]+=1
 # Проверка каждого слова в обеих ролях на крайних, единичных и граничных множителях.
 for fixed in (0,1,255,256,32767,32768,65535):
  for value in range(65536):check(value,fixed);check(fixed,value)
 rng=random.Random(0xE869)
 for _ in range(4096):check(rng.randrange(65536),rng.randrange(65536))
 report=dict(passed=True,cases=cases,branches=dict(branches),extreme_multiplier_cases=extremes,all_words_in_both_roles_at_seven_factors=True,independent_signed_32_bit_result_and_register_flags=True,original_extreme_multiplier_loss_preserved=True,exact_cpu_stack_writes=True,alternate_and_index_registers_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewFaceProductVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Исходные восемь шагов D4DF, все байтовые делимые и крайние расширенные входы."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewSlopeDivisionOracle import divide


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=canonical=0
 def check(high,low,divisor,carry):
  nonlocal cases,canonical
  expected=divide(high,low,divisor,carry);s.registers[:]=initial;r=s.registers;r[A]=high;r[E]=low;r[D]=divisor;r[F]=(r[F]&254)|carry;m.recording=True;m.writes=[];s.run(start=0xD4DF,stop=0x3FFF)
  assert (r[A],r[F],r[D],r[E],r[SP])==(expected['remainder'],expected['flags'],divisor,expected['encoded'],0x8000),(high,low,divisor,carry,r[:8],expected)
  assert r[2:4]==initial[2:4] and r[6:12]==initial[6:12] and r[16:24]==initial[16:24] and not m.writes
  assert ((r[E]*2+(r[F]&1))&255)==expected['inverse_quotient']
  if high==0 and divisor:
   quotient,remainder=divmod(low,divisor);assert (expected['quotient_bits'],r[A])==(quotient,remainder);canonical+=1
  cases+=1
 # Проверка всех канонических байтовых делимых, делителей и обоих входных Carry.
 for divisor in range(256):
  for low in range(256):
   for carry in (0,1):check(0,low,divisor,carry)
 # Проверка всех составных слов A:E на семи делителях, включая нуль и границы потери старшего разряда.
 for divisor in (0,1,7,127,128,129,255):
  for value in range(65536):
   for carry in (0,1):check(value>>8,value&255,divisor,carry)
 report=dict(passed=True,cases=cases,canonical_nonzero_divisor_cases=canonical,all_byte_dividend_and_divisor_pairs=True,all_word_inputs_at_seven_divisors=True,both_input_carries_checked=True,independent_byte_remainder_and_inverse_quotient_model=True,exact_flags_and_preserved_context=True,zero_divisor_original_behavior_preserved=True,discarded_ninth_bit_preserved=True,no_memory_writes=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewSlopeDivisionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

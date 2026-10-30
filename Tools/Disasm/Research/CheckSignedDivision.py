"""Деление HL:A:A' на DE, независимые частное и флаги при допустимом 16-битном результате."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckSignedMultiply import sbc16_flags


def expected(number,divisor,carry,alt_carry,initial_bc):
 raw=number&0xFFFFFFFF;negative_count=int(number<0)+int(divisor<0);magnitude=(~raw)&0xFFFFFFFF if number<0 else raw
 denominator=abs(divisor);q=magnitude//denominator
 if q>=65536:raise ValueError('Вне проверяемого договора, частное не помещается в слово')
 result=q if negative_count%2==0 else q^65535
 # Флаги верхнего байта берутся из восьмой попытки деления до EX AF,AF'.
 trial=2*((magnitude>>9)%denominator)+((magnitude>>8)&1)
 flags=(sbc16_flags(trial,denominator,0)&0xC4)|((result>>8)&0x28)|(1 if negative_count else carry)
 if negative_count%2==0:flags|=0x12
 alt_flags=(0x80 if negative_count==0 else 0)|((result&255)&0x28)|0x12|alt_carry if negative_count%2==0 else 0x42|alt_carry
 bc=(raw>>16) if number<0 else (divisor&65535) if divisor<0 else initial_bc
 return result,flags,alt_flags,bc,denominator,0x2400|((negative_count-1)&255)


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);cases=wide=0
 def check(number,divisor,selector):
  raw=number&0xFFFFFFFF;carry=selector&1;alt_carry=(selector>>1)&1
  sim.registers[:]=initial;r=sim.registers
  r[H],r[L]=(raw>>24)&255,(raw>>16)&255;r[A]=(raw>>8)&255;r[F]=(0x80 if divisor<0 else 0)|carry
  r[16]=raw&255;r[17]=0x5C|alt_carry;r[D],r[E]=(divisor>>8)&255,divisor&255
  sim.run(start=0xDCFB,stop=0x3FFF)
  result,flags,alt_flags,bc,denominator,ix=expected(number,divisor,carry,alt_carry,0x36C9)
  assert (r[H]*256+r[L],r[A],r[F],r[16],r[17],r[B]*256+r[C],r[D]*256+r[E],r[8]*256+r[9])==(result,result>>8,flags,result&255,alt_flags,bc,denominator,ix),(number,divisor,selector,list(r),(result,flags,alt_flags,bc,denominator,ix))
  assert r[SP]==0x8000 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24]
 divisors=(1,2,9,255,256,32767,-1,-9,-255,-32768)
 for divisor in divisors:
  for value in range(65536):
   check(value,divisor,value);check(-value-1,divisor,value);cases+=2
 rng=random.Random(0xDCFB)
 for divisor in divisors:
  for _ in range(1024):
   value=rng.randrange(abs(divisor)*65536);check(value,divisor,value);check(-value-1,divisor,value);wide+=2
 report=dict(passed=True,word_input_cases=cases,wide_input_cases=wide,
  method='original_32_to_16_division_against_integer_quotient_and_independent_flag_formula',
  negative_numerator_uses_ones_complement=True,negative_quotient_uses_ones_complement=True,
  denominator_sign_is_input_F_sign=True,zero_divisor_tested=False,overflow_cases_tested=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SignedDivisionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Два исходных 8-битных квадрата, полная сумма и точные основные/альтернативные флаги."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckWorldSignature import logical_flags


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);memory[0x7FFE:0x8000]=bytes([255,63]);cases=overflow=0
 # Проверка всех 65536 пар, в том числе переноса за пределы суммы слова и нулевых младших байтов квадратов.
 for x in range(256):
  for y in range(256):
   first=x*x;second=y*y;total=first+second;result=total&65535;sim.registers[:]=initial;r=sim.registers;r[A]=x;r[F]=x^y;r[16]=y;r[17]=(x+y)&255
   sim.run(start=0xC368,stop=0x3FFF)
   flags=(logical_flags(second&255)&0xC4)|((result>>8)&0x28)|(((first^second^result)>>8)&0x10)|int(total>65535)
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[16],r[17],r[SP])==(result,second,0xC9,second>>8,flags,first>>8,logical_flags(first&255),0x8000),(x,y,list(r),flags)
   assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and r[14]==initial[14];cases+=1;overflow+=total>65535
 report=dict(passed=True,cases=cases,word_sum_overflow_cases=overflow,method='original_two_8_bit_squares_against_integer_products_all_input_pairs_exact_flags_and_registers',
  main_flags_SZPV_from_second_low_square=True,alternate_flags_from_first_low_square=True,all_input_AF_flags_discarded=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SumSquares8Verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

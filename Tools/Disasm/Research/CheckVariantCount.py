"""Исходный вычислитель количества A7F5, XOR четырёх байтов выбранного ключа и точные флаги."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from CheckRowHighlight import make_context
from CheckAnimatedVariants import dec_flags


def main():
 _,_,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);counts=[0]*7;cases=0
 # Проверка всех первых слов с двумя независимыми последовательностями вторых слов, включая оба нулевых выхода.
 for seed in (0,0xA7F5):
  for first in range(65536):
   second=(first*313+seed)&65535;packed=first.to_bytes(2,'little')+second.to_bytes(2,'little');memory[0x9844:0x9848]=packed
   raw=packed[0]^packed[1]^packed[2]^packed[3];code=raw&7;result=max(code-1,0);flags=dec_flags(code,0) if code else 0x44
   memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.run(start=0xA7F5,stop=0x3FFF);r=sim.registers
   assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==(first,second,result,flags,0x8000)
   assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and memory[0x9844:0x9848]==packed
   counts[result]+=1;cases+=1
 report=dict(passed=True,cases=cases,counts_by_result=counts,range=[0,6],zero_return_for_low_three_bit_codes=[0,1],
  method='original_A7F5_against_four_byte_xor_low_three_bits_saturating_decrement_and_exact_AF',
  unrelated_A806_tail_not_claimed=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/VariantCountVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

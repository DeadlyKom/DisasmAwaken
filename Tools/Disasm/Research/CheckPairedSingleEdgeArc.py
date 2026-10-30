"""Оба прохода E228 и вход после SUB, фактический выбор по E и повторная подготовка края."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckSingleEdgeArc import reference
from CheckWorldSignature import logical_flags


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 sim.registers[:]=initial;sim.registers[H],sim.registers[L]=175,239;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xD0C3,stop=0x3FFF)
 cases=middle=0
 def check(radius,offset,cy,selector,mode,pattern,internal=False):
  nonlocal cases,middle
  left_edge=bool(selector&1);raw=bytes([pattern])*0x1B00
  first,_=reference(raw,radius,offset,cy,left_edge,True,mode);expected,_=reference(first,radius,offset,cy,left_edge,False,mode)
  memory[0x4000:0x5B00]=raw;memory[0xDFAD:0xDFB4]=bytes([0xA6,radius,0,offset,cy-16,0,0]);memory[0xDFB8]=0xA7
  sim.registers[:]=initial;r=sim.registers;r[B]=offset;r[E]=selector;r[A]=(offset-118)&255 if internal else 0x5A
  sim.run(start=0xE22B if internal else 0xE228,stop=0x3FFF)
  assert memory[0x4000:0x5B00]==expected,(radius,offset,cy,selector,mode,pattern,internal)
  low=memory[0xEF00+cy-16]|(30 if left_edge else 1)
  assert (r[A],r[F],r[SP],r[16])==(low,logical_flags(low),0x8000,(offset-118)&255)
  assert memory[0xDFB9]==0 and memory[0xDFB8]==(0xA7 if left_edge else offset) and r[8:12]==initial[8:12]
  cases+=1;middle+=internal
 for mode in (0x38,0x30):
  memory[0xDFC4]=mode==0x38;sim.registers[:]=initial;sim.run(start=0xDFC3,stop=0xDFD8)
  # Проверка двух половин с повторным чтением исходной строки и начального радиуса между проходами.
  for radius in range(9,81):
   for offset in (0,16,32,48,64,80,96,100):
    for cy in (17,95,190):
     for selector in (0,1):
      for pattern in (0,0xA7):check(radius,offset,cy,selector,mode,pattern)
  # Проверка всех байтов E, а также самостоятельного E22B с явно переданным A-пределом.
  for selector in range(256):
   for internal in (False,True):check(40,80,95,selector,mode,0xA7,internal)
 report=dict(passed=True,cases=cases,internal_E22B_cases=middle,all_E_selector_bytes=True,
  method='actual_E228_and_E22B_both_halves_against_composed_single_edge_recurrences_complete_bitmap_final_AF_and_stack',
  selector_bit_0_not_memory_quadrant=True,upper_and_lower_passes_xor_shared_start_row_twice=True,
  full_DFC3_dispatch_proved=False,arbitrary_clipped_inputs_proved=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PairedSingleEdgeArcVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

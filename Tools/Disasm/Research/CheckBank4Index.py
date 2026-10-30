"""Исходный сумматор двух байтов из банка 4 с возвратом банка LANG 6."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import logical_flags


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 memory=SliceableMemory(banks=banks,out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 count=0
 inputs=((a,b,0x16) for a in range(256) for b in range(256))
 from itertools import chain
 for first,second,old in chain(inputs,((0xFF,1,old) for old in range(32))):
  memory.out7ffd(old);memory[0x6306]=old;memory.banks[4][0x2146]=first;memory.banks[4][0x2147]=0xE3;memory.banks[4][0x2148]=second
  put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;trace=PortTrace(sim);sim.set_tracer(trace)
  sim.run(start=0xAA1D,stop=0x3FFF);final=(old&0xF8)|0x16
  assert (r[A],r[F],r[B],r[C],r[SP])==(final,logical_flags(final),0,(first+second)&255,0x8000)
  assert r[H]*256+r[L]==0x1357 and r[D]*256+r[E]==0x247A and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
  assert trace.writes==[(0x7FFD,(old&0xF8)|0x14),(0x7FFD,final)] and memory[0x6306]==final and memory.o7ffd==final
  count+=1
 report=dict(passed=True,cases=count,method='original_bank4_sum_and_bank6_return',all_byte_pairs=True,all_unlocked_pages=True,
  high_byte_E147_ignored=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/Bank4IndexVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

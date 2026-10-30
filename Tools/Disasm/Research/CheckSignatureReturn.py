"""Исходные обёртки характеристики с возвратом банка LANG 6."""
from pathlib import Path
from itertools import product
import sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import signature,logical_flags


def main():
 _,_,base=make_context();base=[bytearray(b) for b in base]
 memory=SliceableMemory(banks=[b.copy() for b in base],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 count=0
 for entry,first,second,variant,old in product((0xA480,0xA48B),(0,0x4734,0x493A,0x4B38,0xFFFF),(0,0xFFFF),(0,1,255),range(32)):
  memory.banks=[b.copy() for b in base];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(old)
  memory[0x6306]=old;put(memory,0x983F,list(first.to_bytes(2,'little')+second.to_bytes(2,'little')+bytes([variant])))
  put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;r[H],r[L]=first>>8,first&255;r[D],r[E]=second>>8,second&255;r[A]=variant
  trace=PortTrace(sim);sim.set_tracer(trace);sim.run(start=entry,stop=0x3FFF);result=signature(first,second,variant)
  assert tuple(r[i] for i in (H,L,D,E,A,F))==tuple(result[k] for k in ('major','size','region','minor','result','flags'))
  final=(old&0xF8)|0x16
  assert trace.writes==[(0x7FFD,(old&0xF8)|0x11),(0x7FFD,(old&0xF8)|0x10),(0x7FFD,final)]
  assert memory.o7ffd==final and memory[0x6306]==final and r[SP]==0x8000
  assert (r[16],r[17])==(final,logical_flags(final)) and r[B]*256+r[C]==0x36C9
  assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
  count+=1
 report=dict(passed=True,cases=count,method='original_signature_wrappers_returning_bank6',physical_page_writes=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SignatureReturnVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

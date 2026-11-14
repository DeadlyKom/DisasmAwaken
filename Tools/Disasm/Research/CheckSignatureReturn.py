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
from CheckWorldSignature import signature,logical_flags,step_key
from CheckBank4Index import WriteMemory


def main():
 _,_,base=make_context();base=[bytearray(b) for b in base]
 memory=WriteMemory(banks=[b.copy() for b in base],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 count=0
 for entry,first,second,variant,old in product((0xA480,0xA48B),(0,0x4734,0x493A,0x4B38,0xFFFF),(0,0xFFFF),(0,1,255),range(32)):
  memory.banks=[b.copy() for b in base];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(old)
  memory[0x6306]=old;put(memory,0x983F,list(first.to_bytes(2,'little')+second.to_bytes(2,'little')+bytes([variant])))
  put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;r[H],r[L]=first>>8,first&255;r[D],r[E]=second>>8,second&255;r[A]=variant
  trace=PortTrace(sim);sim.set_tracer(trace)
  memory.cpu_writes.clear();memory.recording=True;sim.run(start=entry,stop=0x3FFF);memory.recording=False
  result=signature(first,second,variant)
  # Расчёт всех нестековых записей по исходным словам и Variant+1 шагам.
  expected=[(0x6306,(old&0xF8)|0x11)]
  def key_writes(u,v):
   data=u.to_bytes(2,'little')+v.to_bytes(2,'little')
   return [(0x631C+i,value) for i,value in enumerate(data)]
  u,v=first,second;expected+=key_writes(u,v)
  for iteration in range(variant+1):
   u,v,_=step_key(u,v);expected+=key_writes(u,v)
  expected.extend(((0x6306,(old&0xF8)|0x10),(0x6306,(old&0xF8)|0x16)))
  persistent=[(a,v) for a,v in memory.cpu_writes if not 0x7FF2<=a<0x7FFE]
  assert persistent==expected,(entry,first,second,variant,old,persistent,expected)
  assert bytes(memory[0x7FFE:0x8000])==bytes([255,63])
  assert bytes(memory[0x631C:0x6320])==u.to_bytes(2,'little')+v.to_bytes(2,'little')
  assert tuple(r[i] for i in (H,L,D,E,A,F))==tuple(result[k] for k in ('major','size','region','minor','result','flags'))
  final=(old&0xF8)|0x16
  assert trace.writes==[(0x7FFD,(old&0xF8)|0x11),(0x7FFD,(old&0xF8)|0x10),(0x7FFD,final)]
  assert memory.o7ffd==final and memory[0x6306]==final and r[SP]==0x8000
  assert (r[16],r[17])==(final,logical_flags(final)) and r[B]*256+r[C]==0x36C9
  assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
  count+=1
 report=dict(passed=True,cases=count,method='original_signature_wrappers_returning_bank6',physical_page_writes=True,
  exact_non_stack_write_sequence_checked=True,bounded_stack_write_addresses_checked=True,
  stack_write_address_interval=[0x7FF2,0x7FFE],original_return_word_preserved=True,
  final_working_key_checked=True,all_signature_words_and_variants_checked=False,
  full_R_proved=False,physical_paging_lock_emulation_proved=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SignatureReturnVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

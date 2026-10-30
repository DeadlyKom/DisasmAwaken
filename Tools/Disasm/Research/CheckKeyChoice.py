"""Оригинальный выбор двух ключей из LANG через фиксированные обёртки с возвратом банка 6."""
from pathlib import Path
from itertools import product
import json,sys
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
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==5)
 lang=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();base[6][:len(lang)]=lang
 memory=SliceableMemory(banks=[b.copy() for b in base],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x365D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 count=0
 for handler in (0xC924,0xC61B,0xC623,0xC62A,0xC632,0xC63A):
  for choice,old,variant in product(range(256),(0x16,0x1E),(0,1,255)):
   memory.banks=[b.copy() for b in base];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(old)
   memory[0x6306]=old;put(memory,0x7FFE,[255,63])
   current=(0x4B38,0x1357,variant);other=(0xFFFF,0x2468,255-variant)
   for address,values in ((0x983F,current),(0x9844,other)):
    a,b,v=values;put(memory,address,list(a.to_bytes(2,'little')+b.to_bytes(2,'little')+bytes([v])))
   sim.registers[:]=initial;r=sim.registers;r[C]=choice
   if handler!=0xC924:
    r[SP]=0x7FFC;put(memory,0x7FFC,[choice,0x36])
   trace=PortTrace(sim);sim.set_tracer(trace)
   sim.run(start=handler,stop=0x3FFF);expected=signature(*(other if choice==1 else current))
   values=[expected[k] for k in ('major','size','region','minor','result','flags')]
   if handler!=0xC924:
    field={0xC61B:'major',0xC623:'minor',0xC62A:'size',0xC632:'result',0xC63A:'region'}[handler]
    if handler==0xC62A:values[0:2]=[expected['region'],expected['minor']]
    values[2:4]=[0,expected[field]]
   assert tuple(r[i] for i in (H,L,D,E,A,F))==tuple(values)
   assert r[C]==(choice-1)&255 and r[B]==0x36 and r[SP]==0x8000
   assert memory.o7ffd==old and memory[0x6306]==old
   assert trace.writes==[(0x7FFD,(old&0xF8)|0x11),(0x7FFD,(old&0xF8)|0x10),(0x7FFD,old)]
   assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and (r[16],r[17])==(old,logical_flags(old))
   count+=1
 report=dict(passed=True,cases=count,method='original_LANG_key_choice_and_real_banked_wrappers',all_choice_bytes=True,field_handlers=5,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/KeyChoiceVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

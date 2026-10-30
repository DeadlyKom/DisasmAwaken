"""Прямые проверки порога с настоящим разбором индекса и банковым запросом текущего ключа."""
from pathlib import Path
from itertools import product
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import signature
from CheckGlyphRenderer import compare_flags
from CheckMarketAccess import add16_flags


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 lang=(ROOT/(e['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=lang
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x365D,'IX':0xB000,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0
 for entry,base,row_address,offset_address in ((0xC28F,0x95F0,0x7217,0x71B9),(0xC2BB,0x9632,0x73D8,0x737D)):
  inputs=[]
  for variant,prefix in product((0,1,7,255),(b'',b'0',b'1',b'30',b'256',b'65535',b'99999')):
   size=signature(0x4B38,0x1357,variant)['size']
   inputs.extend((variant,prefix,t) for t in (0,size-1,size,size+1,127,255))
  inputs.extend((1,b'',t) for t in range(256))
  for variant,prefix,threshold in inputs:
   memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x16)
   memory[0x6306]=0x16;put(memory,0x7FFE,[255,63]);put(memory,0x983F,[0x38,0x4B,0x57,0x13,variant])
   memory[row_address]=29;memory[offset_address]=7;text=prefix+b'!\r';put(memory,0xB000,list(text))
   index=(int(prefix)-1)&65535 if prefix else 36;delta=(2*index)&65535;address=(base+delta)&65535;memory[address]=threshold
   parsed_flags=compare_flags(33,46 if prefix else 48);saved_flags=add16_flags(delta,base,parsed_flags)
   size=signature(0x4B38,0x1357,variant)['size'];expected=int(size>=threshold)
   sim.registers[:]=initial;r=sim.registers;trace=PortTrace(sim);sim.set_tracer(trace);sim.run(start=entry,stop=0x3FFF)
   assert (r[A],r[F],r[D],r[E],r[H],r[L],r[B],r[C],r[SP])==(expected,0 if expected else compare_flags(size,threshold),0,expected,threshold,saved_flags,0,36,0x8000)
   assert r[8]*256+r[9]==0xB000+len(prefix) and r[10:12]==initial[10:12] and r[18]==4 and r[19:24]==initial[19:24]
   assert trace.writes==[(0x7FFD,0x11),(0x7FFD,0x10),(0x7FFD,0x16)] and memory.o7ffd==0x16
   cases+=1
 report=dict(passed=True,cases=cases,method='original_two_entry_threshold_checks_with_actual_parser_and_banks',
  all_threshold_bytes=True,saved_AF_restored_to_HL=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EntryThresholdVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Четыре исходных селектора характеристик ключа, фактические символы s/c/u и p/g."""
from pathlib import Path
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


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 lang=(ROOT/(e['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=lang
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0
 for entry,default,anchor,count,fields in ((0xC383,0,0xCA25,3,{'s':'major','c':'minor','u':'size'}),
  (0xC399,1,0xCA25,3,{'s':'major','c':'minor','u':'size'}),
  (0xC3AF,0,0xCA2E,2,{'p':'result','g':'region'}),(0xC3C5,1,0xCA2E,2,{'p':'result','g':'region'})):
  for variant in (0,1,255):
   current=(0x4B38,0x1357,variant);other=(0xFFFF,0x2468,255-variant)
   for prefix in [b'']+[str(n).encode() for n in range(257)]+[b'65535',b'99999']:
    for suffix in ['']+list(fields):
     memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x16)
     memory[0x6306]=0x16;put(memory,0x7FFE,[255,63])
     for address,(a,b,v) in ((0x983F,current),(0x9844,other)):put(memory,address,list(a.to_bytes(2,'little')+b.to_bytes(2,'little')+bytes([v])))
     text=prefix+(b'.'+suffix.encode() if suffix else b'!')+b'\r';put(memory,0xB000,list(text));sim.registers[:]=initial;r=sim.registers
     trace=PortTrace(sim);sim.set_tracer(trace);index=((int(prefix)-1)&65535) if prefix else default
     sim.run(start=entry,stop=0x3FFF)
     if suffix:
      info=signature(*(other if index&255==1 else current));hl=info['region']*256+info['minor'] if suffix=='u' else info['major']*256+info['size']
      assert (r[D]*256+r[E],r[H]*256+r[L],r[B],r[C],r[A],r[F])==(info[fields[suffix]],hl,index>>8,((index&255)-1)&255,info['result'],info['flags'])
      assert trace.writes==[(0x7FFD,0x11),(0x7FFD,0x10),(0x7FFD,0x16)]
     else:
      assert (r[D]*256+r[E],r[H]*256+r[L],r[B],r[C],r[A],r[F])==(anchor,index,0x36,default,33,compare_flags(33,46 if prefix else 48))
      assert not trace.writes
     assert r[8]*256+r[9]==0xB000+len(prefix)+(2 if suffix else 0) and r[SP]==0x8000
     assert r[10:12]==initial[10:12] and r[18]==count and r[19:24]==initial[19:24]
     cases+=1
 report=dict(passed=True,cases=cases,method='original_four_key_field_selectors_and_banked_handlers',
  no_suffix_returns_table_anchor=True,all_choice_bytes=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/KeyFieldSelectorsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

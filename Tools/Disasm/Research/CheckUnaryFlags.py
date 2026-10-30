"""Четыре прямые записи режима и два выбора записи по индексу банка 4."""
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
from CheckWorldSignature import logical_flags
from CheckMarketAccess import add16_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();original=bytearray(65536);original[0xC000:0xC000+len(source)]=source
 memory=original.copy();sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69A5},None,False)
 flags_cases=selection_cases=0
 for number in list(range(256))+[256,65535,65536]:
  text=str(number).encode()+b'!';memory[:]=original;memory[0xB000:0xB000+len(text)]=text;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial
  sim.run(start=0xC6EA,stop=0x3FFF);parsed=sim.registers.copy();offset=number&65535
  for entry,mode in product((0xC177,0xC181,0xC189,0xC191),(0,1,2,127,128,255)):
   base={0xC177:0x9A1D,0xC181:0x9A1E,0xC189:0x9A32,0xC191:0x9A41}[entry]
   memory[:]=original;memory[0xB000:0xB000+len(text)]=text;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[16]=mode
   address=(base+offset)&65535;memory[address]=0xA7;sim.run(start=entry,stop=0x3FFF)
   assert memory[address]==mode and (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E],r[SP])==(mode,0xA5,address,base,0x8000)
   assert r[16]==parsed[A] and r[17]==add16_flags(offset,base,parsed[F]) and r[B:C+1]==parsed[B:C+1]
   assert r[8:12]==parsed[8:12] and r[18:24]==initial[18:24]
   flags_cases+=1
 _,_,banks=make_context();banks=[bytearray(b) for b in banks];banks[6][:len(source)]=source
 banked=SliceableMemory(banks=banks,out7ffd=0x16);bsim=Simulator(banked)
 for entry,field in ((0xC199,0x9849),(0xC1A7,0x984A)):
  for first,mode in product(range(256),(0,1,2,127,128,255)):
   banked.out7ffd(0x16);banked[0x6306]=0x16;banked.banks[4][0x2146]=first;banked.banks[4][0x2148]=73
   put(banked,0x7FFE,[255,63]);bsim.registers[:]=initial;r=bsim.registers;r[16]=mode;trace=PortTrace(bsim);bsim.set_tracer(trace)
   bsim.run(start=entry,stop=0x3FFF);index=(first+73)&255;value=index if mode else 255
   assert (banked[field],r[A],r[F],r[B],r[C],r[SP],r[16],r[17])==(value,value,logical_flags(mode),0,index,0x8000,0x16,logical_flags(0x16))
   assert r[H]*256+r[L]==0x1357 and r[D]*256+r[E]==0x247A and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
   assert trace.writes==[(0x7FFD,0x14),(0x7FFD,0x16)]
   selection_cases+=1
 report=dict(passed=True,method='original_unary_indexed_flag_stores_and_bank4_selection',flag_cases=flags_cases,selection_cases=selection_cases,
  arbitrary_alt_A_bytes_tested=True,all_selection_indices=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/UnaryFlagsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

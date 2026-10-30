"""Точная модель исходного частично проверяемого умножения, включая недокументированные флаги."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckWorldSignature import logical_flags
from CheckMarketAccess import add16_flags


def reference(left,right):
 product=0;flags=0
 for step in range(16):
  bit=(right>>15)&1;right=(right<<1)&65535
  flags=logical_flags(right>>8)|bit
  if bit:
   flags=add16_flags(product,left,flags);product=(product+left)&65535
  if step!=15:
   doubled=product*2;flags=add16_flags(product,product,flags);product=doubled&65535
   if doubled>65535:return 65535,product,right,flags,True
 return product,left,right,flags,False


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'AF':0x5A00,'IX':0xB000,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=errors=missed=0;examples=[]
 for left in range(65536):
  for right in (0,1,2,3,255,256,32767,65535):
   sim.registers[:]=initial;r=sim.registers;r[D],r[E]=left>>8,left&255;r[B],r[C]=right>>8,right&255;memory[0x7FFE:0x8000]=bytes([255,63])
   sim.run(start=0xC3DF,stop=0x3FFF);result,hl,bc,flags,error=reference(left,right)
   assert (r[D]*256+r[E],r[H]*256+r[L],r[B]*256+r[C],r[A],r[F],r[SP])==(result,hl,bc,0x5A,flags,0x8000),(left,right)
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
   if result!=min(left*right,65535):
    missed+=1
    if len(examples)<8:examples.append(dict(left=left,right=right,mathematical=left*right,returned=result,flags=flags))
   errors+=error;cases+=1
 report=dict(passed=True,cases=cases,method='original_unrolled_multiply_with_exact_carry_check_positions',
  detected_shift_overflows=errors,results_differing_from_saturating_product=missed,examples=examples,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MultiplyBranchesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

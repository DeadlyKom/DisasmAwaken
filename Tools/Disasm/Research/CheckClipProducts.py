"""Четыре исходных 32-битных произведения для пересечений границ, включая особый DE=8000."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckSignedMultiply import signed,sbc16_flags
from CheckWorldSignature import logical_flags


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 rng=random.Random(0xD8E2);cases=defects=0
 for entry,destination in ((0xD8E2,0xDE6B),(0xD901,0xDE6F),(0xD920,0xDE73),(0xD93F,0xDE77)):
  # Проверка всех вторых операндов при первом 256 и независимых случайных пар конечных точек.
  fixtures=[(value if entry!=0xD93F else (value+255)&65535,511 if entry==0xD901 else 256,0,0) for value in range(65536)]
  fixtures += [tuple(rng.randrange(65536) for _ in range(4)) for _ in range(4096)]
  for x1,y1,x2,y2 in fixtures:
   if entry in (0xD8E2,0xD901):left=(y1-(255 if entry==0xD901 else 0))&65535;right=(x1-x2)&65535;input_bc=255 if entry==0xD901 else 0
   else:left=(y1-y2)&65535;right=(x1-(255 if entry==0xD93F else 0))&65535;input_bc=y2
   mx,my=abs(signed(left)),abs(signed(right));large=mx>=256 and my>=256;small=mx<256 and my<256;defect=large and right==32768
   magnitude=mx*256 if defect else mx*my;negative=bool((left^right)&32768);product=(-magnitude if negative else magnitude)&0xFFFFFFFF
   points=x1.to_bytes(2,'little')+y1.to_bytes(2,'little')+bytes([0xA7])+x2.to_bytes(2,'little')+y2.to_bytes(2,'little')+bytes([0x5A]);memory[0xDE2F:0xDE39]=points
   memory[0xDE6B:0xDE7B]=bytes([0xA7])*16;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers
   sim.run(start=entry,stop=0x3FFF)
   expected=bytearray([0xA7]*16);expected[destination-0xDE6B:destination-0xDE6B+4]=product.to_bytes(4,'little')
   assert memory[0xDE2F:0xDE39]==points and memory[0xDE6B:0xDE7B]==expected and ((r[H]*256+r[L])<<16)|(r[D]*256+r[E])==product
   a=(left>>8)^(right>>8);flags=sbc16_flags(0,magnitude>>16,int(bool(magnitude&65535))) if negative else logical_flags(a)
   bc=magnitude>>16 if negative else 0 if large else input_bc&0xFF00 if not small else input_bc
   ix=magnitude&65535 if large else 0x2468
   assert (r[A],r[F],r[B]*256+r[C],r[8]*256+r[9],r[SP])==(a,flags,bc,ix,0x8000)
   assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24];cases+=1;defects+=defect
 report=dict(passed=True,cases=cases,propagated_second_operand_8000_cases=defects,
  method='four_original_clip_products_complete_signed_multiply_all_second_operands_and_random_endpoints',
  wrapped_coordinate_differences_preserved=True,other_product_slots_preserved=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ClipProductsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

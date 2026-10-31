"""Две широковещательные группы заголовков граней, все исходные байты и полный образ памяти."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,SP
from CheckRowHighlight import make_context
from CheckWorldSignature import logical_flags
from Analyze import payload
QUADS=(0xF382,0xF434,0xF4C4,0xF0F0,0xF144,0xF266,0xF31A)
TRIANGLES=(0xF544,0xF548,0xF2B7,0xF2BB,0xF1BE,0xF1DB)


def main():
 _,_,banks=make_context();raw=payload(6);m=bytearray(65536);m[0x4000:0x8000]=bytes(banks[5]);m[0x8000:0xC000]=bytes(banks[2]);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=bytes([255,63]);s=Simulator(m);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0
 assert all(raw[a-0xC000]&15==4 for a in QUADS) and all(raw[a-0xC000]&15==3 for a in TRIANGLES)
 for first in range(256):
  for second in range(256):
   # Разные прежние заголовки выявляют широковещательную замену, индивидуальный XOR каждой записи дал бы другой результат.
   for i,a in enumerate(QUADS+TRIANGLES):m[a]=(first*31+second*17+i*29)&255
   m[0xF0F0]=first;m[0xF2B7]=second;expected=bytearray(m)
   for a in QUADS:expected[a]=first^0x60
   for a in TRIANGLES:expected[a]=second^0x60
   s.registers[:]=initial;r=s.registers;r[26]=(first+second)&1;s.run(start=0x6364,stop=0x3FFF)
   assert (r[A],r[F],r[SP],r[26])==(second^0x60,logical_flags(second^0x60),0x8000,(first+second)&1)
   assert r[2:12]==initial[2:12] and r[14]==initial[14] and r[16:24]==initial[16:24] and m==expected;cases+=1
 report=dict(passed=True,cases=cases,all_seed_byte_pairs=True,distinct_headers_check_broadcast_not_individual_xor=True,full_memory_compared=True,registers_flags_and_iff_checked=True,quad_headers=QUADS,triangle_headers=TRIANGLES,original_pattern_pairs=raw[0x1100:0x1110].hex(),irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewFaceFillVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

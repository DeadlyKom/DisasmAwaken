"""Четыре произведения после D0C3, реальные границы вместо исходных 0 и 255."""
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
 _,source,banks=make_context();memory=bytearray(65536)
 memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0
 sim.run(start=0xC49B,stop=0x3FFF)
 rng=random.Random(0xD0C3D8E2);cases=defects=0
 for profile in range(256):
  min_x,min_y,max_x,max_y=profile,(profile*37)&255,255-profile,(profile*53)&255
  # Настройка настоящим установщиком, в том числе неупорядоченных минимумов и максимумов.
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=max_y,max_x;r[D],r[E]=min_y,min_x
  sim.run(start=0xD0C3,stop=0x3FFF)
  for entry,destination,bound in ((0xD8E2,0xDE6B,min_y),(0xD901,0xDE6F,max_y),(0xD920,0xDE73,min_x),(0xD93F,0xDE77,max_x)):
   # Проверка случайных конечных точек и граничных разностей, включая второе слово 8000.
   fixtures=[tuple(rng.randrange(65536) for _ in range(4)) for _ in range(32)]
   for delta in (0,1,255,256,32767,32768,32769,65535):
    fixtures.append((delta,(bound+256)&65535,0,0) if entry in (0xD8E2,0xD901) else ((bound+delta)&65535,256,0,0))
   if profile==73:
    # Полный диапазон второго множителя при первом 256 в одном настроенном профиле.
    fixtures.extend((value,(bound+256)&65535,0,0) if entry in (0xD8E2,0xD901) else ((bound+value)&65535,256,0,0) for value in range(65536))
   for x1,y1,x2,y2 in fixtures:
    if entry in (0xD8E2,0xD901):left=(y1-bound)&65535;right=(x1-x2)&65535;input_bc=bound
    else:left=(y1-y2)&65535;right=(x1-bound)&65535;input_bc=y2
    mx,my=abs(signed(left)),abs(signed(right));large=mx>=256 and my>=256;small=mx<256 and my<256
    defect=large and right==32768;magnitude=mx*256 if defect else mx*my;negative=bool((left^right)&32768)
    product=(-magnitude if negative else magnitude)&0xFFFFFFFF
    points=x1.to_bytes(2,'little')+y1.to_bytes(2,'little')+bytes([0xA7])+x2.to_bytes(2,'little')+y2.to_bytes(2,'little')+bytes([0x5A])
    memory[0xDE2F:0xDE39]=points;memory[0xDE6B:0xDE7B]=bytes([0xA7])*16
    sim.registers[:]=initial;r=sim.registers;sim.run(start=entry,stop=0x3FFF)
    expected=bytearray([0xA7]*16);expected[destination-0xDE6B:destination-0xDE6B+4]=product.to_bytes(4,'little')
    assert memory[0xDE2F:0xDE39]==points and memory[0xDE6B:0xDE7B]==expected
    assert ((r[H]*256+r[L])<<16)|(r[D]*256+r[E])==product
    a=(left>>8)^(right>>8);flags=sbc16_flags(0,magnitude>>16,int(bool(magnitude&65535))) if negative else logical_flags(a)
    bc=magnitude>>16 if negative else 0 if large else input_bc&0xFF00 if not small else input_bc
    ix=magnitude&65535 if large else 0x2468
    assert (r[A],r[F],r[B]*256+r[C],r[8]*256+r[9],r[SP])==(a,flags,bc,ix,0x8000)
    assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
    cases+=1;defects+=defect
 report=dict(passed=True,cases=cases,setup_profiles=256,all_byte_values_each_boundary=True,
  all_second_operand_words_in_one_profile=True,propagated_second_operand_8000_cases=defects,
  unordered_bounds_preserved=True,other_product_slots_preserved=True,
  method='original_D0C3_then_four_original_products_complete_signed_multiply_exact_registers_flags_memory',
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ConfiguredClipProductsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

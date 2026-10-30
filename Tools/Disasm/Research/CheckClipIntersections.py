"""Четыре исходных пересечения с полным и кэшированным входом, точное старое деление и выходная страница."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckSignedMultiply import signed,sbc16_flags
from CheckSignedDivision import expected as divide_expected
from CheckWorldSignature import logical_flags


def inc_flags(value,carry):
 result=(value+1)&255
 return (result&0xA8)|(0x40 if result==0 else 0)|(0x10 if result&15==0 else 0)|(4 if result==128 else 0)|carry


def main(configured=False):
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 rng=random.Random(0xD95E);cases=full=wrapped_y=defects=0;offsets=(0,2,126,127,254,255)
 if configured:
  memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0
  sim.run(start=0xC49B,stop=0x3FFF)
 for profile in range(256 if configured else 1):
  min_x,min_y,max_x,max_y=(profile,(profile*37)&255,255-profile,(profile*53)&255) if configured else (0,0,255,255)
  y_stop=192
  if configured:
   # Настройка границ и преобразователей исходным D0C3, без ручной подмены его записей.
   sim.registers[:]=initial;r=sim.registers;r[H],r[L]=max_y,max_x;r[D],r[E]=min_y,min_x
   sim.run(start=0xD0C3,stop=0x3FFF)
  for kind,entry,cached,destination in ((0,0xD95E,0xD961,0xDE6B),(1,0xD9A9,0xD9AC,0xDE6F),(2,0xD9F4,0xD9F7,0xDE73),(3,0xDA52,0xDA55,0xDE77)):
   boundary=(min_y,max_y,min_x,max_x)[kind]
   fixtures=[tuple(rng.randrange(-600,601)&65535 for _ in range(4)) for _ in range(64 if configured else 8192)]
   fixtures += [(0x8000 if kind<3 else 0x80FF,511 if kind==1 else 256,0 if kind<2 else 1000,1000 if kind<2 else 0),
    (0,0,1,1),(0,0,65535,65535),(1,191,255,192),(255,256,0,257),(256,511,255,510)]
   # Проверка пересечений в обеих формах входа, в том числе оборачивания выходного байтового курсора.
   for index,(x1,y1,x2,y2) in enumerate(fixtures):
    if kind<2:left=(y1-boundary)&65535;right=(x1-x2)&65535;product_bc=boundary;denword=(y2-y1)&65535;other=y1;origin=x1
    else:left=(y1-y2)&65535;right=(x1-boundary)&65535;product_bc=y2;denword=(x2-x1)&65535;other=x1;origin=y1
    if not denword:continue
    mx,my=abs(signed(left)),abs(signed(right));large=mx>=256 and my>=256;small=mx<256 and my<256;defect=large and right==32768
    magnitude=mx*256 if defect else mx*my;negative=bool((left^right)&32768);product=(-magnitude if negative else magnitude)&0xFFFFFFFF
    number=product if product<0x80000000 else product-0x100000000;denominator=signed(denword);unsigned=(~product)&0xFFFFFFFF if number<0 else product
    if unsigned>=abs(denominator)*65536:continue
    mul_flags=sbc16_flags(0,magnitude>>16,int(bool(magnitude&65535))) if negative else logical_flags((left>>8)^(right>>8))
    mul_bc=magnitude>>16 if negative else 0 if large else product_bc&0xFF00 if not small else product_bc
    den_flags=sbc16_flags((y2 if kind<2 else x2),(y1 if kind<2 else x1),0)
    for use_cache in (False,True):
     cursor=offsets[index%len(offsets)];initial_f=0x5C|(index&1);pre_f=initial_f if use_cache else mul_flags
     bc_before=0x36C9 if use_cache else mul_bc;ix_before=0x2468 if use_cache or not large else magnitude&65535
     quotient,_,alt_flags,bc,_,_=divide_expected(number,denominator,den_flags&1,pre_f&1,bc_before)
     coordinate=(quotient+origin)&65535;low=coordinate&255;negative_coordinate=bool(coordinate&32768)
     if kind<2:
      projected=min_x if negative_coordinate else max_x if coordinate>>8 else low;pair=(projected,boundary);carry=0
      de=origin if negative_coordinate else (origin&0xFF00)|projected
     else:
      normal=not negative_coordinate and low<y_stop;projected=low if normal else min_y if negative_coordinate else max_y;pair=(boundary,projected);carry=int(normal)
      de=(projected<<8)|(origin&255) if normal else origin
      wrapped_y+=normal and coordinate>=256
     points=x1.to_bytes(2,'little')+y1.to_bytes(2,'little')+bytes([0xA7])+x2.to_bytes(2,'little')+y2.to_bytes(2,'little')+bytes([0x5A])
     memory[0xDE2F:0xDE39]=points;memory[0xDE3B]=cursor;memory[0xDE6B:0xDE7B]=bytes([0xA7])*16
     if use_cache:memory[destination:destination+4]=product.to_bytes(4,'little')
     memory[0xF8FF:0xFA01]=bytes([0xA7])*258;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[F]=initial_f
     sim.run(start=cached if use_cache else entry,stop=0x3FFF)
     expected=bytearray([0xA7]*256);expected[cursor]=pair[0];expected[(cursor+1)&255]=pair[1];next_cursor=(cursor+2)&255
     assert memory[0xF900:0xFA00]==expected and memory[0xF8FF]==memory[0xFA00]==0xA7,(profile,kind,index,use_cache,pair,hex(coordinate),[(k,memory[0xF900+k],expected[k]) for k in range(256) if memory[0xF900+k]!=expected[k]])
     assert memory[0xDE2F:0xDE39]==points and memory[0xDE3B]==next_cursor and memory[destination:destination+4]==product.to_bytes(4,'little')
     assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[SP])==(0xF900+next_cursor,de,bc,next_cursor,inc_flags((cursor+1)&255,carry),0x8000),(kind,index,use_cache,pair,hex(coordinate),list(r))
     k=int(number<0)+int(denominator<0);assert r[8]*256+r[9]==(ix_before&0xFF00)|((k-1)&255)
     assert r[16:18]==[quotient&255,alt_flags] and r[18:24]==initial[18:24] and r[10:12]==initial[10:12]
     cases+=1;full+=not use_cache;defects+=defect
 report=dict(passed=True,cases=cases,full_entry_cases=full,cached_entry_cases=cases-full,
  positive_high_y_low_byte_wrap_cases=wrapped_y,propagated_multiply_exception_cases=defects,
  configured_by_original_D0C3=configured,setup_profiles=256 if configured else 0,
  method='original_four_clip_intersections_actual_products_division_projection_and_wrapping_output_cursor',
  quotient_contract_precondition_checked=True,zero_divisors_excluded=True,output_cursor_values=list(offsets),
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/('Tools/Disasm/Reports/ConfiguredClipIntersectionsVerification.json' if configured else 'Tools/Disasm/Reports/ClipIntersectionsVerification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main('--configured' in sys.argv)

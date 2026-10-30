"""Исходный самомодифицируемый рисователь, независимая попиксельная модель и исключённый последний конец."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address


def points(first,second):
 if first==second:return []
 (x,y),(end_x,end_y)=first,second
 if end_y<y:(x,y),(end_x,end_y)=(end_x,end_y),(x,y)
 dx=abs(end_x-x);dy=end_y-y;step=-1 if end_x<x else 1;major=max(dx,dy);minor=min(dx,dy);error=major//2;result=[]
 for _ in range(major):
  result.append((x,y));error-=minor
  if dx>=dy:
   x+=step
   if error<0:y+=1;error+=major
  else:
   y+=1
   if error<0:x+=step;error+=major
 assert (x,y)==(end_x,end_y)
 return result


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 # Компенсация исходных отступов +8,+16 через байтовое оборачивание входа построителя, чтобы таблицы начинались с экранного 0,0.
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=240;sim.registers[E]=248;sim.run(start=0xC49B,stop=0x3FFF)
 baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912));rng=random.Random(0xD2EE)
 fixtures=[((rng.randrange(256),rng.randrange(192)),(rng.randrange(256),rng.randrange(192))) for _ in range(8192)]
 # Проверка горизонталей, вертикалей, обеих диагональных направленностей и границ восьмистрочных блоков.
 for value in range(256):
  for row in (0,7,8,63,64,127,128,191):fixtures.extend((((0,row),(value,row)),((value,row),(0,row)),((value,0),(value,row)),((value,row),(value,0))))
 for delta in range(192):fixtures.extend((((0,0),(delta,delta)),((255,0),(255-delta,delta)),((0,delta),(delta,0)),((255,delta),(255-delta,0))))
 counts=collections.Counter();steps=0
 for mode,opcode,jump,offset in (('clear',0xA1,0x30,0x28),('set',0xB1,0x38,0x20),('xor',0xA9,0x38,0x20)):
  for first,second in fixtures:
   expected=bytearray(baseline);pixel_points=points(first,second)
   for x,y in pixel_points:
    address=bitmap_address(y,x//8)-0x4000;mask=128>>(x&7)
    if mode=='clear':expected[address]&=255^mask
    elif mode=='set':expected[address]|=mask
    else:expected[address]^=mask
   memory[0x4000:0x5B00]=baseline;memory[0xDE2B:0xDE2F]=bytes([*first,*second]);memory[0xDE3C:0xDE3E]=bytes([opcode,jump]);memory[0xD306]=offset;sim.registers[:]=initial;r=sim.registers
   before_code=bytes(memory[0xD2EE:0xD418]);sim.run(start=0xD2EE,stop=0x3FFF)
   assert memory[0x4000:0x5B00]==expected,(mode,first,second)
   assert memory[0xDE2B:0xDE2F]==bytes([*first,*second]) and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
   if first==second:
    assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F])==(0,second[1]*256+second[0],0x36C9,0x5A,0x42)
    assert memory[0xD2EE:0xD418]==before_code and r[16:18]==initial[16:18];counts[mode+'_equal']+=1
   else:
    start,end=(second,first) if second[1]<first[1] else (first,second);dx=abs(end[0]-start[0]);dy=end[1]-start[1];major=max(dx,dy);minor=min(dx,dy)
    mask=128>>(end[0]&7);mask=mask^255 if mode=='clear' else mask
    assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[16])==(bitmap_address(end[1],end[0]//8),major*256+minor,mask,major//2),(mode,first,second,list(r))
    right=end[0]>start[0];x_major=dx>=dy;site=(0xD3B4 if right else 0xD338) if x_major else (0xD3F3 if right else 0xD377);branch=site+(3 if x_major else 0x1A)
    assert memory[site]==opcode and memory[branch]==jump
    allowed={site-0xD2EE,branch-0xD2EE};assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(before_code,memory[0xD2EE:0xD418])))
    counts[mode+('_right' if right else '_left')+('_x_major' if x_major else '_y_major')]+=1
   steps+=len(pixel_points)
 report=dict(passed=True,cases=sum(counts.values()),pixel_operations=steps,paths=dict(counts),method='original_three_self_modified_line_modes_against_independent_pixel_Bresenham_full_screen_and_endpoint_registers',
  coordinate_domain=dict(x=[0,255],y=[0,191]),screen_origin=[0,0],table_builder_input_DE=0xF0F8,synthetic_alignment_fixture=True,last_endpoint_excluded=True,equal_points_draw_nothing=True,
  temporary_opcodes_match_actual_caller=True,code_writes_limited_to_selected_kernel=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapLineVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

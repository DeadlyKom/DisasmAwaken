"""Исходный рисователь DE1C, независимый bitmap и реальная подготовка таблиц 6322."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckRowHighlight import make_context
from PreviewEdgeRasterOracle import address,points,raster,registers
PATCHES=((0xDE66,0xDE69),(0xDEA5,0xDEBF),(0xDEE2,0xDEE5),(0xDF21,0xDF3B))
MODES={'xor':(0xA9,0x38,0xB0),'or':(0xB1,0x38,0xB0),'and':(0xA1,0x30,0xB8)}


def main():
 _,_,banks=make_context();raw=payload(6);m=Memory([0]*65536);m[0x4000:0x8000]=banks[5];m[0x8000:0xC000]=banks[2];m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 # Подготовка настоящим общим входом, байтовое оборачивание начала даёт экранные row0=col0=0.
 s.registers[:]=initial;s.registers[D]=240;s.registers[E]=248;s.run(start=0x6322,stop=0x3FFF)
 assert list(raw[0xDB0:0xDB8])==[128>>i for i in range(8)] and list(raw[0xDB8:0xDC0])==[255^(128>>i) for i in range(8)]
 buffers=(bytes(6144),bytes([255]*6144),bytes((i*37+11)&255 for i in range(6144)),bytes((85,170))*3072)
 cases=0;branches=collections.Counter();origin=(0,0)
 def check(first,second,mode):
  nonlocal cases
  source=buffers[cases%4];expected=raster(source,first,second,mode,origin);operator,branch,offset=MODES[mode]
  m.recording=False;m[0x4000:0x5800]=source;m[0xC24B:0xC24F]=[first[1],first[0],second[1],second[0]];m[0xC26F:0xC271]=[operator,branch];m[0xDE34]=offset
  for op,jump in PATCHES:m[op]=0;m[jump]=0x38
  s.registers[:]=initial;r=s.registers;m.recording=True;m.writes=[];s.run(start=0xDE1C,stop=0x3FFF)
  assert bytes(m[0x4000:0x5800])==expected,(first,second,mode)
  assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
  assert m[0x7FFE:0x8000]==[255,63]
  if first==second:
   assert not m.writes and (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F])==(0,second[0]*256+second[1],0x36C9,0x5A,0x42)
   assert r[16:18]==initial[16:18];branches['degenerate']+=1
  else:
   start,end=(second,first) if second[0]<first[0] else (first,second);dy=end[0]-start[0];dx=abs(end[1]-start[1]);right=end[1]>start[1];steep=dy>dx;index=2*right+steep;op,jump=PATCHES[index]
   end_pointer=address(end[0]+origin[0],end[1]+origin[1])
   assert (r[H]*256+r[L],r[D],r[E],r[B])==(end_pointer,max(dx,dy),min(dx,dy),0),(first,second,mode,r[:8])
   mask=128>>(end[1]&7);assert r[C]==(mask if mode!='and' else 255^mask)
   assert [(p,v) for p,v in m.writes if p>=0xC000]==[(op,operator),(jump,branch)]
   plotted=points(first,second);allowed={address(row+origin[0],column+origin[1]) for row,column in plotted}
   if not steep:
    direction=1 if right else -1;allowed.update(address(row+origin[0],column+direction+origin[1]) for row,column in plotted)
   assert all(0x4000<=p<0x5800 and p in allowed or p in (op,jump) for p,v in m.writes)
   branches[('right' if right else 'left')+('_steep' if steep else '_shallow')]+=1
  context=registers(first,second,mode,expected,origin)
  assert tuple(r[:2])==context['af'] and tuple(r[16:18])==context['alt_af'],(first,second,mode,origin,r[:2],r[16:18],context)
  cases+=1
 # Проверка каждой пары длин осей до 63 включительно в обоих направлениях и всех трёх режимах.
 for dy in range(64):
  for dx in range(64):
   for reverse in (False,True):
    for mode in MODES:check((0,255 if reverse else 0),(dy,255-dx if reverse else dx),mode)
 # Проверка начала на каждой экранной строке, включая границы 8,64,128 и разные пиксельные биты.
 for row in range(192):
  for dy in (0,min(7,191-row)):
   for mode in MODES:check((row,121),(row+dy,135),mode);check((row,135),(row+dy,121),mode)
 rng=random.Random(0xDE1C)
 for _ in range(2048):check((rng.randrange(192),rng.randrange(256)),(rng.randrange(192),rng.randrange(256)),rng.choice(tuple(MODES)))
 # Проверка смещённых начал, включая округление горизонтального начала вниз до байтовой колонки.
 for row_origin,column_origin in ((19,25),(57,40),(96,88)):
  m.recording=False;s.registers[:]=initial;s.registers[D]=(row_origin-16)&255;s.registers[E]=(column_origin-8)&255;s.run(start=0x6322,stop=0x3FFF);origin=(row_origin,column_origin//8*8)
  for _ in range(512):check((rng.randrange(192-row_origin),rng.randrange(256-origin[1])),(rng.randrange(192-row_origin),rng.randrange(256-origin[1])),rng.choice(tuple(MODES)))
 report=dict(passed=True,cases=cases,branches=dict(branches),independent_pixel_set_and_full_6144_byte_bitmap=True,real_sprite_line_table_setup=True,original_three_operator_and_branch_pairs=True,endpoint_excluded=True,all_64_by_64_slopes_both_directions=True,all_screen_start_rows=True,final_pointer_mask_major_minor_and_preserved_registers_checked=True,exact_two_self_modified_bytes_checked=True,screen_write_bounds_checked=True,exact_main_and_alternate_af_checked=True,shifted_and_unaligned_origins_checked=True,onscreen_table_profile=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewEdgeRasterVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

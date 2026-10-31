"""Подсчёт и печать исходных описаний D3D против независимой пагинации и полного bitmap."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from CheckRowHighlight import make_context
from CheckTextPagination import reference
from CheckInsetFrame import bitmap_address
from Analyze import payload


def selected(m,selector,index):
 p=0xFBD8 if selector==1 else 0xF581
 for _ in range(index+1):p=m.index(10,p)+1
 return p


def paint_positions(m,positions,width,height,origin):
 screen=bytearray(m[0x4000:0x5B00]);glyphs=0;widths=m[0x8900:0x8A00]
 for code,x,y in positions:
  if y>=height or x+widths[code]>255 or x+widths[code]>=width:continue
  px,py=origin[0]+x,origin[1]+y
  if px>255 or py>184:continue
  for line,bits in enumerate(m[0x8A00+8*code:0x8A08+8*code]):
   for bit in range(8):
    if px+bit<256 and bits&(128>>bit):screen[bitmap_address(py+line,(px+bit)//8)-0x4000]^=128>>((px+bit)&7)
  glyphs+=1
 return screen,glyphs


def main():
 _,_,banks=make_context();raw=payload(6);template=bytearray(65536);template[0x4000:0x8000]=bytes(banks[5]);template[0x8000:0xC000]=bytes(banks[2]);template[0xC000:0xC000+len(raw)]=raw
 template[0x4000:0x5B00]=bytes((i*73+(i>>8)*19+17)&255 for i in range(0x1B00));initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts=prints=glyphs=0
 def execute(entry,selector,index,wrapped,width,height,scroll=0,origin=(5,3)):
  nonlocal counts,prints,glyphs
  m=bytearray(template);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[A]=selector;r[H]=scroll>>8;r[L]=scroll&255;row=(index-3)&255 if wrapped else index;base=3 if wrapped else 0;m[0xE146]=row;m[0xE148]=base;m[0x6320:0x6322]=bytes([127,250]);m[0xAEAB]=height;m[0xAEB3]=width;m[0xAEBB]=origin[0];m[0xAEBF]=0;m[0xAEC7]=origin[1];m[0xAECB]=0;m[0xBD26]=0;m[0x7FFE:0x8000]=bytes([255,63]);start=selected(m,selector,index);positions=[];description_image=bytes(m[0xC000:])
  args=(0xA82D if entry==0xE124 else 0xA843,list(m[start:]),list(m[0x8900:0x8A00]),0x3600|row if entry==0xE124 else 0x0800,width,height,0 if entry==0xE124 else scroll&255)
  expected=reference(*args,initial_d=scroll>>8,positions=positions,origin=origin);screen=bytearray(m[0x4000:0x5B00]);widths=m[0x8900:0x8A00]
  screen,painted=paint_positions(m,positions,width,height,origin);glyphs+=painted
  s.run(start=entry,stop=0x3FFF);offset,x,y,a,f,bc,d,e,_=expected
  actual=(r[H]*256+r[L],m[0x6320],m[0x6321],r[A],r[F],r[2]*256+r[3],r[D],r[E]);assert actual==(start+offset,x,y,a,f,bc,d,e),(hex(entry),selector,index,wrapped,width,height,scroll,actual,expected)
  assert m[0x4000:0x5B00]==screen and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
  assert bytes(m[0xC000:])==description_image
  if entry==0xE124:counts+=1
  else:prints+=1
 for selector in (0,1,2,255):
  for index in range(4 if selector==1 else 7):
   for wrapped in (False,True):
    for width,height in ((96,0),(96,13),(96,24),(168,80),(224,160)):
     execute(0xE124,selector,index,wrapped,width,height)
     for scroll in (0,1,2,15,255,256,257,0xA5FF):execute(0xE154,selector,index,wrapped,width,height,scroll)
 for selector in range(256):execute(0xE124,selector,selector%(4 if selector==1 else 7),False,168,80)
 for selector,index in ((0,0),(1,3)):
  for scroll in range(256):execute(0xE154,selector,index,False,168,80,scroll,origin=(248,184))
 report=dict(passed=True,count_cases=counts,print_cases=prints,independent_glyphs=glyphs,all_selectors_checked=True,all_skip_bytes_checked=True,wrapped_index_sum=True,scroll_high_byte_ignored_for_skip=True,real_skip_count_print_and_glyph_callees=True,whole_bitmap_and_attributes_compared=True,original_descriptions_preserved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewDescriptionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

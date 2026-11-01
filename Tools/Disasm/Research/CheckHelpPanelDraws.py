"""Два рисователя справки, настоящая рамка/IM2 и независимая раскладка HELP."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckHelpLineIndex import expected as index_rows
from CheckJustifiedText import reference as justified
from CheckTextStream import reference as stream
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();raw=payload(8);base[7][0x1B00:0x1B00+len(raw)]=list(raw);counts=collections.Counter()
 def run(kind,selector,top,rect,page,flags):
  f=Fixture(base,page=page);m=f.memory;s=f.sim;r=s.registers;initial=f.initial;key=22 if kind=='contents' else 23;address=0x6A5B if key==22 else 0x69A8
  record=0xF0FD+16*key;x,y,w,h=rect;put(m,record,(x,y,w,h,flags,m[record+5]));put(m,0x6A5C,(22,0));put(m,0x69A9,(23,0));m[0x9B16]=1
  put(m,0x6A15,top.to_bytes(2,'little'));put(m,0x699D,top.to_bytes(2,'little'));m.banks[7][0x1B01]=selector
  widths=list(m[0x8900:0x8A00]);width,height=8*w-4,8*h-11;calls=[];seen=[];font_prefix=bytes((0x68,0x48,0x26));put(m,0xAED5,font_prefix)
  if key==23:
   text=list(raw[0x8E2:])+[10]*1024;m.banks[7][0x23E2:0x23E2+len(text)]=text
   pointers,_,_,_=index_rows(text,selector,width,height,widths,initial[2]*256+initial[3]);n=len(pointers);assert n<1024
   pointer=pointers[top] if top<n else 0
   if pointer:
    expected=justified(0xADCD,text[pointer-0xE3E2:],widths,0,8,width,height,0x0800,0xDB,0x7C,origin=(8*x+3,8*y+3))
   else:expected=None
  else:
   text=list(raw[0x87C:0x8E2])+[10]*1024;offset=0
   for _ in range((top&255)+1):offset=text.index(13,offset)+1
   # Геометрия содержимого берётся из полного прямоугольника, реальный DrawCaptionItem проверяет её отдельно.
   expected=stream(text[offset:],widths,0,8,width,height,0,[m[a] for a in (0xBD73,0xBD7E,0xBD89,0xBD94,0xBD9F)],(8*x+3,8*y+3),initial[2])
  def observe(f,pc):
   if m.o7ffd&7==7 and pc in (0xDB00,0xDB42,0xDB5B):seen.append(pc)
   if m.o7ffd&7==7 and pc==0xAE8D and seen and seen[-1] in (0xDB42,0xDB5B):calls.append(r[0])
  result=f.run(address,observe);assert result['wakes']==1 and m.o7ffd==page and m[0x6306]==page
  assert r[8:12]==initial[8:12] if key==22 else r[10:12]==initial[10:12]
  assert r[18:24]==initial[18:24] and r[SP]==0x8000
  pageflags=(page&0xA8)|(4 if page.bit_count()%2==0 else 0)
  if key==23:
   assert seen==[0xDB00,0xDB42] and m[0x6995]+256*m[0x6996]==n and m[0xBD26]==1
   cache=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes(2048-2*n);assert bytes(m.banks[7][0x1B7C:0x237C])==cache
   if expected:
    consumed,cx,cy,a,af,bc,d,e,glyphs=expected;ptr=pointer+consumed
    assert tuple(r[:8])==(page,pageflags,bc>>8,bc&255,d,e,ptr>>8,ptr&255) and calls==glyphs and (m[0x6320],m[0x6321])==(cx,cy),(selector,top,rect,tuple(r[:8]),(page,pageflags,bc>>8,bc&255,d,e,ptr>>8,ptr&255),(m[0x6320],m[0x6321]),(cx,cy),calls[:8],glyphs[:8],tuple(m[a] for a in (0xAEBB,0xAEBF,0xAEC7,0xAECB,0xAEB3,0xAEAB)))
   else:assert tuple(r[:8])==(page,pageflags,8,0,0xDB,0x7C,0,0) and not calls
   assert r[8]*256+r[9]==0xDB7C+2*n;counts['help_body_draws']+=1
  else:
   consumed,cx,cy,a,af,glyphs=expected;delta=(cy-8)&255;rows=(delta>>3)+1;rowflags=(rows&0x28)|(16 if (delta>>3)&15==15 else 0)|((delta>>2)&1);ptr=0xE37C+offset+consumed
   assert tuple(r[:8])==(rows,rowflags,initial[2],initial[3],top>>8,top&255,ptr>>8,ptr&255),(rect,top,r[:8],expected)
   assert r[16:18]==[page,pageflags] and m[0x6A4D]==rows and m[0x6A52]==255 and m[0xBD26]==0
   assert (m[0x6320],m[0x6321])==(cx,8) and calls==glyphs and seen==[0xDB5B];counts['help_contents_draws']+=1
  counts['real_caption_im2_wakeups']+=result['wakes']
 # Проверка исходных разделов и первых двух позиций прокрутки при разных рамках и обоих экранных битах.
 for page in (0x10,0x18):
  for flags in (6,7):
   for rect in ((1,1,12,6),(1,1,24,12),(0,0,24,24)):
    for selector in range(9):
     for top in (0,1):run('body',selector,top,rect,page,flags)
    for top in range(8):run('contents',0,top,rect,page,flags)
 # Проверка временного RET в первом байте обоих рисователей, параметры и память не читаются.
 for address in (0x69A8,0x6A5B):
  f=Fixture(base);m=f.memory;s=f.sim;m[address]=0xC9;before=[bytes(b) for b in m.banks]
  for flags in range(256):
   s.registers[:]=f.initial;r=s.registers;r[1]=flags;s.run(start=address,stop=0x3FFF)
   assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
   assert [bytes(b) for b in m.banks]==before;counts['disabled_draw_returns']+=1
 report=dict(passed=True,cases_by_path=dict(counts),all_original_help_records_and_titles=True,actual_caption_and_help_and_bank_helpers=True,
  independent_layout_and_exact_registers=True,entire_index_cache_checked=True,irq_only_at_caption_halt=True,music_disabled=True,
  independent_whole_bitmap_oracle=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpPanelDrawsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

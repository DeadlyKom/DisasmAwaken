"""Документация оснащения, сухой счётчик, байтовый пропуск, рисование и действие."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckTextPagination import reference
from CheckShipModelActions import remove
from CheckPreviewDescriptions import paint_positions
from CheckScrollBodyClear import rectangle
from CheckScreenUpdate import pointer_image
from skoolkit.simutils import PC,SP


def main():
 station,_,base=make_context();counts=collections.Counter();data=list(base[0][0x11BA:])+[10]*1024;widths=list(base[2][0x900:0xA00])
 def selected(text,selector):
  offset=0
  for _ in range(selector+1):offset=text.index(10,offset)+1
  return offset
 def prepare(width=92,height=29,page=0x10):
  f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;put(m,0x6AB7,(39,0));record=0xF0FD+39*16;put(m,record,(0,0,12,5,7,m[record+5]));put(m,0x6AA4,(1,0));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(0xB6,0x6A,1,1))
  for a,v in ((0xAEB3,width),(0xAEAB,height),(0xAEBB,3),(0xAEBF,0),(0xAEC7,3),(0xAECB,0)):m[a]=v
  put(m,0xAED5,(0x68,0x48,0x26));return f
 def context(f,caption=False):
  r=f.sim.registers;assert r[8:12]==f.initial[8:12] and r[18:24]==f.initial[18:24] and (caption or r[16:18]==f.initial[16:18]) and r[SP]==0x8000
 def update(text,selector,width,height,synthetic=False):
  f=prepare(width,height);m=f.memory;s=f.sim;r=s.registers
  if synthetic:put(m,0xD1BA,text)
  m[0x6ACC]=selector;offset=selected(list(text),selector)
  expected=reference(0xA82D,list(text)[offset:],widths,f.initial[2]*256+f.initial[3],width,height,0)
  consumed,x,y,a,flags,bc,d,e,calls=expected;ptr=0xD1BA+offset+consumed;screen=bytes(m[0x4000:0x5B00]);s.run(start=0x6AC6,stop=0x3FFF)
  assert tuple(r[:8])==(a,flags,bc>>8,bc&255,d,e,ptr>>8,ptr&255) and m[0x6AE0]+256*m[0x6AE1]==0xD1BA+offset
  assert m[0x6A9C]+256*m[0x6A9D]==d*256+e and m[0xBD26]==1 and (m[0x6320],m[0x6321])==(x,y) and bytes(m[0x4000:0x5B00])==screen;context(f)
  counts['synthetic_all_selector_update' if synthetic else 'original_text_update']+=1
 # Проверка первых 24 исходных LF-записей и раннего выхода по высоте, число записей всего блока не предполагается.
 for selector in range(24):
  for width in (64,92,188):
   for height in (8,13,24,192):update(data,selector,width,height)
 # Проверка всего байтового селектора на подготовленном запасе LF, без выдумывания отсутствующих исходных записей.
 for selector in range(256):update(list(bytes([10])*(selector+1)+b'ONE TWO THREE FOUR\n'+bytes([10])*1024),selector,92,192,True)
 # Проверка полного HL пропуска, только E участвует в числе сухих проходов.
 for selector in (0,7,17,23):
  for skip in (0,1,2,255,256,257,65535):
   f=prepare();m=f.memory;r=f.sim.registers;offset=selected(data,selector);put(m,0x6AE0,(0xD1BA+offset).to_bytes(2,'little'));r[6],r[7]=skip>>8,skip&255;positions=[]
   expected=reference(0xA843,data[offset:],widths,0x0800,92,29,skip&255,skip>>8,positions,(3,3));consumed,x,y,a,flags,bc,d,e,calls=expected;ptr=0xD1BA+offset+consumed
   flat=bytearray(m[0:65536]);screen,_=paint_positions(flat,positions,92,29,(3,3));f.run(0x6ADE)
   assert tuple(r[:8])==(a,flags,bc>>8,bc&255,d,e,ptr>>8,ptr&255) and bytes(m[0x4000:0x5B00])==bytes(screen) and (m[0x6320],m[0x6321])==(x,y);context(f);counts['print_full_skip_words']+=1
 # Проверка рамки, выбранного описания и общего контракта прямого рисователя.
 for page in (0x10,0x18):
  for selector in (0,7,17,23):
   for top in (0,1,257):
    f=prepare(page=page);m=f.memory;m[0x6ACC]=selector;put(m,0x6AA4,top.to_bytes(2,'little'));f.run(0x6AB6)
    assert f.wakes==1 and m.o7ffd==page and m[0xBD26]==1 and m[0x6AE0]+256*m[0x6AE1]==0xD1BA+selected(data,selector)
    assert m[0x6AA4]+256*m[0x6AA5]==top;context(f,True);counts['real_caption_draws']+=1;counts['caption_im2_wakes']+=1
 # Проверка точного адреса рисователя, алиас с тем же индексом не считается присутствием.
 for matched in (False,True):
  for disabled in (False,True):
   f=prepare();m=f.memory;r=f.sim.registers;put(m,0x5F00,(0x21,39,0,0xC9));put(m,0xF3DE,bytes((0xB6,0x6A,1,1)) if matched else bytes((0,0x5F,1,1)));m[0x6ACC]=0
   if disabled:m[0x6AB6]=0xC9
   f.run(0x6AAF);assert f.wakes==int(matched and not disabled)
   if not matched or disabled:assert r[4:6]==[0x6A,0xB6]
   counts['conditional_exact_draw_pointer']+=1;counts['conditional_im2_wakes']+=f.wakes
 # Проверка всех селекторов действия на закрытии либо раннем возврате.
 for selector in range(256):
  f=prepare();m=f.memory;r=f.sim.registers;r[0]=selector;r[6:8]=[0x6A,0xB6];r[4:6]=[0,39];record=0xF0FD+39*16;r[8:10]=[record>>8,record&255];m[record+4]=6;m[0xCA20]=6;m[0x9E78]=0;put(m,0x6307,(50,3));m[0x9A82]=0xA7
  f.run(0x6A86)
  if selector&128:assert r[0]==selector and r[1]==(selector&0xA8)|1 and m[0xF3DE:0xF3E2]==[0xB6,0x6A,1,1]
  elif selector==1:assert r[:2]==[0,0x42] and m[0xF3DE:0xF3E2]==[0xB6,0x6A,1,1]
  else:assert m[0xF3DE:0xF3E0]==[1,1] and m[0x9A82]==0
  counts['all_action_selectors_close_or_return']+=1
 # Проверка настоящей прокрутки и независимого bitmap каждого принятого шага.
 for selector in (0,7,17,23):
  for direction in ('up','down'):
   for presses in (0,1,3):
    f=prepare();m=f.memory;s=f.sim;r=s.registers;record=0xF0FD+39*16;r[0]=0;r[6:8]=[0x6A,0xB6];r[4:6]=[0,39];r[8:10]=[record>>8,record&255];m[record+4]=6;m[0xCA20]=6;m[0x9E78]=0;m[0x9B16]=0;put(m,0x6307,(50,80));m[0x6ACC]=selector
    for a in (0x66EC,0x6585,0x66ED,0x658A):m[a]=0
    offset=selected(data,selector);limit=reference(0xA82D,data[offset:],widths,0x36C9,92,29,0)[6:8];limit=limit[0]*256+limit[1];index=1;poll=0;steps=0;frame=list(m[0x4000:0x6000]);expected_screen=None
    def observe(f,pc):
     nonlocal index,poll,steps,frame,expected_screen
     if pc==0xA20A:
      assert r[6]*256+r[7]==index;active=poll<presses;m[0x66ED]=int(active)
      if active:
       m[0x6308]=0 if direction=='up' else 191
       if direction=='up':index=max(0,index-1)
       elif index+2<limit:index+=1
      poll+=1
     if pc==0xA25C:
      cleared=bytearray(frame);rectangle(cleared,3,11,92,36);flat=bytearray(m[0:65536]);flat[0x4000:0x6000]=cleared;positions=[];reference(0xA843,data[offset:],widths,0x0800,92,29,index&255,index>>8,positions,(3,3));screen,_=paint_positions(flat,positions,92,29,(3,3));frame=list(cleared);frame[:6912]=screen;expected_screen=bytes(screen);steps+=1
     if pc==0xA268:assert bytes(m[0x4000:0x5B00])==expected_screen
    f.run(0x6A86,observe)
    assert m[0x6AA4]+256*m[0x6AA5]==index and r[6]*256+r[7]==index and r[:2]==[0,0x44] and m[0x6307:0x6309]==[50,80]
    assert bytes(m[0x4000:0x6000])==bytes(pointer_image(frame,station,50,80)) and poll==presses+1 and f.wakes==steps;counts['scroll_actions']+=1;counts['scroll_im2_wakes']+=steps
 # Проверка раннего Carry после настоящего переноса рисователя в конец списка.
 for selector in (0,1,2,127):
  f=prepare();m=f.memory;r=f.sim.registers;record=0xF0FD+39*16;r[0]=selector;r[6:8]=[0x6A,0xB6];r[4:6]=[0,39];r[8:10]=[record>>8,record&255];m[record+4]=6;m[0xCA20]=6;m[0x9E78]=0
  put(m,0x5F00,(0x21,63,0,0xC9));put(m,0xF3DE,(0xB6,0x6A,0,0x5F,1,1));f.run(0x6A86)
  assert r[0]==selector and r[1]&1 and m[0x6AA4:0x6AA6]==[1,0] and f.wakes==1;counts['repaint_then_carry_return']+=1;counts['repaint_im2_wakes']+=f.wakes
 # Проверка пустого наведения, его JP-обёртки и временного RET рисователя.
 for entry in (0x6A83,0x6AAE,0x6AB6):
  f=prepare();m=f.memory;s=f.sim
  if entry==0x6AB6:m[entry]=0xC9
  before=[bytes(b) for b in m.banks]
  for flags in range(256):
   s.registers[:]=f.initial;r=s.registers;r[1]=flags;s.run(start=entry,stop=0x3FFF)
   assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000 and [bytes(b) for b in m.banks]==before
   counts['noop_and_disabled_returns']+=1
 report=dict(passed=True,cases_by_path=dict(counts),original_records_checked=list(range(24)),all_256_selectors_on_synthetic_valid_text=True,
  physical_source_pointer_and_count_word_checked=True,full_skip_word_low_byte_semantics=True,independent_print_and_scroll_bitmap=True,
  real_im2_only_at_halts=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EquipmentInfoVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

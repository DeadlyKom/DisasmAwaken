"""Действия HELP, реальные списки/прокрутка/выбор раздела и IRQ только в HALT."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckShipModelActions import remove
from CheckWorldSignature import logical_flags
from CheckHelpLineIndex import expected as index_rows
from CheckJustifiedText import reference as justified
from CheckTextStream import reference as stream
from CheckScrollBodyClear import rectangle
from CheckPreviewDescriptions import paint_positions
from CheckScreenUpdate import pointer_image
from skoolkit.simutils import PC,SP


def main():
 station,_,base=make_context();raw=payload(8);base[7][0x1B00:0x1B00+len(raw)]=list(raw);counts=collections.Counter();width,height=92,29
 def prepare(kind,selector,page=0x10):
  f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;key=22 if kind=='contents' else 23;draw=0x6A5B if key==22 else 0x69A8
  put(m,0x6A5C,(22,0));put(m,0x69A9,(23,0))
  for k in (22,23):p=0xF0FD+16*k;put(m,p,(0,0,12,5,6,m[p+5]))
  r[0]=selector;r[6],r[7]=draw>>8,draw&255;r[4],r[5]=0,key;r[8],r[9]=(0xF0FD+16*key)>>8,(0xF0FD+16*key)&255
  m[0x9E78]=0;m[0xCA20]=6;m[0x9A82]=0xA7;m[0x9B16]=0;put(m,0x6307,(50,80));m[0x6548]=1
  for address,value in ((0xAEAB,height),(0xAEB3,width),(0xAEBB,3),(0xAEBF,0),(0xAEC7,3),(0xAECB,0),(0xBD26,1)):m[address]=value
  put(m,0xAED5,(0x68,0x48,0x26));put(m,0x6A15,(1,0));put(m,0x699D,(1,0));m[0x6A52]=255
  keys={0x5F00:63,0x69A8:23,0x6A5B:22};put(m,0x5F00,(0x21,63,0,0xC9));pointers=[0x5F00,0x6A5B,0x69A8] if key==23 else [0x5F00,0x69A8,0x6A5B]
  blob=bytearray(512);prefix=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes((1,1));blob[:len(prefix)]=prefix;put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,blob)
  for a in (0x66EC,0x6585,0x66ED,0x658A):m[a]=0
  return f,keys,blob,0x69E0 if key==22 else 0x697B
 # Проверка всех селекторов, раннего Carry и удаления двух связанных панелей с физическими хвостами.
 for kind in ('body','contents'):
  for selector in range(256):
   if selector==1 and kind=='contents':continue
   f,keys,blob,start=prepare(kind,selector);m=f.memory;r=f.sim.registers;put(m,0x6307,(50,3));before=[bytes(b) for b in m.banks];f.run(start)
   if selector&128:
    assert (r[0],r[1])==(selector,(selector&0xA8)|1) and bytes(m[0xF3DE:0xF5DE])==bytes(blob);counts['high_selector_return']+=1
   elif selector==1:
    assert (r[0],r[1])==(0,0x42) and bytes(m[0xF3DE:0xF5DE])==bytes(blob);counts['body_selector_one_noop']+=1
   else:
    wanted,flags,found=remove(blob,keys,[23,22] if kind=='body' else [22,23],0)
    assert bytes(m[0xF3DE:0xF5DE])==bytes(wanted) and m[0x9A82]==0 and r[0]==0 and r[1]==flags;counts['close_pair']+=1
 # Проверка охранного FF младшего байта ContentsTop, выбор не запускает HELP и рисователи.
 for high in range(256):
  f,keys,blob,start=prepare('contents',1);m=f.memory;r=f.sim.registers;put(m,0x6A15,(255,high));old=bytes(m.banks[7]);f.run(start)
  assert (r[0],r[1])==(0,0x50) and bytes(m.banks[7])==old and bytes(m[0xF3DE:0xF5DE])==bytes(blob) and f.wakes==0;counts['contents_top_ff_guard']+=1
 # Проверка всей байтовой суммы без применения недопустимого селектора к тексту, остановка перед SelectText.
 f,_,_,_=prepare('contents',1);m=f.memory;s=f.sim
 for top in range(255):
  for hover in range(256):
   m.out7ffd(0x10);m[0x6306]=0x10;put(m,0x6A15,(top,0xA5));m[0x6A52]=hover;put(m,0x699D,(5,0xA5));put(m,0x7FFE,(255,63));s.registers[:]=f.initial
   s.run(start=0x6A1E,stop=0xDB57);r=s.registers
   assert r[0]==(top+hover)&255 and m[0x699D:0x699F]==[0,0] and r[SP]==0x7FFC and m.o7ffd==0x17
   f.trace.writes.clear();counts['byte_choice_sum_stopped_before_select_text']+=1
 # Проверка полного принятого выбора раздела, две рамки и настоящий HELP без подмены вызовов.
 for page in (0x10,0x18):
  for top in (0,2):
   for hover in range(8-top):
    f,keys,blob,start=prepare('contents',1,page);m=f.memory;r=f.sim.registers;put(m,0x6A15,(top,0));m[0x6A52]=hover;put(m,0x699D,(5,0xA5))
    seen=[]
    def choice_observe(f,pc):
     if pc in (0x6A1E,0xDB57,0x69A8,0x6A5B,0xC287,0x69B8,0xDB00,0xDB42,0xDB5B):seen.append((hex(pc),list(r[:12]),m.o7ffd,list(m[0xF25D:0xF27D]),[m[a] for a in (0xAEBB,0xAEC7,0xAEB3,0xAEAB)]))
    try:f.run(start,choice_observe)
    except AssertionError:
     print('choice_failed',page,top,hover,seen,'final',list(r[:30]),'stack',m[r[SP]:r[SP]+20],'kernel',m[0xAED5:0xAED8],'bytes',m[r[PC]-8:r[PC]+8]);raise
    assert m.banks[7][0x1B01]==top+hover and m[0x699D:0x699F]==[0,0] and m[0x6A15:0x6A17]==[top,0]
    assert m[0x6A52]==255 and m[0x6A4D]>0 and m[0x9B16]==0 and m.o7ffd==m[0x6306]==0x10 and f.wakes==2
    widths=list(m[0x8900:0x8A00]);body=list(raw[0x8E2:])+[10]*1024
    pointers,_,_,_=index_rows(body,top+hover,width,height,widths,f.initial[2]*256+f.initial[3])
    body_result=justified(0xADCD,body[pointers[0]-0xE3E2:],widths,0,8,width,height,0x0800,0xDB,0x7C,origin=(3,3));bc=body_result[5]
    titles=list(raw[0x87C:0x8E2])+[10]*1024;offset=0
    for _ in range(top+1):offset=titles.index(13,offset)+1
    title_result=stream(titles[offset:],widths,0,8,width,height,0,[m[a] for a in (0xBD73,0xBD7E,0xBD89,0xBD94,0xBD9F)],(3,3),bc>>8)
    consumed,cx,cy,_,_,_=title_result;ptr=0xE37C+offset+consumed;delta=(cy-8)&255;rows=(delta>>3)+1;flags=(rows&0x28)|(16 if (delta>>3)&15==15 else 0)|((delta>>2)&1)
    assert tuple(r[:8])==(0x10,flags,bc>>8,bc&255,0,top,ptr>>8,ptr&255) and r[8]*256+r[9]==0xDB7C+2*len(pointers)
    assert r[SP]==0x8000 and m[0xBD26]==0;counts['section_choice_real_two_draws']+=1;counts['choice_im2_wakes']+=f.wakes
 # Проверка настоящей прокрутки с независимым индексом, очисткой и полным bitmap каждого шага.
 for kind in ('body','contents'):
  for page in (0x10,0x18):
   for direction in ('up','down'):
    for presses in (0,1,3):
     f,keys,blob,start=prepare(kind,0,page);m=f.memory;s=f.sim;r=s.registers;initial=list(r);widths=list(m[0x8900:0x8A00]);text=list(raw[0x8E2:])+[10]*1024
     pointers,_,_,_=index_rows(text,0,width,height,widths,f.initial[2]*256+f.initial[3]);n=len(pointers);cache=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes(2048-2*n);m.banks[7][0x1B7C:0x237C]=list(cache);m.banks[7][0x23E2:0x23E2+len(text)]=text;put(m,0x6995,n.to_bytes(2,'little'))
     frame=list(m[0x4000:0x6000]);attrs=bytes(frame[6144:6912]);index=1;poll=0;steps=0;expected_screen=None
     def observe(f,pc):
      nonlocal index,poll,steps,frame,expected_screen
      if pc==0xA1D6:
       limit=n if kind=='body' else 7;assert m[0xA235]+256*m[0xA236]==limit and m[0xA265]+256*m[0xA266]==(0x69CF if kind=='body' else 0x6A6C)
      if pc==0xA20A:
       assert r[6]*256+r[7]==index;active=poll<presses;m[0x66ED]=int(active)
       if active:
        m[0x6308]=0 if direction=='up' else 191
        if direction=='up':index=max(0,index-1)
        elif index+2<(n if kind=='body' else 7):index+=1
       poll+=1
      if pc==0xA25C:
       assert bytes(m.banks[7][:6144])==bytes(frame[:6144]);flat=bytearray(m[0:65536]);flat[0xC000:]=bytes(m.banks[7]);cleared=bytearray(frame);rectangle(cleared,3,11,width,36);flat[0x4000:0x6000]=cleared;positions=[]
       if kind=='body':justified(0xADCD,text[pointers[index]-0xE3E2:],widths,0,8,width,height,0x0800,0xDB,0x7C,positions,(3,3))
       else:
        source=list(raw[0x87C:0x8E2])+[10]*1024;offset=0
        for _ in range(index+1):offset=source.index(13,offset)+1
        stream(source[offset:],widths,0,8,width,height,0,[m[a] for a in (0xBD73,0xBD7E,0xBD89,0xBD94,0xBD9F)],(3,3),r[2],positions=positions)
       screen,glyphs=paint_positions(flat,positions,width,height,(3,3));frame=list(cleared);frame[:6912]=screen;expected_screen=bytes(screen);steps+=1
      if pc==0xA268:assert bytes(m[0x4000:0x5B00])==expected_screen
     f.run(start,observe)
     saved=0x699D if kind=='body' else 0x6A15
     assert m[saved]+256*m[saved+1]==index and r[6]*256+r[7]==index and (r[0],r[1])==(0,0x44) and m[0x6307:0x6309]==[50,80]
     assert bytes(m[0x4000:0x6000])==bytes(pointer_image(frame,station,50,80)) and bytes(m.banks[7][6144:6912])==attrs
     assert poll==presses+1 and f.wakes==steps and m.o7ffd==m[0x6306]==0x10 and m[0x9B16]==0
     counts['scroll_actions']+=1;counts['scroll_steps_and_im2_wakes']+=steps
 # Проверка обязательного Carry после настоящей перестановки и перерисовки, последующее действие подавляется.
 for kind in ('body','contents'):
  for selector in (0,1,2,127):
   f,keys,blob,start=prepare(kind,selector);m=f.memory;r=f.sim.registers;draw=0x69A8 if kind=='body' else 0x6A5B;other=0x6A5B if kind=='body' else 0x69A8
   put(m,0xF3DE,draw.to_bytes(2,'little')+other.to_bytes(2,'little')+bytes((0,0x5F,1,1)));old_selector=m.banks[7][0x1B01];f.run(start)
   assert r[0]==selector and r[1]&1 and m.banks[7][0x1B01]==old_selector and f.wakes==1
   assert m[0x699D:0x699F]==[1,0] and m[0x6A15:0x6A17]==[1,0];counts['repaint_then_carry_return']+=1;counts['repaint_im2_wakes']+=f.wakes
 # Проверка пустого обработчика наведения текста и его трёхбайтовой JP-обёртки.
 for entry in (0x6978,0x69A7):
  f,_,_,_=prepare('body',0);m=f.memory;s=f.sim;before=[bytes(b) for b in m.banks]
  for flags in range(256):
   s.registers[:]=f.initial;r=s.registers;r[1]=flags;s.run(start=entry,stop=0x3FFF)
   assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000 and [bytes(b) for b in m.banks]==before
   counts['text_hover_noop_returns']+=1
 report=dict(passed=True,cases_by_path=dict(counts),all_256_action_selectors_covered=True,exact_pair_removal_and_fixed_tail=True,ff_guard_checks_low_byte_only=True,
  real_two_panel_choice_and_help_calls=True,independent_scroll_index_and_complete_step_bitmap=True,real_caption_and_scroll_im2=True,
  input_mutated_at_poll_boundaries=True,irq_only_at_halts=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpPanelActionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

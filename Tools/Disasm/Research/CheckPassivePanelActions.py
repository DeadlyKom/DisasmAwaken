"""Действия информации и приветствия, перенос списка, закрытие и настоящая перерисовка."""
import collections,json,random
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckHelpNewsOpening import move
from CheckShipModelActions import remove
from CheckGlyphRenderer import compare_flags
from skoolkit.simutils import SP


MODES=((0x7679,0x768F,19,(0,0,16,24)),(0x794B,0x7955,45,(0,0,32,24)))


def main():
 _,_,base=make_context();counts=collections.Counter();rng=random.Random(0x7679)
 def prepare(mode,selector,y=80,page=0x10,repaint=False):
  entry,draw,key,rect=mode;f=Fixture(base,page=page);m=f.memory;r=f.sim.registers
  # Проверка исходного кода B400, список и весь проверяемый хвост находятся в F3DE.
  assert bytes(m[0xB400:0xB408])==bytes(base[2][0x3400:0x3408])
  put(m,draw+1,(key,0));p=0xF0FD+16*key;put(m,p,(*rect,6,m[p+5]))
  blob=bytearray(rng.randrange(256) for _ in range(512));pointers=[draw,0x5F00] if repaint else [draw];prefix=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes((1,1));blob[:len(prefix)]=prefix
  put(m,0x5F00,(0x21,63,0,0xC9));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,blob);put(m,0x6307,(50,y));m[0xAEBF]=3;m[0xCA20]=6;m[0x9E78]=0;m[0x9A82]=0xA7
  put(m,0x983F,(0x38,0x4B,0,0x4A,4));put(m,0x9844,(0x38,0x4B,0,0x4A,1));r[0]=selector;r[6:8]=[draw>>8,draw&255];r[4:6]=[0,key];r[8:10]=[p>>8,p&255]
  return f,blob
 # Проверка каждого полного селектора без необходимости рисовать уже последний элемент.
 for mode in MODES:
  for page in (0x10,0x18):
   for selector in range(256):
    for y in (3,80):
     f,blob=prepare(mode,selector,y,page);m=f.memory;r=f.sim.registers;entry,draw,key,_=mode;close=[];screen=bytes(m[0x4000:0x5B00]);f.run(entry,lambda f,pc:close.append(pc) if pc==0xC85E else None)
     if selector&128:
      assert r[:2]==[selector,(selector&0xA8)|1] and bytes(m[0xF3DE:0xF5DE])==bytes(blob) and not close and m[0x9A82]==0xA7
      counts['high_selector_no_action']+=1
     else:
      expected,_=move(blob,{draw:key},draw,key)
      if selector==1:
       assert r[:2]==[0,0x42] and not close;counts['selection_no_content_action']+=1
      else:
       assert close==[0xC85E]
       if y==3:
        expected,_,found=remove(expected,{draw:key},(key,),0);assert found and r[:2]==[0,0x44] and m[0x9A82]==0;counts['close_same_character_row']+=1
       else:
        assert r[:2]==[0,compare_flags(0,y>>3)];counts['other_row_no_close']+=1
       assert r[3]==y>>3
      assert bytes(m[0xF3DE:0xF5DE])==bytes(expected) and r[6:8]==[draw>>8,draw&255]
     assert r[4:6]==[0,key] and r[8:12]==[0xF0+(key*16+0xFD)//256,(key*16+0xFD)&255,*f.initial[10:12]]
     assert r[SP]==0x8000 and bytes(m[0x4000:0x5B00])==screen and not f.trace.writes and f.wakes==0
 # Проверка раннего Carry после реальной перерисовки, DEC A и закрытие уже не исполняются.
 for mode in MODES:
  for page in (0x10,0x18):
   for selector in (0,1,2,127):
    f,blob=prepare(mode,selector,page=page,repaint=True);m=f.memory;r=f.sim.registers;entry,draw,key,_=mode;close=[]
    f.run(entry,lambda f,pc:close.append(pc) if pc==0xC85E else None)
    expected,_=move(blob,{draw:key,0x5F00:63},draw,key)
    assert bytes(m[0xF3DE:0xF5DE])==bytes(expected) and r[0]==selector and r[1]&1 and not close and r[4:6]==[0,key]
    assert m.o7ffd==m[0x6306]==0x10 and r[8:12]==[0xF0+(key*16+0xFD)//256,(key*16+0xFD)&255,*f.initial[10:12]] and f.wakes==1,(mode,page,selector,m.o7ffd,m[0x6306],r[8:12],f.wakes)
    if key==45:assert r[6:8]==[0xCE,0x19]
    counts['real_repaint_then_carry_return']+=1;counts['real_caption_im2']+=f.wakes
 report=dict(passed=True,cases_by_path=dict(counts),all_full_selectors=True,whole_512_byte_list_and_128_byte_shifts=True,
  real_repaint_caption_text_and_pointer=True,draw_hl_result_not_restored=True,repaint_final_page_10=True,fixture_b400_original_code_verified=True,
  independent_whole_repaint_bitmap=False,irq_only_at_caption_halt=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PassivePanelActionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

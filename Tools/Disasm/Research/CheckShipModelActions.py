"""Выбор строки, удаление пяти связанных панелей и действие списка с настоящими помощниками."""
import collections,json,random
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckGlyphRenderer import compare_flags
from skoolkit.simutils import SP,PC
GROUP_OPERANDS=(0x7A16,0x6878,0x6946,0x7A56,0x7A83)


def remove(blob,keys,targets,carry):
 blob=bytearray(blob);any_found=False;flags=0
 for wanted in targets:
  found=None
  for position in range(0,len(blob)-130,2):
   pointer=int.from_bytes(blob[position:position+2],'little')
   if pointer>>8==1:break
   key=keys[pointer];carry=int(key<wanted)
   if key==wanted:found=position;break
  if found is not None:
   # Удаление физически переносит ровно 128 байтов, включая хвост после ограничителя.
   blob[found:found+128]=blob[found+2:found+130];carry=0;flags=0x44;any_found=True
  else:flags=0x42|carry
 return blob,flags,any_found


def main():
 _,_,base=make_context();raw=payload(6);base[4][:len(raw)]=list(raw);rng=random.Random(0x6774);counts=collections.Counter()
 # Проверка всех строк выбора, включая FF, двух прежних индексов, экранов и границ слова прокрутки.
 for row in range(256):
  for old in (0x5A,0xA7):
   page=0x10 if row&1 else 0x18;f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;m.banks[4][0x2146]=old;m[0x67D7]=row
   put(m,0x6933,(255-row,row));m[0x68EB]=0;m[0x9B16]=0;before4=bytearray(m.banks[4]);before7=bytes(m.banks[7]);screen=bytes(m.banks[5][:6912]);before_periodic=bytes(m[0x9A89:0x9A8B]);f.trace.writes.clear()
   result=f.run(0x67AA);expected=before4
   if row!=255:expected[0x2146]=row
   assert bytes(m.banks[4])==bytes(expected) and bytes(m[0x6933:0x6935])==bytes(2) and m[0x68EB]==1
   assert tuple(r[:8])==(1,0x0C,f.initial[2],f.initial[3],f.initial[4],f.initial[5],0,0)
   assert r[8:12]==f.initial[8:12] and r[18:24]==f.initial[18:24] and r[SP]==0x8000
   assert m.o7ffd==m[0x6306]==0x10 and m[0x9B16]==0 and bytes(m[0x9A89:0x9A8B])==before_periodic
   assert bytes(m.banks[7][:6912])==screen and bytes(m.banks[7][6912:])==before7[6912:]
   assert f.trace.writes==[(0x7FFD,v) for v in (0x17,0x18,0x1C,0x18,0x10)] and result['wakes']==0
   counts['choice_apply']+=1;counts['choice_ff_preserved']+=row==255
 # Проверка пустого входа перед Apply, он является настоящим RET, а не точкой выполнения выбора.
 f=Fixture(base);m=f.memory;before=[bytes(b) for b in m.banks]
 for flags in range(256):
  f.sim.registers[:]=f.initial;r=f.sim.registers;r[1]=flags;f.run(0x67A9)
  assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and [bytes(b) for b in m.banks]==before
  counts['choice_empty_entry']+=1
 # Проверка пяти удалений, равных индексов, C9-алиасов и физических хвостов фиксированного LDIR.
 for kind in range(8):
  for iteration in range(16):
   f=Fixture(base);m=f.memory;r=f.sim.registers;targets=[30,26,27,28,29] if kind<6 else [iteration&3]*5
   for address,value in zip(GROUP_OPERANDS,targets):put(m,address,value.to_bytes(2,'little'))
   keys={0x5F00+8*i:(targets[i%5] if i<10 else 63+i) for i in range(12)}
   for pointer,key in keys.items():put(m,pointer,bytes((0xC9 if pointer&8 else 0x21,key&255,key>>8,0xC9)))
   selected=list(keys) if kind not in (0,1) else ([] if kind==0 else list(keys)[-2:])
   if kind in (3,7):selected.reverse()
   if kind in (4,5):rng.shuffle(selected)
   blob=bytearray(rng.randrange(256) for _ in range(512));prefix=b''.join(p.to_bytes(2,'little') for p in selected)+bytes((1,1));blob[:len(prefix)]=prefix
   put(m,0xF3DE,blob);put(m,0x9A89,(0x20,0x5F));m[0x9A82]=0xA7;r[1]=iteration&1;wanted,flags,found=remove(blob,keys,targets,r[1]&1);screen=bytes(m.banks[5][:6912]);f.trace.writes.clear()
   f.run(0x6780)
   assert bytes(m[0xF3DE:0xF5DE])==bytes(wanted) and m[0x9A82]==(0 if found else 0xA7) and bytes(m[0x9A89:0x9A8B])==bytes((0x58,0x9A))
   assert tuple(r[:8])==(0,flags,f.initial[2],f.initial[3],targets[-1]>>8,targets[-1]&255,0x9A,0x58)
   assert r[8:12]==f.initial[8:12] and r[16:24]==f.initial[16:24] and bytes(m.banks[5][:6912])==screen and not f.trace.writes
   counts['drop_group']+=1
 # Проверка всех селекторов действия при уже последнем рисователе, текущий элемент удаляется до пяти связанных.
 for selector in range(256):
  for same_row in (False,True):
   for hover in (3,255):
    f=Fixture(base);m=f.memory;r=f.sim.registers;r[0]=selector;r[6]=0x67;r[7]=0xE0;r[4]=0;r[5]=25;r[8]=0xF2;r[9]=0x8D
    put(m,0xF28D,(0,0,24,12,6,5));m[0xCA20]=6;m[0x9E78]=0;m[0x9A82]=0xA7;put(m,0x6307,(50,3 if same_row else 80));m[0xAEC7]=3;m[0xAECB]=0;m[0xAEBB]=3
    put(m,0x9A90,(0x58,0x9A));put(m,0x9A8D,(255,255));put(m,0x6933,(5,0xA5));m[0x67D7]=hover;m[0x68EB]=0;m.banks[4][0x2146]=0xA7;put(m,0x9A89,(0x20,0x5F))
    targets=[30,26,27,28,29]
    for address,value in zip(GROUP_OPERANDS,targets):put(m,address,value.to_bytes(2,'little'))
    pointers=[0x5F00+8*i for i in range(6)]+[0x67E0];keys=dict(zip(pointers,[63,*targets,25]))
    for pointer,key in list(keys.items())[:-1]:put(m,pointer,(0x21,key,0,0xC9))
    blob=bytearray(512);prefix=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes((1,1));blob[:len(prefix)]=prefix;put(m,0xF3DE,blob);f.trace.writes.clear();f.run(0x6774)
    if selector&128:
     assert (r[0],r[1])==(selector,(selector&0xA8)|1) and bytes(m[0xF3DE:0xF5DE])==bytes(blob);counts['action_high_bit_return']+=1
    elif selector==1:
     assert (r[0],r[1],m[0x68EB])==(1,0x0C,1) and bytes(m[0x6933:0x6935])==bytes(2) and m.banks[4][0x2146]==(hover if hover!=255 else 0xA7)
     assert bytes(m[0xF3DE:0xF5DE])==bytes(blob);counts['action_choice']+=1
    elif same_row:
     wanted,flags,found=remove(blob,keys,[25,*targets],0)
     assert bytes(m[0xF3DE:0xF5DE])==bytes(wanted) and m[0x9A82]==0 and bytes(m[0x9A89:0x9A8B])==bytes((0x58,0x9A)) and r[0]==0
     counts['action_close_group']+=1
    else:
     assert bytes(m[0xF3DE:0xF5DE])==bytes(blob) and m[0x9A82]==0xA7 and (r[0],r[1],r[3])==(0,compare_flags(0,10),10);counts['action_other_row']+=1
    assert r[SP]==0x8000 and (selector==1 or bytes(m[0x6933:0x6935])==bytes((5,0xA5)))
    if selector!=1:assert m[0x68EB]==0 and m.banks[4][0x2146]==0xA7 and not f.trace.writes
 # Проверка Carry после настоящей перестановки и перерисовки, выбор строки после неё не выполняется.
 for selector in (0,1,2,127):
  f=Fixture(base);m=f.memory;r=f.sim.registers;r[0]=selector;r[6]=0x67;r[7]=0xE0;r[4]=0;r[5]=25;r[8]=0xF2;r[9]=0x8D
  put(m,0xF28D,(1,1,24,12,6,m[0xF28D+5]));put(m,0x5F00,(0x21,63,0,0xC9));put(m,0xF3DE,(0xE0,0x67,0,0x5F,1,1));m[0xCA20]=6
  put(m,0x6933,(5,0xA5));m[0x68EB]=0;m[0x67D7]=3;put(m,0x9A89,(0x20,0x5F));before_model=m.banks[4][0x2146]
  result=f.run(0x6774)
  assert r[0]==selector and r[1]&1 and bytes(m[0x6933:0x6935])==bytes((5,0xA5)) and m[0x68EB]==0 and m.banks[4][0x2146]==before_model
  assert bytes(m[0xF3DE:0xF3E4])==bytes((0,0x5F,0xE0,0x67,1,1)) and result['wakes']==1
  counts['action_repaint_first_return']+=1;counts['redraw_irq_wakeups']+=result['wakes']
 report=dict(passed=True,cases_by_path=dict(counts),all_256_hover_rows=True,hover_ff_preserves_model_byte=True,full_description_top_word_reset=True,
  all_256_action_selectors=True,exact_five_drop_order_and_128_byte_tail_shifts=True,duplicate_and_disabled_aliases=True,
  real_repaint_pointer_row_close_screen_and_bank_helpers=True,no_immediate_preview_render=True,selection_requests_deferred_redraw=True,
  independent_list_and_register_oracle=True,irq_executed=True,irq_only_at_redraw_caption_halts=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShipModelActionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

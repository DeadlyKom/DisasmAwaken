"""Выбор продажи/покупки, байт модели банка 4 и реальное переключение двух рамок."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckEnvironmentRows import inc_flags
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();d3d=payload(6);base[4][:len(d3d)]=list(d3d);counts=collections.Counter();centered=json.loads((ROOT/'Tools/Disasm/Reports/Symbols.json').read_text('utf-8'))['Station.DrawCenteredItem.Entry']
 def prepare(page=0x10):
  f=Fixture(base,page=page);m=f.memory;put(m,0x7A56,(28,0));put(m,0x7A83,(29,0));m.banks[4][0x2146]=0xA7;m[0x68EB]=0xA5;m[0x79DD]=0x5A
  for key,rect in ((28,(1,1,9,4)),(29,(12,1,9,4))):
   p=0xF0FD+16*key;put(m,p,(*rect,0x26,m[p+5]))
  put(m,0xAED5,(0x68,0x48,0x26));return f
 # Проверка полного раннего RET C, все A и все F с установленным Carry сохраняются.
 for entry in (0x7A24,0x7A64):
  f=prepare();m=f.memory;s=f.sim;before=[bytes(b) for b in m.banks]
  for af in range(1,65536,2):
   s.registers[:]=f.initial;r=s.registers;r[:2]=[af>>8,af&255];s.run(start=entry,stop=0x3FFF)
   assert r[:2]==[af>>8,af&255] and r[2:12]==f.initial[2:12] and r[16:24]==f.initial[16:24] and r[SP]==0x8000;counts['carry_guard_returns']+=1
  assert [bytes(b) for b in m.banks]==before and not f.trace.writes
 # Проверка всех селекторов и всех байтов собственного типа, остановка перед рисованием контуров.
 f=prepare();m=f.memory;s=f.sim
 for selector in range(256):
  for owned in range(256):
   m.out7ffd(0x10);m[0x6306]=0x10;m[0x6906]=selector;m[0x9849]=owned if selector==0 else owned^255;m[0x984A]=owned if selector!=0 else owned^255;m.banks[4][0x2146]=0xA7;m[0x68EB]=0xA5;m[0x79DD]=0x5A;put(m,0x7FFE,(255,63));s.registers[:]=f.initial;r=s.registers;r[1]&=254;r[4:6]=[0,28];f.trace.writes.clear();s.run(start=0x7A24,stop=0xA806)
   assert tuple(r[4:8])==((0,28,0,29) if owned!=255 else (0,29,0,28))
   assert tuple(r[:2])==((1,inc_flags(owned)) if owned!=255 else (0,0x44)) and m[0x79DD]==int(owned!=255)
   assert m[0x68EB]==1 and m.banks[4][0x2146]==0 and m.o7ffd==0x10 and r[SP]==0x7FFE and f.trace.writes==[(0x7FFD,0x14),(0x7FFD,0x10)];counts['all_selector_owned_pairs_before_contour']+=1
 # Проверка полного слова нового индекса покупки до обращения к FInterfaceItem, неверные индексы дальше не запускаются.
 for new_index in range(65536):
  m.out7ffd(0x10);m[0x6306]=0x10;m.banks[4][0x2146]=0xA7;m[0x68EB]=0xA5;m[0x79DD]=0x5A;put(m,0x7FFE,(255,63));s.registers[:]=f.initial;r=s.registers;r[1]&=254;r[4:6]=[new_index>>8,new_index&255];f.trace.writes.clear();s.run(start=0x7A64,stop=0xA806)
  assert tuple(r[4:8])==(new_index>>8,new_index&255,0,28) and r[:2]==[0,0x44] and m[0x79DD]==0 and m[0x68EB]==1 and m.banks[4][0x2146]==0;counts['all_new_purchase_words_before_contour']+=1
 # Проверка полного переключения рамок, обоих экранных битов, нулевого и ненулевого селектора и FF.
 for entry in (0x7A24,0x7A64):
  for page in (0x10,0x18):
   for selector in (0,1,2,255):
    for owned in (0,3,255):
     for flags in (0,1,0xFE,0xFF):
      f=prepare(page);m=f.memory;r=f.sim.registers;r[1]&=254;r[4:6]=[0,28 if entry==0x7A24 else 29];m[0x6906]=selector;m[0x9849]=owned if selector==0 else owned^255;m[0x984A]=owned if selector!=0 else owned^255
      p28=0xF0FD+16*28;p29=0xF0FD+16*29;m[p28+4]=flags;m[p29+4]=flags^0xAA;before4=bytearray(m.banks[4]);before4[0x2146]=0;f.trace.writes.clear();f.run(entry)
      sale=entry==0x7A24 and owned!=255;new=28 if sale else 29;old=29 if sale else 28
      assert r[4:8]==[0,new,0,new] and r[0]==0xC3 and r[2:4]==f.initial[2:4] and r[8:12]==f.initial[8:12] and r[18:23]==f.initial[18:23]
      assert m[0x79DD]==int(sale) and m[0x68EB]==1 and bytes(m.banks[4])==bytes(before4) and m[0x9B16]==0
      oldflags=(flags^0xAA) if old==29 else flags;newflags=flags if new==28 else flags^0xAA
      assert m[0xF0FD+16*old+4]==oldflags&254 and m[0xF0FD+16*new+4]==newflags|1
      assert m.o7ffd==m[0x6306]==page and f.wakes==0 and f.trace.writes==[(0x7FFD,(page&0xF8)|0x14),(0x7FFD,page)];counts['full_two_contour_calls']+=1
 # Проверка общего входа покупки, он обходит Carry и не сбрасывает строку либо запрос перерисовки.
 for page in (0x10,0x18):
  for flags in (0,1,0x40,0xFF):
   f=prepare(page);m=f.memory;r=f.sim.registers;r[1]=flags;r[4:6]=[0,29];f.run(0x7A78)
   assert m[0x79DD]==0 and m[0x68EB]==0xA5 and m.banks[4][0x2146]==0xA7 and r[4:8]==[0,29,0,29] and not f.trace.writes;counts['shared_purchase_entry_without_reset']+=1
 # Проверка двух исходных кнопочных JP-обёрток сравнением с тем же реальным DrawCenteredItem.
 for entry,index in ((0x7A55,28),(0x7A82,29)):
  for flags in (0,1,0xFE,0xFF):
   outcomes=[]
   for start in (entry,centered):
    f=prepare();m=f.memory;r=f.sim.registers;m[0xF0FD+16*index+4]=flags
    if start==centered:r[6:8]=[0,index]
    f.run(start);outcomes.append((list(r[:12]),list(r[16:24]),[bytes(b) for b in m.banks]))
   assert outcomes[0]==outcomes[1];counts['mode_button_wrapper_equivalence']+=1
  f=prepare();m=f.memory;s=f.sim;m[entry]=0xC9;before=[bytes(b) for b in m.banks]
  for flags in range(256):
   s.registers[:]=f.initial;r=s.registers;r[1]=flags;s.run(start=entry,stop=0x3FFF)
   assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000 and [bytes(b) for b in m.banks]==before;counts['disabled_mode_button_returns']+=1
 report=dict(passed=True,cases_by_path=dict(counts),all_selector_and_owned_bytes=True,all_carry_guard_af=True,all_new_purchase_indices_stopped_before_contour=True,
  original_bank_4_row_operand_only_reset=True,both_screen_bits_preserved=True,real_centered_frames_and_pointer=True,
  shared_tail_does_not_reset_row_or_pending=True,independent_whole_contour_bitmap=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ModelTradeModeVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

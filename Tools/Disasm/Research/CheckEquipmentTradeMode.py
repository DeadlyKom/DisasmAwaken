"""Две кнопки режима оборудования, исходные подписи и оба пути Carry."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();counts=collections.Counter();roles=[]
 def prepare(page=0x10):
  f=Fixture(base,page=page);m=f.memory
  put(m,0x7B26,(37,0));put(m,0x7B41,(36,0));m[0x71EC]=0xA5
  for key,x in ((36,1),(37,12)):
   p=0xF0FD+16*key;put(m,p,(x,1,9,4,0x26,m[p+5]))
  put(m,0xAED5,(0x68,0x48,0x26));return f
 f=prepare();m=f.memory
 # Проверка подписей через исходное правило SkipLfRecords, сначала пропускается LF перед первой записью.
 for key,word,expected in ((36,0x7B41,'Продажа'),(37,0x7B26,'Покупка')):
  record=0xF0FD+16*key;p=0xE4AA
  for _ in range(m[record+5]+1):
   while m[p]!=10:p+=1
   p+=1
  end=p
  while m[end]!=13:end+=1
  caption=bytes(m[p:end]).decode('cp866');assert caption==expected
  assert m[word-1]==0x21 and m[record+12]+256*m[record+13]==word-1
  roles.append(dict(index=key,caption=caption,wrapper=word-1))
 # Проверка всех AF с Carry, никакой режим, память, порты и регистры не меняются.
 for entry in (0x7B1A,0x7B34):
  f=prepare();m=f.memory;s=f.sim;before=[bytes(b) for b in m.banks]
  for af in range(1,65536,2):
   s.registers[:]=f.initial;r=s.registers;r[:2]=[af>>8,af&255];s.run(start=entry,stop=0x3FFF)
   assert r[:12]==[af>>8,af&255,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
   counts['carry_guard_af']+=1
  assert [bytes(b) for b in m.banks]==before and not f.trace.writes
 # Проверка всех слов нового индекса до доступа к записям, неверные адреса в рисователь не передаются.
 for entry,mode,old in ((0x7B1A,0,36),(0x7B34,1,37)):
  f=prepare();m=f.memory;s=f.sim
  for new in range(65536):
   put(m,0x7FFE,(255,63));m[0x71EC]=0xA5;s.registers[:]=f.initial;r=s.registers;r[1]&=254;r[4:6]=[new>>8,new&255]
   s.run(start=entry,stop=0xA806)
   assert r[4:8]==[new>>8,new&255,0,old] and m[0x71EC]==mode and r[0]==mode and r[1]==(0x44 if mode==0 else f.initial[1]&254)
   assert r[SP]==0x7FFE;counts['new_index_words_before_contour']+=1
 # Проверка реальных контуров и указателя, обе экранные страницы и все предыдущие значения режима.
 for entry,mode,new,old in ((0x7B1A,0,37,36),(0x7B34,1,36,37)):
  for page in (0x10,0x18):
   for previous in range(256):
    f=prepare(page);m=f.memory;r=f.sim.registers;r[1]&=254;r[4:6]=[0,new];m[0x71EC]=previous
    po=0xF0FD+16*old;pn=0xF0FD+16*new;m[po+4]=previous;m[pn+4]=previous^0xAA;f.run(entry)
    assert m[0x71EC]==mode and m[po+4]==previous&254 and m[pn+4]==(previous^0xAA)|1
    assert r[4:8]==[0,new,0,new] and r[0]==0xC3 and r[2:4]==f.initial[2:4] and r[8:12]==f.initial[8:12] and r[18:23]==f.initial[18:23]
    assert m.o7ffd==m[0x6306]==page and not f.trace.writes and f.wakes==0;counts['real_contour_calls']+=1
 # Проверка обёрток сравнением с тем же исходным рисователем, без независимого oracle bitmap.
 for wrapper,key in ((0x7B25,37),(0x7B40,36)):
  for flags in (0,1,0xFE,0xFF):
   states=[]
   for entry in (wrapper,0xC2DF):
    f=prepare();m=f.memory;r=f.sim.registers;m[0xF0FD+16*key+4]=flags
    if entry==0xC2DF:r[6:8]=[0,key]
    f.run(entry);states.append((list(r[:12]),list(r[16:24]),[bytes(b) for b in m.banks]))
   assert states[0]==states[1];counts['wrapper_equivalence']+=1
  f=prepare();m=f.memory;s=f.sim;m[wrapper]=0xC9;before=[bytes(b) for b in m.banks]
  for flags in range(256):
   s.registers[:]=f.initial;r=s.registers;r[1]=flags;s.run(start=wrapper,stop=0x3FFF)
   assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
   counts['disabled_wrapper_flags']+=1
  assert [bytes(b) for b in m.banks]==before
 report=dict(passed=True,cases_by_path=dict(counts),physical_button_roles=roles,all_previous_mode_bytes=True,
  independent_whole_contour_bitmap=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EquipmentTradeModeVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

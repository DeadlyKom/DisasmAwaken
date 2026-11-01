"""Исходная подпись Перелет, пустой callback, его настоящий вызов при закрытии и рисователь кнопки."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();counts=collections.Counter();record=0xF0FD+16*21
 assert base[0][record-0xC000+5]==40
 text=bytes(base[0][0x24AA:]).split(bytes((10,)))[41];assert text==bytes((0x8F,0xA5,0xE0,0xA5,0xAB,0xA5,0xE2,13))
 f=Fixture(base);m=f.memory;s=f.sim;before=[bytes(b) for b in m.banks]
 # Проверка всех AF исходного RET, остальные пары, порты и вся память сохраняются.
 for af in range(65536):
  s.registers[:]=f.initial;r=s.registers;r[:2]=[af>>8,af&255];s.run(start=0x7B50,stop=0x3FFF)
  assert r[:12]==[af>>8,af&255,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
  counts['empty_callback_all_af']+=1
 assert [bytes(b) for b in m.banks]==before and not f.trace.writes
 # Проверка исходной установки и фактического косвенного вызова через CloseActiveItem.
 for page in (0x10,0x18):
  f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;put(m,record,(1,1,5,2,0x11,40));put(m,0x7B52,(21,0));put(m,0xF3DE,(0x51,0x7B,1,1));m[0x9E78]=255;put(m,0x9E7E,(21,0));m[0x9839]=0;r[0]=1;r[4:6]=[0,21];r[8:10]=[record>>8,record&255]
  f.run(0x7B46);assert m[0x9E8B]+256*m[0x9E8C]==0x7B50
  put(m,0x7FFE,(255,63));r[SP]=0x7FFE;seen=[]
  def observe(f,pc):
   if pc==0x7B50:
    assert r[0:2]==[0,0x44] and r[SP]==0x7FF8 and m[0x7FF8]+256*m[0x7FF9]==0x9E8D;seen.append(pc)
  f.run(0x9E77,observe)
  assert seen==[0x7B50] and r[:2]==[0,0x45] and m[0x9E78]==0 and bytes(m[0x9E8B:0x9E8D])==bytes((0x58,0x9A)) and f.wakes==0
  counts['real_install_and_close_callback']+=1
 # Проверка рисователя как точного хвостового входа DrawCenteredItem на исходном тексте.
 for page in (0x10,0x18):
  for flags in (0x60,0x61):
   outputs=[]
   for entry in (0x7B51,0xC2DF):
    f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;put(m,record,(16,21,5,2,flags,40));put(m,0x7B52,(21,0));put(m,0xF3DE,(0x51,0x7B,1,1));r[6:8]=[0,21];f.run(entry)
    outputs.append((list(r[:12]),list(r[16:24]),[bytes(b) for b in m.banks],list(f.trace.writes)))
   assert outputs[0]==outputs[1];counts['draw_tail_equivalence']+=1
 report=dict(passed=True,cases_by_path=dict(counts),original_caption=text.decode('cp866').rstrip('\r'),physical_text_index=40,
  explicit_callback_source=0x7B49,callback_target=0x7B50,actual_indirect_callback_executed=True,flight_algorithm_present_in_callback=False,
  independent_bitmap=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/FlightButtonVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

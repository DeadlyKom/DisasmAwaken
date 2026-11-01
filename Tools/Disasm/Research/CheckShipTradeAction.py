"""Полный обработчик подтверждения модели, настоящий LANG и завершение интерфейсного цикла."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from skoolkit.simutils import PC,SP


def prepare(base,row=0,owned_mode=0,selector=0,page=0x10,owned=255,credits=65535):
 f=Fixture(base,page=page);m=f.memory;r=f.sim.registers
 for address,value in ((0x67E1,25),(0x7A16,30),(0x6878,26),(0x6946,27),(0x7A56,28),(0x7A83,29),(0x7F36,0),(0x6E8B,24)):
  put(m,address,value.to_bytes(2,'little'))
 m[0x67D7]=row;m[0x79DD]=owned_mode;m[0x6906]=selector;m[0x9849]=owned;m[0x984A]=255;m[0x9851]=255;m[0x9E78]=0xA7
 m.banks[4][0x2148]=0;put(m,0x984E,credits.to_bytes(2,'little'));put(m,0x9852,bytes(60));put(m,0x988E,bytes(52));put(m,0x98F6,bytes(14))
 record=0xF0FD;put(m,record,(0,0,32,5,0,m[record+5]));m[0x993D]=0x80
 pointers=(0x67E0,0x7A15,0x6877,0x6945,0x7A55,0x7A82,0x7F35)
 put(m,0xF3DE,b''.join(p.to_bytes(2,'little') for p in pointers)+bytes((1,1)))
 return f


def main():
 _,_,base=make_context()
 for bank,slot in ((4,6),(6,5)):
  raw=payload(slot);base[bank][:len(raw)]=list(raw)
 counts=collections.Counter();events=collections.Counter();finals=set();calls_expected=(0xA49F,0x7F35,0xA496,0x6780)
 # Проверка полного пути каждого корабля, обоих экранов, режимов и исходов недостатка денег.
 for mode in (0,1):
  for selector in (0,1):
   for row in range(7):
    for page in (0x10,0x18):
     for owned,credits in ((255,0),(255,65535),(0,65535)):
      f=prepare(base,row,mode,selector,page,owned,credits);m=f.memory;r=f.sim.registers;calls=[];seen=[]
      def observe(f,pc):
       if pc==0xC000 and m.o7ffd&7==6:
        seen.append(m[0x983A]);assert m.banks[4][0x2146]==row
       if pc in calls_expected:calls.append(pc)
      f.run(0x79C7,observe);event=1+int(mode!=0)+2*int(selector!=0)
      assert seen==[event] and tuple(calls)==calls_expected,(event,row,seen,calls)
      # Проверка реального списка по индексам рисователей после шести последовательных удалений.
      keys=[]
      for position in range(0,130,2):
       pointer=m[0xF3DE+position]+256*m[0xF3DF+position]
       if pointer>>8==1:break
       keys.append(m[pointer+1]+256*m[pointer+2])
      assert 0 in keys and not set(keys)&{25,26,27,28,29,30},keys
      assert m[0x9E78]==0 and m[0x9B16]==0 and m.o7ffd==m[0x6306]==0x10
      assert bytes(m[0x9A89:0x9A8B])==bytes((0x58,0x9A)) and r[0:2]==[0,0x44] and r[4:8]==[0,29,0x9A,0x58] and r[SP]==0x8000
      assert r[10:12]==f.initial[10:12] and f.wakes==0
      finals.add(tuple(r[2:4]));counts['complete_action']+=1;events[str(event)]+=1
 # Проверка всех байтов обоих переключателей до входа в настоящий LANG без вызова недопустимой записи.
 for field in ('mode','selector'):
  for value in range(256):
   mode=value if field=='mode' else 0;selector=value if field=='selector' else 0;f=prepare(base,3,mode,selector);m=f.memory;r=f.sim.registers;r[PC]=0x79C7
   for _ in range(100):
    if r[PC]==0xC000 and m.o7ffd&7==6:break
    f.sim.run()
   else:raise AssertionError(('event_entry_not_reached',field,value,hex(r[PC])))
   assert m[0x983A]==1+int(mode!=0)+2*int(selector!=0) and m.banks[4][0x2146]==3
   counts['all_mode_and_selector_bytes']+=1
 # Проверка раннего FF без единого банкового переключения и без изменений регистров кроме AF.
 for flags in range(256):
  f=prepare(base,row=255);m=f.memory;r=f.sim.registers;r[1]=flags;before=[bytes(b) for b in m.banks];f.trace.writes.clear();f.run(0x79C7)
  assert r[0:2]==[0,0x50|(flags&1)] and r[2:12]==f.initial[2:12] and r[16:24]==f.initial[16:24]
  assert [bytes(b) for b in m.banks]==before and not f.trace.writes;counts['ff_return_all_flags']+=1
 report=dict(passed=True,cases_by_path=dict(counts),per_event=dict(events),final_bc_values=[list(v) for v in sorted(finals)],
  actual_original_lang=True,real_status_redraw_and_six_removals=True,independent_whole_status_bitmap=False,
  all_mode_and_selector_bytes=True,ff_does_not_select_bank=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShipTradeActionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

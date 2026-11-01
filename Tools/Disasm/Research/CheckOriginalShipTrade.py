"""События корабля в неизменённом LANG, независимые денежные и предметные результаты."""
import collections,json
from ProbeShipPreviewCallbacks import ROOT,make_context,payload,put
from CheckScreenUpdate import PortTrace
from CheckWeightedLoad import reference as load_reference
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,PC,SP


def main():
 _,_,base=make_context()
 for bank,slot in ((4,6),(6,5)):
  raw=payload(slot);base[bank][:len(raw)]=list(raw)
 script=bytes(base[6][0xA8F:0xF18]);counts=collections.Counter();messages=collections.Counter()
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 def execute(event,index,owned,credits,capacity=255,cargo=0,blocked=False):
  page=0x16 if sum(counts.values())&1 else 0x1E;m=SliceableMemory(banks=[b.copy() for b in base],out7ffd=page)
  s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);m[0x6306]=page;m[0x983A]=event
  m.banks[4][0x2146]=index;m.banks[4][0x2148]=0;m[0x9849]=owned;m[0x984A]=255;m[0x9851]=capacity
  put(m,0x9852,bytes(60));put(m,0x988E,bytes(52));put(m,0x98F6,bytes(14));m[0x9852]=cargo
  put(m,0x984E,credits.to_bytes(2,'little'));put(m,0x983F,(4,0x38,0x4A,0));m[0x9843]=0
  # Создание нарушения только для отдельного активного оснащения, сам алгоритм читает исходные таблицы.
  if blocked:m[0x988E]=1;m[0x95F0]=255
  put(m,0x6E8B,(24,0));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(1,1));m[0x6E91]=0xA7
  before=bytearray(m[0:65536]);weight=load_reference(before,0xC0DB)[0]
  price=lambda item:before[0x9803+5*item]+256*before[0x9804+5*item]
  selected_price=price(index);limit=before[0x9802+5*index];expected_messages=[];expected_owned=owned;expected_credits=credits;expected_capacity=capacity
  # Проверка независимого результата по исходным порядку условий и ширине полей.
  if event==1:
   if owned!=255:expected_messages=[1]
   elif selected_price>credits:expected_messages=[0]
   elif limit<weight:expected_messages=[2]
   elif blocked:expected_messages=[6]
   else:expected_owned=index;expected_credits=credits-selected_price;expected_capacity=limit;expected_messages=[11]
  elif event==2:
   if owned==255:expected_messages=[8]
   elif before[0x9806+5*owned]==0:
    expected_messages=[3];expected_credits=min(65535,credits+price(owned));expected_owned=255
   else:
    if min(65535,credits+selected_price)>65000:expected_messages.append(10)
    expected_credits=min(65535,credits+price(owned));expected_owned=255;expected_capacity=0;expected_messages.append(11)
  put(m,0x7FFE,(255,63));s.registers[:]=initial;s.registers[PC]=0xC000;observed=[]
  for _ in range(240000):
   if s.registers[PC]==0x3FFF:break
   if s.registers[PC]==0xA85F:observed.append(s.registers[A])
   s.run()
  else:raise AssertionError(('instruction_limit',event,index,owned,hex(s.registers[PC])))
  actual=(m[0x9849],m[0x984E]+256*m[0x984F],m[0x9851],observed)
  wanted=(expected_owned,expected_credits,expected_capacity,expected_messages)
  assert actual==wanted,(event,index,owned,credits,capacity,cargo,blocked,weight,actual,wanted)
  assert m[0x9850]==load_reference(bytearray(m[0:65536]),0xC0DB)[0]
  assert bytes(m.banks[6][0xA8F:0xF18])==script and s.registers[SP]==0x8000 and m.o7ffd==m[0x6306]==page
  assert m[0x6E91]==(observed[-1] if observed else 0xA7)
  counts[str(event)]+=1;messages.update(observed)
 # Проверка всех семи исходных кораблей, текущего выбора, денежных границ и отказов.
 for event in (1,2,3,4):
  for index in range(7):
   for owned in (255,*range(7)):
    for credits in (0,1,1000,64000,65000,65535):execute(event,index,owned,credits)
 for index in range(7):
  for cargo in (0,1,16,127):
   for blocked in (False,True):execute(1,index,255,65535,cargo=cargo,blocked=blocked)
 report=dict(passed=True,per_event=dict(counts),queued_messages=dict(messages),original_script_bytes_unchanged=True,
  actual_interpreter_and_original_script=True,independent_ship_price_capacity_and_selection_oracle=True,
  events_3_and_4_have_no_matching_block=True,real_bank_switching=True,station_display_not_executed=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/OriginalShipTradeVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

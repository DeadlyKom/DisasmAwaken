"""Покупка и продажа оснащения исходным LANG с независимой моделью последовательности проверок."""
import collections,json
from ProbeShipPreviewCallbacks import ROOT,make_context,payload,put
from CheckScreenUpdate import PortTrace
from CheckWeightedLoad import reference as load_reference
from CheckActiveNeighbors import reference as neighbor_reference
from CheckWorldSignature import signature
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,PC,SP


def decode(raw):return raw if raw<128 else raw^255


def main():
 _,_,base=make_context();raw=payload(5);base[6][:len(raw)]=list(raw);script=bytes(base[6][0xA8F:0xF18]);counts=collections.Counter();messages=collections.Counter()
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 def execute(event,index,quantity,owned,credits,capacity=255,neighbor=False):
  page=0x16 if sum(counts.values())&1 else 0x1E;m=SliceableMemory(banks=[b.copy() for b in base],out7ffd=page);s=Simulator(m);s.set_tracer(PortTrace(s))
  m[0x6306]=page;m[0x983A]=event;m[0x7217]=index;m[0x71B9]=0;m[0x9849]=owned;m[0x984A]=255;m[0x9851]=capacity
  put(m,0x9852,bytes(60));put(m,0x988E,bytes(52));put(m,0x98F6,bytes(14));m[0x988E+index]=quantity
  if neighbor:m[0x988E+((index+1)%30)]=1
  put(m,0x984E,credits.to_bytes(2,'little'));put(m,0x983F,(0x38,0x4B,0,0x4A,0));put(m,0x6E8B,(24,0));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(1,1));m[0x6E91]=0xA7
  before=bytearray(m[0:65536]);weight=load_reference(before,0xC0DB)[0];price=before[0x9592+2*index]+256*before[0x9593+2*index]
  threshold=before[0x95F0+2*index];unit=before[0x95F1+2*index];key_limit=signature(0x4B38,0x4A00,0)['size']
  quantity_value=decode(quantity);expected_messages=[];result=quantity_value;expected_credits=credits
  # Проверка очередности исходных условий, @ разрешает M05 только для нулевого 255-k.
  if event==5:
   if threshold>key_limit:expected_messages=[7]
   elif owned==255:expected_messages=[4]
   elif owned in before[0x9400+4*index:0x9404+4*index]:expected_messages=[6]
   elif neighbor_reference(before,index,0x964E,0x988E)[-1]:expected_messages=[12]
   elif quantity_value>=(1 if quantity&128 else 127):expected_messages=[5]
   elif price>credits:expected_messages=[0]
   elif min(65535,weight+unit)>capacity:expected_messages=[2]
   else:result=quantity_value+1;expected_credits=max(0,credits-price)
  else:
   if quantity_value==0:expected_messages=[8]
   else:
    if min(65535,credits+price)>65000:expected_messages=[10]
    result=max(0,quantity_value-1);expected_credits=min(65535,credits+price)
  expected_raw=quantity if result==quantity_value else ((result&255)^255 if quantity&128 else result&255)
  put(m,0x7FFE,(255,63));s.registers[:]=initial;s.registers[PC]=0xC000;observed=[]
  for _ in range(240000):
   if s.registers[PC]==0x3FFF:break
   if s.registers[PC]==0xA85F:observed.append(s.registers[A])
   s.run()
  else:raise AssertionError(('instruction_limit',event,index,quantity,owned,hex(s.registers[PC])))
  actual=(m[0x988E+index],m[0x984E]+256*m[0x984F],observed);wanted=(expected_raw,expected_credits,expected_messages)
  assert actual==wanted,(event,index,quantity,owned,credits,capacity,neighbor,threshold,key_limit,actual,wanted)
  assert m[0x9850]==load_reference(bytearray(m[0:65536]),0xC0DB)[0] and m[0x9849]==owned and m[0x9851]==capacity
  assert bytes(m.banks[6][0xA8F:0xF18])==script and s.registers[SP]==0x8000 and m.o7ffd==m[0x6306]==page
  assert m[0x6E91]==(observed[-1] if observed else 0xA7)
  counts[str(event)]+=1;messages.update(observed)
 # Проверка всех тридцати строк и обеих кодировок количества с денежными границами.
 for event in (5,6):
  for index in range(30):
   for quantity in (0,1,2,126,127,128,129,254,255):
    for owned in (0,255):
     for credits in (0,65535):execute(event,index,quantity,owned,credits)
 # Проверка каждого физического байта количества, вместимости и соседства.
 for quantity in range(256):execute(6,0,quantity,0,65000)
 for index in range(30):
  for owned in range(7):
   for neighbor in (False,True):
    for capacity in (0,1,255):execute(5,index,0,owned,65535,capacity,neighbor)
 report=dict(passed=True,per_event=dict(counts),queued_messages=dict(messages),all_30_equipment_rows=True,all_quantity_bytes=True,
  original_script_bytes_unchanged=True,actual_interpreter_and_original_script=True,independent_quantity_credits_conditions_and_messages=True,
  inverse_at_checks_missing_ship=True,real_bank_switching=True,station_display_not_executed=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/OriginalEquipmentTradeVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

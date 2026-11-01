"""Исходные входной и периодический сценарии станции, статус, штрафы, плата и реальная команда W."""
import collections,json
from ProbeShipPreviewCallbacks import ROOT,make_context,payload,put
from CheckScreenUpdate import PortTrace
from CheckWeightedLoad import reference as weight
from CheckWorldSignature import signature
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,PC,SP


CLEARED=(2,3,5,6,7,8,9,31)


def main():
 _,_,base=make_context();lang=payload(5);base[6][:len(lang)]=list(lang);script=bytes(base[6][0xA8F:0xF18]);counts=collections.Counter();messages=collections.Counter()
 initial=get_registers({'SP':0x7FFE,'AF':0x5A5D,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 def execute(event,status,credits,quantity_seed=0,second=0x4A00,owned=255):
  m=SliceableMemory(banks=[b.copy() for b in base],out7ffd=0x16);s=Simulator(m);s.set_tracer(PortTrace(s));m[0x6306]=0x16;m[0x983A]=event;m[0x984B]=status;m[0x9849]=owned;m[0x984A]=255
  put(m,0x984E,credits.to_bytes(2,'little'));put(m,0x9852,bytes(60));quantities=bytes((quantity_seed+29*i)&255 for i in range(32));put(m,0x988E,quantities);put(m,0x98F6,bytes(14));put(m,0x983F,bytes((0x38,0x4B))+second.to_bytes(2,'little')+bytes((0,)))
  put(m,0x6E8B,(24,0));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(1,1));m[0x6E91]=0xA7;m[0x9AB7]=0xA5;put(m,0x7FFE,(255,63));s.registers[:]=initial;s.registers[PC]=0xC000
  expected_credit=credits;expected_status=status;expected_quantities=bytearray(quantities);expected_messages=[];expected_transition=0xA5;exit_to_4200=False
  if event==15:
   if 48<=status<64:expected_credit=max(0,credits-50);expected_messages=[15]
   elif status>=64:
    expected_credit=max(0,credits-1000);expected_status=status-48;expected_messages=[14]
    for i in CLEARED:expected_quantities[i]=255 if quantities[i]&128 else 0
  if event==16:
   unit=signature(0x4B38,second,0)['size']
   if credits<=unit:expected_credit=0;expected_messages=[13];expected_transition=255;exit_to_4200=owned!=255
   else:expected_credit=max(0,credits-5*unit)
  observed=[];ticks=0;w_calls=0
  for _ in range(300000):
   pc=s.registers[PC]
   if pc in (0x3FFF,0x4200):break
   if pc==0xA85F:observed.append(s.registers[A])
   if pc==0xC86F:ticks+=1
   if pc==0x7E5A:w_calls+=1
   s.run()
  else:raise AssertionError(('instruction_limit',event,status,credits,owned,hex(s.registers[PC])))
  actual=(m[0x984E]+256*m[0x984F],m[0x984B],bytes(m[0x988E:0x98AE]),observed,m[0x9AB7])
  wanted=(expected_credit,expected_status,bytes(expected_quantities),expected_messages,expected_transition)
  assert actual==wanted,(event,status,credits,quantity_seed,second,owned,actual,wanted)
  assert s.registers[PC]==(0x4200 if exit_to_4200 else 0x3FFF)
  if not exit_to_4200:assert s.registers[SP]==0x8000 and m.o7ffd==m[0x6306]==0x16
  assert ticks==1+int(event==17 or event==15 and status>=64) and w_calls==int(event==16 and expected_transition==255)
  assert m[0x9850]==weight(bytearray(m[0:65536]),0xC0DB)[0] and bytes(m.banks[6][0xA8F:0xF18])==script
  counts[str(event)]+=1;counts['w_to_4200']+=exit_to_4200;counts['w_without_ship_returns']+=bool(w_calls and not exit_to_4200);messages.update(observed)
 # Проверка каждого байта статуса, границ двух штрафов и обеих кодировок количества.
 for status in range(256):
  for credits in (0,49,50,999,1000,65535):execute(15,status,credits,(status*73)&255)
 # Поиск всех шестнадцати размеров текущего ключа по исходному независимому алгоритму.
 keys={}
 for second in range(65536):
  keys.setdefault(signature(0x4B38,second,0)['size'],second)
  if len(keys)==16:break
 assert set(keys)==set(range(1,17))
 for unit,second in sorted(keys.items()):
  for credits in sorted({0,unit-1,unit,unit+1,5*unit-1,5*unit,5*unit+1,65535}):
   for seed in (0,255):execute(16,0,credits,seed,second)
  execute(16,0,unit,0,second,0)
 for seed in range(256):execute(17,0,65000,seed)
 report=dict(passed=True,cases_by_event_and_exit=dict(counts),queued_messages=dict(messages),all_status_bytes=True,
  actual_interpreter_and_original_script=True,independent_credit_status_equipment_and_weight_oracle=True,
  equipment_explicit_indices_cleared=list(CLEARED),o32_writes_index31_beyond_first30=True,
  all_key_sizes_1_to_16=True,transition_threshold_credits_le_unit=True,ordinary_charge_is_five_times_unit=True,
  actual_w_executed=True,native_transition_code_4200_not_executed=True,script_bytes_unchanged=True,
  station_display_not_executed=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StationScriptsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

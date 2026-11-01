"""Ограниченные полные проходы MainLoop, реальные LANG, рисователи, опросы и немузыкальный IM2."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckStationInterrupt import InterruptPorts
from CheckWorldSignature import signature
from skoolkit.simutils import PC,SP,I,IFF,IM


def main():
 _,_,base=make_context();lang=payload(5);base[6][:len(lang)]=list(lang);flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));boot=next(g for g in flow if g['name']=='StationBoot');loader=[i for i in boot['instructions'] if 0x4257<=i['address']<0x4278];items=json.loads((ROOT/'Tools/Disasm/Reports/InterfaceItems.json').read_text('utf-8'));counts=collections.Counter();summaries=[]
 def execute(status,credits,page,periodic,schedule,pulse=True,owned=255):
  f=Fixture(base,page=page);m=f.memory;s=f.sim;r=s.registers
  # Подготовка изменяемых индексов выполняется исходным фрагментом загрузчика, копируемые инструкции сверены по диску.
  source=payload(4)
  for instruction in loader:
   data=bytes.fromhex(instruction['hex']);assert data==source[instruction['offset']:instruction['offset']+len(data)];put(m,instruction['address'],data)
  s.run(start=0x4257,stop=0x4278)
  for item in items:
   draw=item['values'][11];assert m[draw+1]+256*m[draw+2]==item['index']
  for index,rect in ((0,(0,0,32,5)),(1,(1,6,20,2))):p=0xF0FD+16*index;put(m,p,(*rect,0x80,m[p+5]))
  put(m,0xF3DE,bytes(512));put(m,0xF3DE,(0x35,0x7F,0xEE,0xA6,1,1));put(m,0x9CA6,(0xDE,0xF3));m[0x9CAA]=0;m[0x9E78]=0;m[0x9AD0]=0;m[0x65A8]=1;put(m,0x66E8,bytes(7));m[0x68EB]=0
  pressed=any(schedule);put(m,0x6307,(20,20) if pressed else (250,190));put(m,0x983F,(0x38,0x4B,0xF3,0x4A,0));m[0x984B]=status;m[0x9849]=owned;m[0x984A]=255;m[0x9851]=255
  put(m,0x984E,credits.to_bytes(2,'little'));put(m,0x9852,bytes(60));put(m,0x988E,bytes(30));m[0x98AC]=0x80;put(m,0x98F6,bytes(14));m[0x983B]=m[0x983C]=m[0x983D]=0;m[0x983E]=0x99 if pulse else 0;m[0x9B7E]=1 if pulse else 50;m[0x9A82]=0
  put(m,0x7FFE,(255,63));r[:]=f.initial;r[PC]=0x9A59;frames=0;irq=0;script_events=[];script_pending=None;expected_credit=credits;expected_status=status;last_code=0;branch=None;merge_expected=None;pending_hover=False;calls=collections.Counter();unit=signature(0x4B38,0x4AF3,0)['size']
  def wake(pc):
   nonlocal irq
   before=tuple(r[:28]);old_page=m.o7ffd;target=pc+1;bits=schedule[min(max(frames-1,0),len(schedule)-1)] if pc==0x9A87 else 0
   f.trace.inputs=InterruptPorts([tuple(m[a:a+2]) for a in range(0x99B6,0x99C2,2)],bits,0x5A)
   for _ in range(18000):
    s.run()
    if r[PC]==target:break
   else:raise AssertionError(('halt',hex(pc)))
   assert s.accept_interrupt(r,m,pc) and r[PC]==0x8181
   for _ in range(6000):
    if r[PC]==target:break
    assert r[PC]!=0xDB05;s.run()
   else:raise AssertionError(('irq_return',hex(pc),hex(r[PC])))
   assert tuple(r[:12])==before[:12] and tuple(r[16:24])==before[16:24] and r[SP]==before[SP] and r[I]==before[I] and r[IM]==2 and r[IFF]==1
   assert m.o7ffd==m[0x6306]==old_page and m[0x9C0D]+256*m[0x9C0E]==before[SP] and m[0x9C11]+256*m[0x9C12]==target
   irq+=1
  for steps in range(6000000):
   pc=r[PC]
   if pc==0x4200:break
   assert pc!=0x3FFF,('unexpected_main_return',status,credits)
   if pc==0x9A81:
    if frames:assert branch in (None,'empty','closed','dispatched')
    frames+=1
    if frames>len(schedule):break
    branch=None
   if pc==0xA91B:assert m[0xA9A9]==0x80;calls['market']+=1
   if pc==0x9A6C:assert m[0xA9A9]==0
   if pc==0x9C77:calls['rebuild']+=1
   if pc==0xC000 and m.o7ffd&7==6:
    event=m[0x983A];script_events.append(event);assert event in (15,16) and script_pending is None
    if event==15:
     if 48<=expected_status<64:expected_credit=max(0,expected_credit-50)
     elif expected_status>=64:expected_credit=max(0,expected_credit-1000);expected_status-=48
    else:expected_credit=0 if expected_credit<=unit else max(0,expected_credit-5*unit)
    script_pending=event
   if pc in (0x9A7C,0x9AB1):
    assert script_pending==(15 if pc==0x9A7C else 16)
    assert m[0x984E]+256*m[0x984F]==expected_credit and m[0x984B]==expected_status;script_pending=None
   # Перед границами вызовов задаются действительные callback, тела процедур не подменяются.
   if pc==0x9A88:put(m,0x9A89,periodic.to_bytes(2,'little'));calls['periodic']+=1
   if pc==0x9A8B:put(m,0x9A8D,(0x0D,0xF1));put(m,0x9A90,(0xEA,0xA6));pending_hover=True
   if pc==0xA6EA:calls['hover']+=1
   if pc==0x9A98:
    assert pending_hover and bytes(m[0x9A90:0x9A92])==bytes((0x58,0x9A));pending_hover=False
   if pc==0x9ACB:merge_expected=(((m[0x66EC]|m[0x6585])<<1)|(m[0x66ED]|m[0x658A]))&255
   if pc==0x9ACE:assert r[0]==merge_expected
   if pc==0x9AD5:
    current=merge_expected;assert r[0]==r[3]==current and r[4]==last_code and m[0x9AD0]==current
    branch='empty' if not(current|last_code) else ('close' if current<last_code else 'dispatch');last_code=current
   if pc==0x9ADE:assert branch=='close';branch='closed';calls['close']+=1
   if pc==0x9AE4:assert branch=='dispatch';branch='dispatched';calls['dispatch']+=1
   if pc==0x7F1A:calls['status_action']+=1
   if m[pc]==0x76:wake(pc)
   else:s.run()
  else:raise AssertionError(('instruction_limit',status,credits,hex(periodic),schedule,hex(r[PC])))
  exited=r[PC]==0x4200
  assert calls['market']==1 and script_events[0]==15 and m[0xA9A9]==0 and m[0x984E]+256*m[0x984F]==expected_credit and m[0x984B]==expected_status
  if not exited:assert frames==len(schedule)+1 and r[SP]==0x7FFE and bytes(m[0x7FFE:0x8000])==bytes((255,63)) and m.o7ffd==m[0x6306]==0x10 and script_pending is None
  else:assert script_pending==16 and owned!=255 and expected_credit==0
  assert bool(16 in script_events)==pulse and calls['hover']==calls['periodic']
  counts['bounded_original_main_runs']+=1;counts['native_im2_in_model']+=irq;counts['copied_transition_4200_boundaries']+=exited;counts.update(calls)
  summaries.append(dict(status=status,credits=credits,page=page,periodic=periodic,input_schedule=list(schedule),pulse=pulse,owned=owned,script_events=script_events,irqs=irq,instructions=steps,exit_4200=exited,final_credits=expected_credit,calls=dict(calls)))
 for page in (0x10,0x18):
  for status in (0,55,80):
   for periodic in (0x9A58,0x68EA,0x7F35):execute(status,2000,page,periodic,(0,16,16,0) if status==0 else (0,0,0))
 for status in (0,55,80):execute(status,2000,0x10,0x9A58,(0,0),False)
 for page in (0x10,0x18):
  for owned in (255,0):execute(0,0,page,0x9A58,(0,0),True,owned)
 report=dict(passed=True,cases_by_path=dict(counts),runs=summaries,actual_market_rebuild_status_counter_scripts_and_input=True,
  real_im2_including_unblocked_pointer_path=True,physical_irq_return_pc_and_sp_checked=True,real_boot_draw_index_fragment_executed=True,
  callbacks_assigned_at_call_boundaries=True,callback_bodies_not_stubbed=True,mouse_disabled=True,music_disabled=True,
  interrupts_only_at_halts=True,continuous_hardware_interrupt_timing_not_proved=True,independent_script_money_and_input_branch_oracle=True,
  independent_whole_game_bitmap=False,action_4200_code_not_executed=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MainLoopExecutionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in report.items() if k!='runs'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

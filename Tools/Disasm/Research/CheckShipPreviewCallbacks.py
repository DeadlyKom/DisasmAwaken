"""Контракты ветвей корабельного просмотра, исходные помощники и настоящее IM2-пробуждение HALT."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckWorldSignature import logical_flags
from CheckSignedMultiply import sbc16_flags
from PreviewEdgeRasterOracle import arithmetic
from CheckInsetFrame import bitmap_address
from skoolkit.simutils import PC,SP,I,IFF,IM


def main():
 _,_,base=make_context();raw=payload(6);base[4][:len(raw)]=list(raw);counts=collections.Counter();cases=[]
 # Проверка всех комбинаций двух ненулевых байтов отложенного запроса и занятого элемента, рисование не начинается.
 f=Fixture(base);m=f.memory;s=f.sim;r=s.registers;initial=f.initial;before=[bytes(b) for b in m.banks]
 for pending in range(1,256):
  for active in range(1,256):
   m[0x68EB]=pending;m[0x9E78]=active;r[:]=initial;s.run(start=0x68EA,stop=0x3FFF)
   assert (r[0],r[1],r[SP])==(active,logical_flags(active),0x8000)
   assert r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and m[0x68EB]==pending and not f.trace.writes
   counts['busy_deferred_returns']+=1
 # Проверка полного допустимого диапазона слов последнего обработчика, старший байт 1 принадлежит ограничителю списка.
 m[0x68EB]=m[0x9E78]=0
 for last in range(65536):
  if last>>8==1 or last==0x6877:continue
  put(m,0xF3DE,last.to_bytes(2,'little')+bytes((1,1)));r[:]=initial;s.run(start=0x68EA,stop=0x3FFF)
  value=(last-0x6877)&65535;flags=sbc16_flags(last,0x6877,0)
  assert tuple(r[:8])==(last>>8,flags,initial[2],initial[3],0x68,0x77,value>>8,value&255)
  assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000 and not f.trace.writes
  counts['last_handler_mismatch_returns']+=1
 # Проверка условного рисования при отсутствии точного указателя, равный индекс чужого обработчика не подходит.
 for last in range(65536):
  if last>>8==1 or last==0x6877:continue
  put(m,0xF3DE,last.to_bytes(2,'little')+bytes((1,1)));r[:]=initial;s.run(start=0x6870,stop=0x3FFF)
  assert tuple(r[:8])==(1,int(last<0x6877),initial[2],initial[3],0x68,0x77,initial[6],initial[7])
  assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000 and not f.trace.writes
  counts['missing_exact_preview_pointer_returns']+=1
 for flags in range(256):
  put(m,0xF3DE,(1,1));r[:]=initial;r[1]=flags;s.run(start=0x6870,stop=0x3FFF)
  assert (r[0],r[1])==(1,flags&1) and r[6:8]==initial[6:8] and r[SP]==0x8000
  counts['empty_list_pointer_returns']+=1
 # Проверка отсутствия побочных записей вне явно меняемых фикстурой слов и подставленного CALL GetLastDraw.
 allowed={0x68EB,0x9E78,*range(0xF3DE,0xF3E6),*range(0x7FFA,0x7FFE)}
 for bank,(old,new) in enumerate(zip(before,m.banks)):
  for index,(a,b) in enumerate(zip(old,new)):
   if a!=b:assert bank==5 and 0x4000+index in allowed or bank==2 and 0x8000+index in allowed or bank==0 and 0xC000+index in allowed,(bank,index,a,b)
 # Проверка временного RET выключенной панели без чтения индекса, все регистры и память сохраняются.
 f=Fixture(base);m=f.memory;m[0x6877]=0xC9;before_disabled=[bytes(b) for b in m.banks]
 for flags in range(256):
  f.sim.registers[:]=f.initial;r=f.sim.registers;r[1]=flags;f.sim.run(start=0x6877,stop=0x3FFF)
  assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
  assert [bytes(b) for b in m.banks]==before_disabled;counts['disabled_preview_returns']+=1
 entries=json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_text('utf-8'))
 addresses={x['name']:x['address'] for x in entries if x['region']=='Station'};begin=addresses['BeginScreenUpdate'];end=addresses['EndScreenUpdate'];fill=addresses['FillWindowBody']
 def draw(selector,model,rect,page,flags,fill_mode):
  f=Fixture(base,selector,model,rect,page,flags);m=f.memory;m[0x99B4]=fill_mode;observed=[];valid=rect[2]>=4 and rect[3]>=4
  def observe(f,pc):
   m=f.memory;r=f.sim.registers
   if pc==0xE13C and m.o7ffd&7==4:
    # Расчёт физических пределов по действительным Width=AEB3 и Height=AEAB, прямоугольники не квадратные.
    expected=(((8*rect[3]-11-14)&255)<<8)|((8*rect[2]-4-13)&255)
    assert r[6]*256+r[7]==expected and r[4]*256+r[5]==0 and r[0]==selector
    assert r[20]*256+r[21]==(((rect[1]<<8)|rect[0])*8)&65535
    assert m[0x9A89]+256*m[0x9A8A]==(0x68EA if valid else 0x9A58);observed.append('setup')
   if pc==0xE07F and m.o7ffd&7==4:assert r[0]==selector;observed.append('frame')
  result=f.run(0x6877,observe);r=f.sim.registers;expected_page=(page&0xF8)|0x10
  assert observed==(['setup','frame'] if valid else ['setup']) and result['wakes']==(2 if valid else 1)
  assert (r[0],r[1],m.o7ffd,m[0x6306],r[I],r[IFF],r[IM])==(expected_page,logical_flags(expected_page),expected_page,expected_page,0x80,1,2)
  if not valid:
   # Расчёт C из фактического последнего SUB Height-14, основная геометрия перед E13C подтверждена выше.
   _,input_flags=arithmetic((8*rect[3]-11)&255,14,True)
   assert (r[6]*256+r[7],r[4]*256+r[5],r[2],r[3])==(0,0x9A58,(selector-1)&255,input_flags)
  counts['preview_draws']+=1;counts['irq_wakeups']+=result['wakes'];counts['initial_frames']+=valid;cases.append(dict(kind='draw',selector=selector,model=model,rectangle=rect,page=page,flags=flags,fill_mode=fill_mode))
  return f
 # Проверка двух списков всех исходных моделей, остальных селекторов, двух геометрий, полос и экранов.
 for selector,count in ((0,7),(1,4),(2,7),(255,7)):
  for model in range(count):
   for rect in ((1,1,16,12),(1,1,2,3)):
    for flags in (0,1):
     for page in (0x10,0x18):draw(selector,model,rect,page,flags,model&1)
 # Проверка реального периодического кадра после подготовки его окна тем же исходным рисователем.
 for selector,count in ((0,7),(1,4)):
  for model in range(count):
   f=draw(selector,model,(3,2,24,18),0x10,1,model&1);m=f.memory;r=f.sim.registers;r[:]=f.initial;put(m,0x7FFE,(255,63));f.wakes=0;events=[];state={}
   def observe(f,pc):
    m=f.memory;r=f.sim.registers
    if pc==begin:state['screen']=bytes(m.banks[5][:6912]);events.append('begin')
    elif pc==fill:
     state['filled']=bytearray(m.banks[5][:6912]);value=0 if m[0x99B4]&1 else 255
     for row in range(8*(18-3)):
      address=bitmap_address(8*(2+2)+row,3+1)-0x4000;state['filled'][address:address+22]=bytes([value])*22
     events.append('fill')
    elif pc==0x68FF:assert bytes(m.banks[5][:6912])==bytes(state['filled'])
    elif pc==0xE07F and m.o7ffd&7==4:assert r[0]==selector;state['triangle']=m[0xF2B7];events.append('frame')
    elif pc==0x690A:
     triangle=state['triangle']^0x60;assert (r[0],r[1])==(triangle,logical_flags(triangle));state['frame_regs']=tuple(r[:28])
    elif pc==end:
     assert bytes(m.banks[7][:6912])==state['screen'] and m.o7ffd==0x18;events.append('end')
   result=f.run(0x68EA,observe)
   assert events==['begin','fill','frame','end'] and result['wakes']==1 and (r[0],r[1],m.o7ffd,m[0x6306],m[0x9B16])==(0x10,logical_flags(0x18),0x10,0x10,0)
   assert tuple(r[2:12])==state['frame_regs'][2:12] and tuple(r[18:24])==state['frame_regs'][18:24]
   counts['periodic_frames']+=1;counts['irq_wakeups']+=result['wakes']
 # Проверка отложенного обновления с отсутствующей либо присутствующей панелью описания и изменением порядка списка.
 for selector in (0,1):
  for description in (False,True):
   for preview in ('active','disabled','alias'):
    f=Fixture(base,selector);m=f.memory;r=f.sim.registers;pointer=0x5F00 if preview=='alias' else 0x6877
    if preview=='disabled':m[0x6877]=0xC9
    if preview=='alias':put(m,0x5F00,(0x21,26,0))
    list_items=[pointer,0x67E0]+([0x6945] if description else [])
    put(m,0xF3DE,b''.join(v.to_bytes(2,'little') for v in list_items)+bytes((1,1)));m[0x68EB]=255;m[0x9E78]=0;events=[]
    def observe(f,pc):
     if pc in (begin,0x67E0,0x6945,0x6877,end):events.append(pc)
    result=f.run(0x68EA,observe)
    assert events==[begin,0x67E0]+([0x6945] if description else [])+([0x6877] if preview!='alias' else [])+[end]
    wanted=[0x67E0]+([0x6945] if description else [])+[pointer]
    assert bytes(m[0xF3DE:0xF3DE+2*len(wanted)+2])==b''.join(v.to_bytes(2,'little') for v in wanted)+bytes((1,1))
    expected_flags=logical_flags(0x18) if preview=='active' else 0x50 if preview=='disabled' else 1
    assert m[0x68EB]==0 and m[0x9A89]+256*m[0x9A8A]==(0x68EA if preview=='active' else 0x9A58) and m.o7ffd==m[0x6306]==0x10 and (r[0],r[1])==(0x10,expected_flags)
    assert result['wakes']==1+int(description)+2*(preview=='active') and m[0x9B16]==0
    counts['deferred_refreshes']+=1;counts['deferred_'+preview]+=1;counts['irq_wakeups']+=result['wakes']
 report=dict(passed=True,cases_by_path=dict(counts),all_11_original_models=True,selectors=[0,1,2,255],both_screen_pages=True,both_caption_flags=True,both_fill_modes=True,
  all_allowed_last_handler_words_except_real_preview=True,all_nonzero_pending_and_active_byte_pairs=True,
  disabled_ret_preserves_all_context=True,same_item_key_alias_not_accepted_as_exact_preview_pointer=True,
  real_banks_and_all_graphics_helpers=True,real_boot_im2_vector_and_original_isr=True,irq_registers_stack_bank_and_screen_restored=True,
  irq_only_at_halt_boundaries=True,pointer_update_blocked_during_irq=True,music_disabled=True,independent_whole_preview_bitmap_oracle=False,independent_window_fill_bitmap_checked=True,
  exact_preview_hl_limits_from_textwindow_height_and_width=True,final_main_context_checked_by_composition=True,
  all_final_numeric_registers_from_independent_oracle=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShipPreviewCallbacksVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

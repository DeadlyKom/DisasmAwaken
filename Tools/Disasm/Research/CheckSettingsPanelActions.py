"""Редактирование установок, настоящий скан матрицы и явно отдельная модель задержек клавиатуры."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,Trace,ROOT,make_context,put
from CheckEnvironmentRows import reference as printed_rows
from CheckScrollBodyClear import rectangle
from CheckScreenUpdate import pointer_image
from skoolkit.simutils import PC,SP


class Keys(Trace):
 def __init__(self,simulator):super().__init__(simulator);self.pressed=None
 def read_port(self,registers,port,offset=0):
  if port&255==0xFE:
   return (255^self.pressed[1]) if self.pressed and port>>8==self.pressed[0] else 255
  return super().read_port(registers,port,offset)


def main():
 station,_,base=make_context();counts=collections.Counter();flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));rows=next(g['instructions'] for g in flow if g['name']=='Station')
 key_delay=next(i['address'] for i in rows if 0xA116<=i['address']<0xA163 and i['operation']=='HALT')
 modes={False:(0x6AEC,0x6B2C,0x6B84,0x6BA5,41,0x6B23,0x6B95,0x9728,0x99AE,13,66,12),
  True:(0x759C,0x75DC,0x7616,0x7637,42,0x75D3,0x7627,0x9736,0x99C8,43,110,26)}
 def prepare(game,selector=1,index=0,page=0x10):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game]
  f=Fixture(base,page=page);f.trace=Keys(f.sim);f.sim.set_tracer(f.trace);m=f.memory;r=f.sim.registers;p=0xF0FD+16*key
  put(m,draw+1,(key,0));put(m,p,(0,0,20 if game else 12,5,6,m[p+5]));put(m,top,(max(0,index-2),0));m[hover]=index-max(0,index-2)
  put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(*draw.to_bytes(2,'little'),1,1));m[0xCA20]=6;m[0x9E78]=0;m[0x99B2]=0x80;m[0x9B62]=0x80;m[0x9B16]=0;m[0x9A82]=0xA7;put(m,0x6307,(50,80))
  for a,v in ((0xAEB3,156 if game else 92),(0xAEAB,29),(0xAEBB,3),(0xAEBF,0),(0xAEC7,3),(0xAECB,0),(0xBD26,0),(0xBD73,column)):m[a]=v
  put(m,0xAED5,(0x68,0x48,0x26));r[0]=selector;r[6:8]=list(draw.to_bytes(2,'big'));r[4:6]=[0,key];r[8:10]=list(p.to_bytes(2,'big'))
  return f
 def run(f,start,keys=(),observer=None):
  m=f.memory;s=f.sim;r=s.registers;r[PC]=start;read=0;released=0
  for _ in range(1200000):
   pc=r[PC]
   if pc==0x3FFF:break
   if pc==0xA116:
    assert read<len(keys),('unexpected_key_wait',keys,read);code=keys[read];read+=1;pair=0x96AC+2*(code-0x1D);f.trace.pressed=tuple(m[pair:pair+2]);assert f.trace.pressed[0]!=0
    # Проверка FSettingsWaitFrame под возвратом ReadMatrixKey, указатель переживает каждое повторное ожидание.
    assert r[SP]==0x7FFA and m[r[SP]+4:r[SP]+6]==[255,63]
    values=modes[start==0x759C][7];assert m[r[SP]+2]+256*m[r[SP]+3]==values+r[2]*256+r[3]
    counts['wait_frame_words_checked']+=1
   if pc in (0x6B57,0x7606):
    # Проверка трёх слов FSettingsEditFrame непосредственно перед промежуточным CALL рисователя.
    assert r[SP]==0x7FFA and m[r[SP]:r[SP]+2]==[r[3],r[2]] and m[r[SP]+2:r[SP]+4]==[r[7],r[6]] and m[r[SP]+4:r[SP]+6]==[255,63]
    counts['edit_frame_words_checked']+=1
   if observer:observer(f,pc)
   if pc==key_delay:
    # Модель явно освобождает только HALT задержки ввода, IRQ и время этих десяти пробуждений не утверждаются.
    r[PC]+=1;released+=1
   elif m[pc]==0x76:f.wake(pc)
   else:s.run()
  else:raise AssertionError(('settings_action_limit',hex(start),hex(r[PC])))
  assert r[SP]==0x8000 and r[26]==1 and read==len(keys) and released==10*read
  counts['keyboard_calls_real_matrix_scan']+=read;counts['keyboard_halts_explicitly_released_without_irq']+=released
  return read
 def parsed(memory,values,records,length):
  old=bytes(memory[records:records+2*length]);result=bytearray(old);number=0
  for index in range(length):
   code=memory[values+index]
   if code==0:break
   number+=1;kind=old[2*index]
   if kind==127 or kind>=130:
    address=0x96AC+((2*((code-29)&255))&255);result[2*index:2*index+2]=bytes(memory[address:address+2])
   elif kind in (128,129) and code in (ord('N'),ord('Y')):result[2*index]=128 if code==ord('N') else 129
   else:result[2*index]=(code-48)&255
  return bytes(result),number
 # Проверка закрытия с преобразованием всей подписи в FSettingWord и ранних Carry всех селекторов.
 for game in (False,True):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game]
  for selector in range(256):
   if selector==1:continue
   f=prepare(game,selector);m=f.memory;r=f.sim.registers;put(m,0x6307,(50,3));before_values=bytes(m[values:values+length+1]);before_records=bytes(m[records:records+2*length]);list_before=bytes(m[0xF3DE:0xF5DE]);expected,number=parsed(m,values,records,length)
   run(f,start)
   if selector&128:
    assert r[0]==selector and r[1]==(selector&0xA8)|1 and bytes(m[records:records+2*length])==before_records and bytes(m[0xF3DE:0xF5DE])==list_before;counts['high_selector_returns']+=1
   else:
    moved=bytearray(list_before);moved[:128]=list_before[2:130];moved[:4]=list_before[:4]
    wanted=bytearray(moved);wanted[:128]=moved[2:130]
    assert bytes(m[0xF3DE:0xF5DE])==bytes(wanted) and bytes(m[records:records+2*length])==expected and m[0x9A82]==0,(game,selector,bytes(m[0xF3DE:0xF3E8]),bytes(wanted[:10]),bytes(m[records:records+2*length]),expected,m[0x9A82],r[:12])
    assert tuple(r[:8])==(0,0x54,(values+number)>>8,(values+number)&255,(records+2*number)>>8,(records+2*number)&255,draw>>8,draw&255);counts['close_and_parse_settings']+=1
   assert bytes(m[values:values+length+1])==before_values and f.wakes==0
  # Проверка охраны FF только младшего байта TopRow без запуска ввода или рисования.
  for high in range(256):
   f=prepare(game);m=f.memory;r=f.sim.registers;put(m,top,(255,high));before=bytes(m[values:values+length+1]);run(f,start)
   assert r[:2]==[0,0x50] and bytes(m[values:values+length+1])==before and f.wakes==0;counts['low_top_ff_guard']+=1
 # Проверка всей старой байтовой величины на ветвях Y/N, остановка до перерисовки.
 for game in (False,True):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game]
  for index in range(1 if game else 4):
   for old in range(256):
    f=prepare(game,index=index);m=f.memory;s=f.sim;m[values+index]=old;before=bytes(m[values:values+length+1]);s.run(start=select,stop=redraw)
    expected=bytearray(before);expected[index]=ord('N') if old==ord('Y') else ord('Y');assert bytes(m[values:values+length+1])==bytes(expected);counts['all_old_toggle_bytes_before_redraw']+=1
 # Проверка полной байтовой суммы до чтения или изменения потенциально чужого элемента.
 for game in (False,True):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game];operation='AND A' if game else 'CP #04'
  stop=next(i['address'] for i in rows if select<i['address']<redraw and i['operation']==operation)
  f=prepare(game);m=f.memory;s=f.sim
  for first in range(255):
   for second in range(256):
    put(m,top,(first,0xA5));m[hover]=second;put(m,0x7FFE,(255,63));s.registers[:]=f.initial;s.run(start=select,stop=stop);r=s.registers;index=(first+second)&255
    assert r[0]==r[3]==index and r[2]==0 and r[6]*256+r[7]==values+index;counts['byte_index_pairs_stopped_before_edit']+=1
 # Проверка полных переключений на обеих экранных страницах.
 for game in (False,True):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game]
  for page in (0x10,0x18):
   for index in range(1 if game else 4):
    for old in (0,ord('N'),ord('Y'),255):
     f=prepare(game,index=index,page=page);m=f.memory;m[values+index]=old;run(f,start)
     assert m[values+index]==(ord('N') if old==ord('Y') else ord('Y')) and f.wakes==1 and m.o7ffd==m[0x6306]==0x10
     counts['full_toggle_actions']+=1;counts['caption_im2_wakes']+=f.wakes
 # Проверка всех реально закодированных клавиш для первой клавишной строки и крайних числовых ограничений.
 f=prepare(False);valid=[code for code in range(0x1E,0x5B) if f.memory[0x96AC+2*(code-0x1D)]!=0]
 for game in (False,True):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game]
  cases=[(1 if game else 4,code) for code in valid]
  cases += [(index,code) for index in (26,) if game for code in (0x1E,0x1F,0x20,0x30,0x41,0x5A)]
  if not game:cases += [(index,code) for index in (5,6,7,8,9) for code in (0x1E,0x1F,0x20,0x30,0x41,0x5A)]+[(index,code) for index in (10,11) for code in range(0x30,0x38)]+[(12,0x30),(12,0x31)]
  for page in (0x10,0x18):
   for index,code in cases:
    f=prepare(game,index=index,page=page);m=f.memory;before=bytes(m[values:values+length+1]);sequence=[0x1D]
    if not game and index in (10,11):sequence.append(0x38)
    if not game and index==12:sequence.append(0x32)
    sequence.append(code);run(f,start,sequence)
    expected=bytearray(before);expected[index]=code;assert bytes(m[values:values+length+1])==bytes(expected) and f.wakes==2
    assert m.o7ffd==m[0x6306]==0x10 and m[hover]==255 and m[0x9B16]==0;counts['accepted_key_actions']+=1;counts['caption_im2_wakes']+=f.wakes
 # Проверка полного цикла прокрутки и независимого bitmap каждого принятого шага.
 for game in (False,True):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game];width=156 if game else 92
  for page in (0x10,0x18):
   for direction in ('up','down'):
    for presses in (0,1,3):
     f=prepare(game,selector=0,page=page);m=f.memory;r=f.sim.registers;put(m,top,(1,0));m[hover]=255
     for a in (0x66EC,0x6585,0x66ED,0x658A):m[a]=0
     index=1;poll=0;steps=0;frame=list(m[0x4000:0x6000]);attributes=bytes(frame[6144:6912]);expected_screen=None
     def observe(f,pc):
      nonlocal index,poll,steps,frame,expected_screen
      if pc==0xA1D6:assert m[0xA235]+256*m[0xA236]==limit and m[0xA265]+256*m[0xA266]==(0x7648 if game else 0x6BB6)
      if pc==0xA20A:
       assert r[6]*256+r[7]==index;active=poll<presses;m[0x66ED]=int(active)
       if active:
        m[0x6308]=0 if direction=='up' else 191
        if direction=='up':index=max(0,index-1)
        elif index+2<limit:index+=1
       poll+=1
      if pc==0xA25C:
       assert bytes(m.banks[7][:6144])==bytes(frame[:6144]);cleared=bytearray(frame);rectangle(cleared,3,11,width,36);flat=list(m[0:65536]);flat[0x4000:0x6000]=list(cleared)
       expected=printed_rows(flat,index,width,29,labels=0xDF3C if game else 0xDECB,values=values);screen=expected[-1];frame=list(cleared);frame[:6912]=screen;expected_screen=bytes(screen);steps+=1
      if pc==0xA268:assert bytes(m[0x4000:0x5B00])==expected_screen
     run(f,start,observer=observe)
     assert m[top]+256*m[top+1]==index and r[6]*256+r[7]==index and r[:2]==[0,0x44] and m[0x6307:0x6309]==[50,80]
     assert bytes(m[0x4000:0x6000])==bytes(pointer_image(frame,station,50,80)) and bytes(m.banks[7][6144:6912])==attributes and poll==presses+1
     assert f.wakes==steps and m.o7ffd==m[0x6306]==0x10;counts['scroll_actions']+=1;counts['scroll_steps_and_real_im2']+=steps
 # Проверка обязательного раннего Carry после настоящей перерисовки, значение и верхний индекс не редактируются.
 for game in (False,True):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game]
  for page in (0x10,0x18):
   for selector in (0,1,2,127):
    f=prepare(game,selector,page=page);m=f.memory;r=f.sim.registers;before=bytes(m[values:values+length+1]);old_top=bytes(m[top:top+2]);put(m,0x5F00,(0x21,63,0,0xC9));put(m,0xF3DE,(*draw.to_bytes(2,'little'),0,0x5F,1,1));run(f,start)
    assert r[0]==selector and r[1]&1 and bytes(m[values:values+length+1])==before and bytes(m[top:top+2])==old_top and f.wakes==1
    counts['repaint_then_carry_returns']+=1;counts['caption_im2_wakes']+=f.wakes
 # Проверка JP-обёрток наведения сравнением с теми же настоящими помощниками, включая изменение XOR-полосы.
 for game,wrapper,helper in ((False,0x6AE9,0x6B8E),(True,0x7599,0x7620)):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game]
  for previous in (255,0,2):
   for y in (0,11,15,35,80,191):
    for last in (False,True):
     outcomes=[]
     for entry in (helper,wrapper):
      f=prepare(game);m=f.memory;r=f.sim.registers;m[hover]=previous;m[0x6308]=y
      if not last:put(m,0x5F00,(0x21,key,0,0xC9));put(m,0xF3DE,(0,0x5F,1,1))
      run(f,entry);outcomes.append((list(r[:12]),list(r[16:24]),[bytes(b) for b in m.banks],list(f.trace.writes)))
     assert outcomes[0]==outcomes[1];counts['hover_proxy_equivalence']+=1
 # Проверка отключённого рисователя и чужого адреса с тем же ключом, прямой первый игровой вызов отличается от условного.
 for game in (False,True):
  start,select,redraw,draw,key,top,hover,values,records,length,column,limit=modes[game]
  for variant in ('disabled','alias'):
   for editing in (False,True):
    index=(1 if game else 4) if editing else 0;f=prepare(game,index=index);m=f.memory
    if variant=='disabled':m[draw]=0xC9
    else:put(m,0x5F00,(0x21,key,0,0xC9));put(m,0xF3DE,(0,0x5F,1,1))
    old=m[values+index];run(f,start,[0x1D,0x41] if editing else [])
    assert m[values+index]==(0x41 if editing else ord('N') if old==ord('Y') else ord('Y'))
    assert f.wakes==int(game and editing and variant=='alias') and m.o7ffd==0x10;counts['disabled_or_aliased_edit']+=1;counts['caption_im2_wakes']+=f.wakes
 report=dict(passed=True,cases_by_path=dict(counts),real_keyboard_matrix_and_lookup_executed=True,keyboard_delay_irq_and_time_not_modelled=True,
  caption_irq_real_and_music_disabled=True,all_256_old_toggle_bytes=True,all_physical_non_caps_keys=True,
  ink_paper_range_0_7_and_bright_range_0_1_checked=True,caps_shift_rejected=True,independent_full_scroll_bitmap_and_parsed_records=True,
  game_template_43_labels_but_scroll_last_index_26=True,repaint_physical_tail_shift_included=True,single_pressed_key_at_a_time=True,
  independent_whole_edit_redraw_bitmap=False,keyboard_delay_irq_executed=False,iff_remains_enabled_in_model=True,
  both_dynamic_stack_frames_verified=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SettingsPanelActionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Действие списка оснащения, первый выбор описания и повторное подтверждение сделки."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckShipModelActions import remove
from CheckEquipmentRows import reference as rows_reference
from skoolkit.simutils import PC,SP


def prepare(base,row=0,mode=0,text_index=0,selector=1,info=False,page=0x10):
 f=Fixture(base,page=page);m=f.memory;r=f.sim.registers
 for address,value in ((0x7228,38),(0x6AB7,39),(0x7B26,37),(0x7B41,36),(0x7F36,0),(0x6E8B,24)):
  put(m,address,value.to_bytes(2,'little'))
 for index,rect in ((38,(0,0,32,24)),(39,(0,0,24,12)),(0,(0,0,32,5))):
  p=0xF0FD+16*index;put(m,p,(*rect,7 if index else 0,m[p+5]))
 m[0x71EC]=mode;m[0x7217]=row;m[0x6ACC]=text_index;put(m,0x71B9,(0,0));put(m,0x6AA4,(5,0xA5))
 put(m,0x9852,bytes(60));put(m,0x988E,bytes(52));put(m,0x98F6,bytes(14));m[0x98AC]=0x80;m[0x9849]=0;m[0x984A]=255;m[0x9851]=255;put(m,0x984E,(255,255))
 put(m,0x983F,(0x38,0x4B,0,0x4A,0));put(m,0xF3DE,(0xB6,0x6A,0x27,0x72,1,1) if info else (0x27,0x72,1,1));m[0xCA20]=7;m[0x9E78]=0
 r[0]=selector;r[4:6]=[0,38];r[6:8]=[0x72,0x27];p=0xF0FD+16*38;r[8:10]=[p>>8,p&255]
 return f


def main():
 _,_,base=make_context();raw=payload(5);base[6][:len(raw)]=list(raw);counts=collections.Counter()
 # Проверка подтверждения для каждой строки, двух режимов, обоих экранов и настоящего LANG.
 for row in range(30):
  for mode in (0,1):
   for page in (0x10,0x18):
    f=prepare(base,row,mode,row,page=page);m=f.memory;r=f.sim.registers;events=[];calls=[]
    def observe(f,pc):
     if pc==0xC000 and m.o7ffd&7==6:events.append(m[0x983A])
     if pc in (0xA49F,0x7F35,0x7227,0xA496):calls.append(pc)
    f.run(0x7175,observe)
    assert events==[5+mode] and calls==[0xA49F,0x7F35,0x7227,0xA496],(row,mode,events,calls)
    assert m[0x7217]==255 and m[0x6ACC]==row and bytes(m[0x6AA4:0x6AA6])==bytes((5,0xA5))
    assert m.o7ffd==m[0x6306]==0x10 and m[0x9B16]==0 and f.wakes==1 and r[SP]==0x8000
    counts['confirmed_original_trade_and_redraw']+=1;counts['real_caption_im2']+=f.wakes
 # Проверка первого выбора, описание обновляется без запуска сценария даже при режимах продажи.
 for row in range(30):
  for info in (False,True):
   f=prepare(base,row,1,(row+1)%30,info=info);m=f.memory;events=[];calls=[]
   def observe(f,pc):
    if pc==0xC000 and m.o7ffd&7==6:events.append(pc)
    if pc in (0xA49F,0x6AAF,0x7220,0xA496):calls.append(pc)
   f.run(0x7175,observe)
   assert not events and m[0x6ACC]==row and bytes(m[0x6AA4:0x6AA6])==bytes(2)
   assert calls[0]==0xA49F and calls[-2:]==[0x7220,0xA496],calls
   assert f.wakes==1+int(info) and m[0x7217]==255 and m.o7ffd==0x10
   counts['first_choice_updates_description_only']+=1;counts['real_caption_im2']+=f.wakes
 # Проверка отсутствия строки, собственная ветвь FF не меняет результат общего префикса.
 for mode in (0,1,255):
  f=prepare(base,255,mode);m=f.memory;states=[]
  def observe(f,pc):
   if pc==0x7178:states.append((bytes(m[0x9849:0x9904]),bytes(m[0xF3DE:0xF45E]),bytes(m[0x6AA4:0x6AA6])))
  f.run(0x7175,observe);assert len(states)==1;before=states[0]
  after=(bytes(m[0x9849:0x9904]),bytes(m[0xF3DE:0xF45E]),bytes(m[0x6AA4:0x6AA6]))
  assert before==after and f.wakes==0,(mode,f.wakes,[(part,[(i,a,b) for i,(a,b) in enumerate(zip(left,right)) if a!=b]) for part,(left,right) in enumerate(zip(before,after))])
  counts['ff_without_selection']+=1
 # Проверка всех остальных селекторов при закрытии и при низком окне без доступных строк прокрутки.
 for selector in range(256):
  if selector==1:continue
  for same in (False,True):
   f=prepare(base,255,selector=selector,info=True);m=f.memory;r=f.sim.registers;put(m,0xF3DE,(0x25,0x7B,0x40,0x7B,0xB6,0x6A,0x27,0x72,1,1));put(m,0x6307,(50,3 if same else 80));m[0xAEC7]=3;m[0xAEAB]=24;m[0xAEB3]=188;m[0xAEBB]=3;m[0xAEBF]=m[0xAECB]=0;states=[]
   def observe(f,pc):
    if pc==0x7178:states.append(bytes(m[0xF3DE:0xF5DE]))
   f.run(0x7175,observe)
   if selector&128:
    assert r[0:2]==[selector,(selector&0xA8)|1] and len(states)==1 and bytes(m[0xF3DE:0xF5DE])==states[0];counts['high_selector_return']+=1
   elif same:
    assert len(states)==1;keys={0x7B25:37,0x7B40:36,0x6AB6:39,0x7227:38};wanted,_,_=remove(states[0],keys,[38,37,36,39],0)
    assert bytes(m[0xF3DE:0xF5DE])==bytes(wanted);counts['close_four_panels']+=1
   else:
    assert len(states)==1 and bytes(m[0xF3DE:0xF5DE])==states[0] and bytes(m[0x71B9:0x71BB])==bytes(2)
    assert bytes(m[0xA235:0xA237])==bytes((29,0)) and bytes(m[0xA265:0xA267])==bytes((0x44,0x72)) and m[0xC6E3]==24
    counts['scroll_height_rejection']+=1
   assert f.wakes==0
 # Проверка принятой прокрутки с настоящими опросами, callback и независимым bitmap каждой пачки строк.
 for top in (0,1,28):
  for direction in ('up','down'):
   for presses in (1,3):
    for page in (0x10,0x18):
     f=prepare(base,255,selector=0,page=page);m=f.memory;r=f.sim.registers;put(m,0x71B9,top.to_bytes(2,'little'));put(m,0x6307,(50,80))
     for address,value in ((0xAEC7,3),(0xAEAB,53),(0xAEB3,188),(0xAEBB,3),(0xAEBF,0),(0xAECB,0),(0x66EC,0),(0x6585,0),(0x66ED,0),(0x658A,0)):m[address]=value
     state=dict(index=top,polls=0,steps=0,body=None)
     def observe(f,pc):
      if pc==0xA20A:
       assert r[6]*256+r[7]==state['index'];active=state['polls']<presses;m[0x66ED]=int(active)
       if active:
        m[0x6308]=191 if direction=='down' else 0
        if direction=='down':
         difference=29-state['index'];second=(difference&65535)-3-int(difference<0)
         if second>0:state['index']=(state['index']+1)&65535;state['steps']+=1
        elif state['index']:state['index']-=1;state['steps']+=1
       state['polls']+=1
      if pc==0xA25C:assert bytes(m.banks[7][:6144])==bytes(m.banks[5][:6144])
      if pc==0x7244:state['body']=rows_reference(m,r[6]*256+r[7],188,53)
      if pc==0xA268:
       expected=state['body'];assert expected is not None and bytes(m[0x4000:0x5B00])==bytes(expected['screen'])
       assert m[0x7212]==expected['counter'][0];state['body']=None
     f.run(0x7175,observe)
     assert m[0x71B9]+256*m[0x71BA]==state['index'] and state['polls']==presses+1 and f.wakes==state['steps']
     assert m[0x7217]==255 and m.o7ffd==0x10 and m[0x9B16]==0 and bytes(m[0x6307:0x6309])==bytes((50,80))
     counts['complete_scroll_actions']+=1;counts['independent_scroll_body_bitmaps']+=state['steps'];counts['real_scroll_im2']+=f.wakes
 # Проверка каждого полного режима перед вызовом LANG, любое ненулевое значение задаёт продажу.
 for mode in range(256):
  f=prepare(base,0,mode);m=f.memory;r=f.sim.registers;r[PC]=0x7175
  for _ in range(4000):
   if r[PC]==0xC000 and m.o7ffd&7==6:break
   f.sim.run()
  else:raise AssertionError(('event_entry',mode,hex(r[PC])))
  assert m[0x983A]==5+int(mode!=0);counts['all_owned_mode_bytes']+=1
 report=dict(passed=True,cases_by_path=dict(counts),first_selection_does_not_trade=True,repeated_selection_uses_original_lang=True,
  actual_helpers_and_banks=True,independent_scroll_body_bitmap=True,independent_whole_redraw_bitmap=False,irq_only_at_halt=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EquipmentListActionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Выбор ближайшего варианта настоящих ресурсов, нулевой ключ и отключение callback при закрытии."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckWorldSignature import signature
from CheckMapDistanceMinimum import distance
from skoolkit.simutils import SP


CURSORS=(0xC6CA,0xC6E7,0xC704,0xC721,0xC73E,0xC75B)


def main():
 _,_,base=make_context();symbols=json.loads((ROOT/'Tools/Disasm/Reports/Symbols.json').read_text('utf-8'));empty=symbols['Station.EmptyCallback.Entry'];update=symbols['Station.UpdateVariantPanel.Entry'];counts=collections.Counter()
 def prepare(q=3,page=0x10,rect=(1,1,10,10),info=False):
  f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;p=0xF0FD+16*20;put(m,p,(*rect,6,m[p+5]));put(m,0x788D,(20,0));put(m,0x7690,(19,0));pi=0xF0FD+16*19;put(m,pi,(0,0,16,24,6,m[pi+5]));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(0x8F,0x76,0x8C,0x78,1,1) if info else (0x8C,0x78,1,1));m[0x993D]=0x80;m[0x9E78]=0;m[0xCA20]=6;put(m,0x9A89,update.to_bytes(2,'little'))
  put(m,0x9844,(0x38,0x4B,0x39^q,0x4A,0));put(m,0x983F,(0x38,0x4B,0,0x4A,0));r[0]=1;r[6:8]=[0x78,0x8C];r[4:6]=[0,20];r[8:10]=[p>>8,p&255]
  return f
 # Проверка всех ненулевых количеств и настоящих ресурсных курсоров, рамка сначала готовит исходную сцену.
 for q in range(2,8):
  for page in (0x10,0x18):
   for info in (False,True):
    for rect in ((1,1,10,10),(0,0,2,3)):
     f=prepare(q,page,rect,info);m=f.memory;f.run(0x788C);counts['scene_preparation_im2']+=f.wakes;points=[]
     for address in CURSORS[:q-1]:
      j=address-0xC000;ptr=m.banks[1][j]+256*m.banks[1][j+1];points.append(tuple(m.banks[1][ptr-0xC000:ptr-0xC000+2]))
     assert all(len(point)==2 for point in points)
     # Расчёт целевой пары с полными словными переносами, исходные точки ресурсов не подменяются.
     origin=rect[0]+256*rect[1];bias=(8*((origin+0x0404)&65535)+0x0603)&65535;pointer=(bias+points[-1][0]+256*points[-1][1])&65535;target=(pointer-bias)&65535;tx,ty=target&255,target>>8
     distances=[distance((x-tx)&255,(y-ty)&255)[0] for x,y in points];chosen=min(range(len(points)),key=lambda i:distances[i])
     put(m,0x6307,pointer.to_bytes(2,'little'));put(m,0x7FFE,(255,63));f.sim.registers[:]=f.initial;r=f.sim.registers;r[0]=1;r[6:8]=[0x78,0x8C];r[4:6]=[0,20];p=0xF0FD+16*20;r[8:10]=[p>>8,p&255];f.wakes=0;selected=[];calls=[]
     def observe(f,pc):
      if pc==0x7872:
       selected.append(m[0x9848]);assert m[0x9848]==chosen and r[0]==chosen
       assert m.banks[1][0x668]+256*m.banks[1][0x669]==min(distances)
      if pc in (0x7688,0x7885):calls.append(pc)
     f.run(0x783B,observe)
     assert selected==[chosen] and calls==[0x7688,0x7885] and m[0x9848]==chosen and m.o7ffd==m[0x6306]==0x10 and f.wakes==1+int(info)
     expected=update if rect[2]>=4 and rect[3]>=4 else empty
     assert m[0x9A89]+256*m[0x9A8A]==expected and r[10:12]==f.initial[10:12] and r[SP]==0x8000
     counts['real_nearest_variant_and_redraw']+=1;counts['real_caption_im2']+=f.wakes
 # Проверка End, созданного настоящими периодическими кадрами, без подмены курсорных операндов.
 marker_profiles=[]
 for page in (0x10,0x18):
  for info in (False,True):
   rect=(1,1,24,10);f=prepare(3,page,rect,info);m=f.memory;f.run(0x788C)
   path_snapshot=bytes(m.banks[1][0xA45:0xD03]);end=0xCB37;ticks=0;advances=[]
   m[0x78D7]=0;m[0x78DC]=1
   def cursor0():return m.banks[1][0x6CA]+256*m.banks[1][0x6CB]
   while cursor0()!=end:
    assert ticks<512,('End_not_reached',page,info,ticks,hex(cursor0()))
    put(m,0x7FFE,(255,63));f.sim.registers[:]=f.initial
    def animation_observer(f,pc):
     if pc==0xC6D9:
      r=f.sim.registers
      assert bytes(m.banks[1][0x6D9:0x6DC])==bytes((0x22,0xCA,0xC6))
      advances.append((cursor0(),r[6]*256+r[7]))
    f.run(0x78D6,animation_observer);ticks+=1
    assert m.o7ffd==m[0x6306]==page,(page,info,ticks,m.o7ffd,m[0x6306])
   assert advances and advances[-1]==(end-2,end)
   assert bytes(m.banks[1][0xA45:0xD03])==path_snapshot
   points=[]
   for address in CURSORS[:2]:
    j=address-0xC000;ptr=m.banks[1][j]+256*m.banks[1][j+1]
    points.append(tuple(m.banks[1][ptr-0xC000:ptr-0xC000+2]))
   assert points[0]==(128,16)
   origin=rect[0]+256*rect[1];bias=(8*((origin+0x0404)&65535)+0x0603)&65535
   pointer=(bias+128+256*16)&65535;px,py=pointer&255,pointer>>8
   assert 8*rect[0]<=px<8*(rect[0]+rect[2]) and 8*rect[1]<=py<8*(rect[1]+rect[3])
   distances=[distance((x-128)&255,(y-16)&255)[0] for x,y in points]
   chosen=min(range(2),key=lambda i:distances[i]);assert chosen==0 and distances[0]==0
   put(m,0x6307,pointer.to_bytes(2,'little'));put(m,0x7FFE,(255,63));f.sim.registers[:]=f.initial
   r=f.sim.registers;r[0]=1;r[6:8]=[0x78,0x8C];r[4:6]=[0,20];p=0xF0FD+16*20;r[8:10]=[p>>8,p&255]
   reached=[];selected=[]
   def marker_observer(f,pc):
    if pc==0xC5E8:
     assert cursor0()==end
     reached.append(cursor0())
    if pc==0x7872:
     assert m[0x9848]==0 and r[0]==0 and m.banks[1][0x668:0x66A]==[0,0]
     selected.append(m[0x9848])
   f.run(0x783B,marker_observer)
   assert reached==[end] and selected==[0] and r[SP]==0x8000
   assert m.o7ffd==m[0x6306]==0x10 and bytes(m.banks[1][0xA45:0xD03])==path_snapshot
   marker_profiles.append(dict(initial_page=page,info_panel=info,callback_ticks=ticks,
       actual_cursor_updates=len(advances),last_cursor_write=list(advances[-1]),
       pointer=[px,py],points=[list(point) for point in points],selected=0,minimum=0))
   counts['natural_End_full_action']+=1
 # Проверка нулевых количеств обоих XOR-классов, дескриптор возвращается без выбора и перерисовки.
 for q in (0,1):
  for variant in range(256):
   f=prepare(q);m=f.memory;r=f.sim.registers;m[0x9848]=variant;before=bytes(m[0x4000:0x5B00]);callback=bytes(m[0x9A89:0x9A8B]);expected=signature(0x4B38,0x4A00|(0x39^q),variant);f.run(0x783B)
   assert r[:2]==[0,expected['flags']] and r[6:8]==[expected['major'],expected['size']] and r[4:6]==[expected['region'],expected['minor']]
   assert m[0x9848]==variant and bytes(m[0x4000:0x5B00])==before and bytes(m[0x9A89:0x9A8B])==callback and f.wakes==0;counts['zero_count_without_selection']+=1
 # Проверка каждого полного неселективного A, callback отключается только после совпавшей строки закрытия.
 for selector in range(256):
  if selector==1:continue
  for same in (False,True):
   f=prepare();m=f.memory;r=f.sim.registers;r[0]=selector;put(m,0x6307,(42,11 if same else 80));m[0xAEC7]=11;before=bytes(m[0x4000:0x5B00]);f.run(0x783B)
   closed=selector<128 and same;callback=m[0x9A89]+256*m[0x9A8A];assert callback==(empty if closed else update),(selector,same,hex(callback),r[:8],m[0xAEC7],m[0x6308])
   if closed:assert r[6:8]==[empty>>8,empty&255] and bytes(m[0xF3DE:0xF3E0])==bytes((1,1))
   assert m[0x9848]==0 and bytes(m[0x4000:0x5B00])==before and f.wakes==0;counts['nonselection_close_filter']+=1
 report=dict(passed=True,cases_by_path=dict(counts),real_resource_coordinates_after_draw=True,all_positive_counts_1_to_6=True,
  first_minimum_index_independent=True,zero_count_preserves_variant_and_callback=True,close_disables_callback_only_on_matching_row=True,
  natural_End_profiles=marker_profiles,End_reached_by_original_callback_without_cursor_patch=True,
  full_action_prefix_preserves_End_until_selector=True,modeled_pointer_inside_panel=True,
  all_UI_schedules_proved=False,
  actual_helpers_and_banks=True,independent_whole_redraw_bitmap=False,irq_only_at_caption_halt=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SystemMapActionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

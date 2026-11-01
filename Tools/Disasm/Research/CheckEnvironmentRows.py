"""CR-подписи и текущие значения среды, независимый счётчик, статусы и полный bitmap."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckTextStream import reference as stream
from CheckKeyLabel import reference as key_label,glyph
from CheckGlyphRenderer import compare_flags
from skoolkit.simutils import SP


def inc_flags(previous,carry=0):
 result=(previous+1)&255
 return (result&0xA8)|(64 if result==0 else 0)|(16 if previous&15==15 else 0)|(4 if previous==127 else 0)|carry


def reference(memory,top,width,height,origin=(3,3),bc=0x36C9,labels=0xDECB,values=0x9728):
 text=list(memory[labels:0x10000])+[10]*1024;offset=0
 for _ in range((top&255)+1):offset=text.index(13,offset)+1
 positions=[];columns=[memory[a] for a in (0xBD73,0xBD7E,0xBD89,0xBD94,0xBD9F)]
 _,x,y,a,f,_=stream(text[offset:],list(memory[0x8900:0x8A00]),0,8,width,height,0,columns,origin,bc>>8,positions=positions)
 screen=bytearray(memory[0x4000:0x5B00])
 for code,cx,cy in positions:glyph(memory,code,cx,cy,width,height,origin,screen)
 pointer=(values+top)&65535;y=8;count=0;counterflags=0x44;bc=values
 for _ in range(512):
  x=memory[0xBD73];code=memory[pointer]
  if code==0:return pointer,x,y,0,0x44,bc,top,count,counterflags,screen
  x,a,f,_=key_label(memory,code,x,y,width,height,origin,screen);pointer=(pointer+1)&65535;counterflags=inc_flags(count);count=(count+1)&255
  if not f&1 and a in (1,2):return pointer,x,y,0,0x42,bc,top,count,counterflags,screen
  next_y=(y+8)&255;bc=0x9700|height
  if next_y>=height:return pointer,x,y,next_y,compare_flags(next_y,height),bc,top,count,counterflags,screen
  y=next_y
 raise AssertionError('environment_values_not_terminated')


def main():
 _,_,base=make_context();counts=collections.Counter()
 def prepare(width=92,height=29,page=0x10,origin=(3,3),controls=False):
  f=Fixture(base,page=page);m=f.memory;key=42 if controls else 41;draw=0x7637 if controls else 0x6BA5;operand=0x7638 if controls else 0x6BA6;top=0x75D3 if controls else 0x6B23
  put(m,operand,(key,0));p=0xF0FD+key*16;put(m,p,(0,0,20 if controls else 12,5,7,m[p+5]));put(m,top,(0,0));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(*draw.to_bytes(2,'little'),1,1))
  for a,v in ((0xAEB3,width),(0xAEAB,height),(0xAEBB,origin[0]&255),(0xAEBF,(origin[0]>>8)&255),(0xAEC7,origin[1]&255),(0xAECB,(origin[1]>>8)&255),(0xBD26,0),(0xBD73,110 if controls else 66)):m[a]=v
  put(m,0xAED5,(0x68,0x48,0x26));return f
 def check(top,width,height,values=None,origin=(3,3),controls=False):
  f=prepare(width,height,origin=origin,controls=controls);m=f.memory;r=f.sim.registers;r[6:8]=[top>>8,top&255];value_base=0x9736 if controls else 0x9728;label_base=0xDF3C if controls else 0xDECB
  if values is not None:put(m,(value_base+top)&65535,values)
  expected=reference(m,top,width,height,origin,labels=label_base,values=value_base);ptr,x,y,a,flags,bc,de,count,counterflags,screen=expected;f.run(0x7650 if controls else 0x6BBE)
  assert tuple(r[:8])==(a,flags,bc>>8,bc&255,de>>8,de&255,ptr>>8,ptr&255),(top,width,height,r[:8],expected[:9])
  assert r[16:18]==[count,counterflags] and r[18:24]==f.initial[18:24] and r[8:12]==f.initial[8:12] and r[SP]==0x8000
  assert (m[0x6320],m[0x6321])==(x,y) and bytes(m[0x4000:0x5B00])==bytes(screen);counts['control_row_prints' if controls else 'row_prints']+=1
 # Проверка всех 13 начальных смещений исходной подписи среды и трёх размеров окна.
 for top in range(13):
  for width in (64,92,188):
   for height in (8,13,16,24,29,192):check(top,width,height)
 # Проверка каждого ненулевого значения, четырёхсимвольных сокращений и окончательного нуля.
 for code in range(1,256):
  for width in (66,67,92,188):check(0,width,29,(code,0))
 for top in (0,1,256,257):check(top,92,29,(ord('Y'),ord('N'),0))
 check(0,92,29,(0,))
 # Проверка флагов альтернативного счётчика и его обёртывания при исходном цикле Y=0..248.
 for count in (127,128,255,256,257):check(0,188,255,[ord('Y')]*count+[0],(3,-512))
 # Проверка всех 43 исходных смещений подписи игровых клавиш через настоящий общий хвост.
 for top in range(43):
  for width in (128,188,248):
   for height in (8,13,16,24,29,192):check(top,width,height,controls=True)
 # Проверка всего AF и обоих прежних изменяемых параметров на десятибайтовой настройке.
 for setup,column in ((0x6C00,66),(0x766C,110)):
  f=prepare();m=f.memory;s=f.sim
  for af in range(65536):
   put(m,0x7FFE,(255,63));s.registers[:]=f.initial;r=s.registers;r[0],r[1]=af>>8,af&255;m[0xBD26]=r[0];m[0xBD73]=r[1];s.run(start=setup,stop=0x3FFF)
   assert r[:2]==[column,0x44] and r[2:12]==f.initial[2:12] and r[16:24]==f.initial[16:24] and m[0xBD26]==0 and m[0xBD73]==column and r[SP]==0x8000;counts['setup_all_af']+=1
 # Проверка рамки и полного результата счётчика, который затем ограничивает наведение.
 for controls in (False,True):
  draw,conditional,callback,top_operand,hover,row_count,column,count_top,width,label_base,value_base=(
   (0x7637,0x7630,0x7648,0x75D3,0x7627,0x7622,110,43,156,0xDF3C,0x9736) if controls else
   (0x6BA5,0x6B9E,0x6BB6,0x6B23,0x6B95,0x6B90,66,13,92,0xDECB,0x9728))
  for page in (0x10,0x18):
   for top in range(count_top):
    f=prepare(page=page,controls=controls);m=f.memory;r=f.sim.registers;put(m,top_operand,(top,0));f.run(draw)
    # Независимый расчёт счётчика и результата значений, bitmap самой рамки здесь не является oracle.
    flat=list(m[0:65536]);flat[0x4000:0x5B00]=[0]*6912;expected=reference(flat,top,width,29,labels=label_base,values=value_base);ptr,x,y,a,flags,bc,de,count,counterflags,_=expected
    assert tuple(r[:8])==(count,counterflags,bc>>8,bc&255,de>>8,de&255,ptr>>8,ptr&255) and r[16:18]==[a,flags]
    assert m[hover]==255 and m[row_count]==r[0] and m[0xBD26]==0 and m[0xBD73]==column and f.wakes==1 and m.o7ffd==page
    assert r[8:12]==f.initial[8:12] and r[18:24]==f.initial[18:24] and r[SP]==0x8000;counts['caption_draws']+=1;counts['caption_im2_wakes']+=f.wakes
  # Проверка точного адреса рисователя и временного RET, алиас индекса не считается совпадением.
  for matched in (False,True):
   for disabled in (False,True):
    f=prepare(controls=controls);m=f.memory;put(m,0x5F00,(0x21,42 if controls else 41,0,0xC9));put(m,0xF3DE,(*draw.to_bytes(2,'little'),1,1) if matched else (0,0x5F,1,1))
    if disabled:m[draw]=0xC9
    f.run(conditional);assert f.wakes==int(matched and not disabled);counts['conditional_draw']+=1;counts['conditional_im2_wakes']+=f.wakes
  # Проверка callback с входным HL от ScrollWindowRows без новой рамки.
  for top in range(count_top):
   f=prepare(width=width,controls=controls);m=f.memory;r=f.sim.registers;r[6:8]=[0,top];expected=reference(m,top,width,29,labels=label_base,values=value_base);ptr,x,y,a,flags,bc,de,count,counterflags,screen=expected;f.run(callback)
   assert tuple(r[:8])==(count,counterflags,bc>>8,bc&255,de>>8,de&255,ptr>>8,ptr&255) and r[16:18]==[a,flags]
   assert m[row_count]==count and f.wakes==0 and bytes(m[0x4000:0x5B00])==bytes(screen);counts['internal_callback_no_frame']+=1
 report=dict(passed=True,cases_by_path=dict(counts),all_13_original_value_offsets=True,all_43_original_controls_offsets=True,all_255_nonzero_value_codes=True,
  high_top_byte_used_for_value_pointer_but_not_cr_selector=True,independent_entire_row_bitmap_and_registers=True,
  real_caption_im2=True,music_disabled=True,independent_caption_bitmap=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EnvironmentRowsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

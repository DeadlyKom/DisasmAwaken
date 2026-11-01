"""Два списка позиций, прямое рисование, реальный HALT/IM2 и независимое тело текста."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckTextStream import reference as stream
from CheckKeyLabel import glyph
from skoolkit.simutils import SP


PANELS=((0x7492,43,0x7489,0xDE53,'В позицию '),(0x751B,44,0x7512,0xDE8F,'С позиции '))


def main():
 _,_,base=make_context();counts=collections.Counter()
 def prepare(panel,page=0x10,rect=(0,0,12,8),flags=6):
  entry,key,hover,_,_=panel;f=Fixture(base,page=page);m=f.memory;put(m,entry+1,(key,0));p=0xF0FD+16*key;put(m,p,(*rect,flags,m[p+5]));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(*entry.to_bytes(2,'little'),1,1));m[hover]=0xA5;return f
 for panel in PANELS:
  entry,key,hover,text,prefix=panel
  # Проверка физических пяти строк, их номера в тексте 1..5 не являются готовым байтом имени SAVE.
  raw=bytes(base[0][text-0xC000:]);end=raw.index(10)+1
  assert raw[:end].decode('cp866')=='\r'.join(prefix+str(i) for i in range(1,6))+'\n'
  for page in (0x10,0x18):
   for rect in ((0,0,12,8),(1,1,12,8),(0,0,2,3)):
    for flags in (6,7,0x60,0x61):
     f=prepare(panel,page,rect,flags);m=f.memory;r=f.sim.registers;body=[]
     def observe(f,pc):
      # Проверка входа хвостового PrintText с сохранённым внешним CPU-возвратом.
      if body or pc!=0xBD08 or m[r[SP]:r[SP]+2]!=[255,63]:return
      positions=[];columns=[m[a] for a in (0xBD73,0xBD7E,0xBD89,0xBD94,0xBD9F)];width,height=m[0xAEB3],m[0xAEAB];origin=(8*rect[0]+3,8*rect[1]+3)
      expected=stream(list(raw),list(m[0x8900:0x8A00]),m[0x6320],m[0x6321],width,height,0,columns,origin,r[2],positions=positions);screen=bytearray(m[0x4000:0x5B00])
      for code,x,y in positions:glyph(m,code,x,y,width,height,origin,screen)
      body.append((expected,screen,tuple(r[2:12]),tuple(r[16:24])))
     f.run(entry,observe);assert len(body)==1;expected,screen,main,alternate=body[0];consumed,x,y,a,flags,_=expected
     assert r[:2]==[a,flags] and r[6]*256+r[7]==text+consumed and tuple(r[2:6])==main[:4] and tuple(r[8:12])==main[6:10] and tuple(r[16:24])==alternate
     assert m[hover]==255 and m[0xBD26]==0 and (m[0x6320],m[0x6321])==(x,y) and bytes(m[0x4000:0x5B00])==bytes(screen)
     assert r[SP]==0x8000 and m.o7ffd==m[0x6306]==page and f.wakes==1;counts['real_panel_draws']+=1;counts['real_caption_im2']+=f.wakes
  f=prepare(panel);m=f.memory;s=f.sim;m[entry]=0xC9;before=[bytes(b) for b in m.banks]
  # Проверка отключённого первого байта по всем флагам, наведение и режим текста не меняются.
  for flags in range(256):
   s.registers[:]=f.initial;r=s.registers;r[1]=flags;s.run(start=entry,stop=0x3FFF)
   assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000;counts['disabled_all_flags']+=1
  assert [bytes(b) for b in m.banks]==before
 report=dict(passed=True,cases_by_path=dict(counts),five_physical_labels_each=True,independent_all_body_bitmap_and_text_status=True,
  original_im2_only_at_caption_halt=True,music_disabled=True,independent_caption_bitmap=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SaveSlotPanelsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

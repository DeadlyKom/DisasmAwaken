"""Рамка оснащения, счётчик попыток, внутренний callback и точный указатель рисователя."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckEquipmentRows import reference
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();counts=collections.Counter();row_report=json.loads((ROOT/'Tools/Disasm/Reports/EquipmentRowsVerification.json').read_text('utf-8'));assert row_report['passed']
 def prepare(top=0,rect=(0,0,32,24),page=0x10):
  f=Fixture(base,page=page);m=f.memory;p=0xF0FD+16*38;put(m,p,(*rect,7,m[p+5]));put(m,0x7228,(38,0));put(m,0x71B9,top.to_bytes(2,'little'));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(0x27,0x72,1,1));m[0x7212]=0xA7;m[0x7217]=0xA5
  return f
 def compare(f,expected):
  r=f.sim.registers;m=f.memory;main=tuple(b for w in expected['main'] for b in (w>>8,w&255));other=tuple(b for w in expected['alternate'] for b in (w>>8,w&255))
  assert tuple(r[:2])==expected['counter'] and tuple(r[16:18])==expected['af'] and tuple(r[2:8])==main and tuple(r[18:24])==other
  assert m[0x7212]==r[0] and bytes(m[0x4000:0x5B00])==bytes(expected['screen']) and (m[0x6320],m[0x6321])==(expected['x'],expected['y'])
  assert r[8:12]==f.initial[8:12] and r[SP]==0x8000
 # Проверка рамки и счётчика по всем 30 штатным смещениям, двум страницам и трём геометриям.
 for top in range(30):
  for page in (0x10,0x18):
   for rect in ((0,0,32,24),(0,0,24,8),(0,0,2,3)):
    f=prepare(top,rect,page);m=f.memory;r=f.sim.registers;body=[];header=[]
    def observe(f,pc):
     if pc==0x723B:header.append((tuple(r[:8]),bytes(m[0x4000:0x5B00])))
     if pc==0x7244:body.append(reference(m,top,m[0xAEB3],m[0xAEAB],(3,3)))
    f.run(0x7227,observe);assert len(header)==1
    if body:
     assert len(body)==1 and not header[0][0][1]&1;compare(f,body[0]);counts['full_panel_body']+=1
    else:
     old,screen=header[0];assert old[1]&1 and r[:2]==[0,0x44] and tuple(r[16:18])==old[:2] and tuple(r[2:8])==old[2:8] and m[0x7212]==0 and bytes(m[0x4000:0x5B00])==screen;counts['header_carry_skips_body']+=1
    assert m[0x7217]==255 and m[0xBD26]==0 and m.o7ffd==m[0x6306]==page and f.wakes==1;counts['real_caption_im2']+=1
 # Проверка внутреннего входа 7244 от прокрутки, без рамки и сброса подсветки.
 for top in range(30):
  f=prepare(top);m=f.memory;r=f.sim.registers;r[6:8]=[0,top]
  for a,v in ((0xBD26,0),(0xBD73,116),(0xBD7E,134),(0xBD89,156),(0xBD94,174),(0x72DD,8),(0xAEB3,188),(0xAEAB,53),(0xAEBB,3),(0xAEBF,0),(0xAEC7,3),(0xAECB,0)):m[a]=v
  expected=reference(m,top,188,53);f.run(0x7244);compare(f,expected);assert f.wakes==0 and m[0x7217]==0xA5;counts['internal_callback_no_frame']+=1
 # Проверка точного адреса, чужой алиас с тем же ключом не проходит TestDrawPointer.
 for present in (False,True):
  for disabled in (False,True):
   f=prepare();m=f.memory;put(m,0x5F00,(0x21,38,0,0xC9))
   if not present:put(m,0xF3DE,(0,0x5F,1,1))
   if disabled:m[0x7227]=0xC9
   f.run(0x7220);assert f.wakes==int(present and not disabled)
   if not present or disabled:assert m[0x7212]==0xA7 and m[0x7217]==0xA5
   counts['conditional_exact_pointer_and_c9']+=1
 # Проверка всех F отключённого прямого входа, код не читает даже изменяемое слово индекса.
 f=prepare();m=f.memory;s=f.sim;m[0x7227]=0xC9;before=[bytes(b) for b in m.banks]
 for flags in range(256):
  s.registers[:]=f.initial;r=s.registers;r[1]=flags;s.run(start=0x7227,stop=0x3FFF)
  assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
  counts['disabled_all_flags']+=1
 assert [bytes(b) for b in m.banks]==before
 report=dict(passed=True,cases_by_path=dict(counts),row_model_report='Tools/Disasm/Reports/EquipmentRowsVerification.json',
  full_word_top_row=True,sentinel_attempt_counter_preserved=True,independent_whole_body_bitmap=True,
  independent_caption_bitmap=False,original_im2_only_at_caption_halt=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EquipmentListPanelsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

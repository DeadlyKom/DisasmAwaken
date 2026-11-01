"""Действие статуса, настоящий рисователь, сохранённый AF и физический синтетический возврат."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckGlyphRenderer import and_flags
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();counts=collections.Counter()
 # Проверка полного раннего Carry без геометрического вызова для каждого допустимого F и A.
 f=Fixture(base);m=f.memory;s=f.sim;before=[bytes(b) for b in m.banks]
 for flags in range(256):
  if not flags&1 or flags&64:continue
  for a in range(256):
   s.registers[:]=f.initial;r=s.registers;r[:2]=[a,flags];s.run(start=0x7F17,stop=0x3FFF)
   assert r[:12]==[a,flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
   counts['early_carry_all_af_with_z_clear']+=1
 assert [bytes(b) for b in m.banks]==before and not f.trace.writes
 def execute(a,flags,last,alias=False):
  f=Fixture(base);m=f.memory;r=f.sim.registers;draw=0x5F00 if alias else 0x7F35;put(m,0x7F36,(0,0));put(m,0x5F00,(0xC9,0,0,0xC9));put(m,0x5F10,(0x21,63,0,0xC9))
  pointers=(0x5F10,draw) if last else (draw,0x5F10);put(m,0xF3DE,b''.join(p.to_bytes(2,'little') for p in pointers)+bytes((1,1)))
  put(m,0xF0FD,(0,0,32,5,0x80,0));m[0xCA20]=6;m[0x9E78]=0;m[0x984B]=0;put(m,0x984E,(0xE8,3));m[0x9850]=1;m[0x9851]=10
  r[:2]=[a,flags];r[4:6]=[0,0];r[6:8]=[draw>>8,draw&255];r[8:10]=[0xF0,0xFD];saved_flags=and_flags(a) if flags&64 else flags;saved=a*256+saved_flags;frames=[];calls=[]
  def observe(f,pc):
   if pc==0x7F1E:assert r[:2]==[a,saved_flags]
   if pc==0x7F1F:
    assert r[SP]==0x7FFC and bytes(m[0x7FFC:0x8000])==saved.to_bytes(2,'little')+bytes((255,63));frames.append('saved')
   if pc==draw:
    assert not last and r[SP]==0x7FFA and bytes(m[0x7FFA:0x8000])==bytes((0x30,0x7F))+saved.to_bytes(2,'little')+bytes((255,63));frames.append('draw')
   if pc in (0x7F30,0x7F33):calls.append(pc)
  f.run(0x7F17,observe)
  assert r[:2]==[a,saved_flags] and frames==(['saved'] if last else ['saved','draw'])
  assert calls==([0x7F33] if last else [0x7F30,0x7F33]) and r[SP]==0x8000 and f.wakes==0
  if last:assert r[4:8]==[0,0,draw>>8,draw&255]
  else:assert m[0x9B16]==0
  counts['full_action']+=1;counts['synthetic_draw_frames']+=not last;counts['actual_status_draws']+=not last and not alias;counts['ret_alias_draws']+=not last and alias
 # Проверка всех A, исходного Z и двух маршрутов списка с настоящим рисователем.
 for a in range(256):
  for flags in (0,0x20,0x40,0x60):
   for last in (False,True):execute(a,flags,last)
 # Проверка сохранения существующего адреса C9-алиаса с тем же индексом.
 for a in (0,1,2,127,128,255):
  for flags in (0,0x20,0x40,0x60):
   for last in (False,True):execute(a,flags,last,True)
 report=dict(passed=True,cases_by_path=dict(counts),all_input_a_bytes=True,z_selects_geometry_independently_of_a=True,
  saved_af_exact_after_geometry=True,physical_action_draw_and_return_frames=True,real_status_draw_and_pointer_helpers=True,
  existing_ret_alias_kept_by_key_lookup=True,active_callback_fixture_is_empty=True,independent_whole_status_bitmap=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StatusPanelActionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

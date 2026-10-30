"""Полное действие с префиксом RepaintAndFlag, настоящий 14-байтовый кадр и вложенные CALL."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckGlyphRenderer import compare_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));_,_,banks=make_context();banks=[bytearray(b) for b in banks]
 entry=next(e for e in manifest['entries'] if e['slot']==5);lang=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=lang
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':31,'BC':0x36C9,'AF':0x0144,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 fixtures=[('accept',1,0,False,12,100,15,3,2000),('wrap_accept',1,0,False,250,10,15,15,2000),
  ('reject',1,0,False,100,10,15,3,2000),('same_key',1,0,True,12,100,15,3,2000),
  ('other_row',0,0,False,12,100,15,3,2000),
  ('complete_refresh',0,1,True,12,100,15,3,2000),('complete_refresh',1,1,True,12,100,15,3,2000)]
 for credits in (0,999,1000,65535):
  for quantity in (0,15,255):fixtures.append(('cancel',1,1,False,12,100,quantity,3,credits))
 results=[];wakeups=0;max_steps=0
 # Проверка успешного принятия, отказа, пропуска и расторжения через настоящий общий хвост.
 fixtures=[(*fixture,pointer_y) for fixture in fixtures for pointer_y in (0,100)]
 for name,row,active,same,used,capacity,quantity,required,credits,pointer_y in fixtures:
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x10)
  memory[0x6306]=0x10;memory[0x6548]=1;memory[0x9B16]=0x5A;put(memory,0x6307,[50,pointer_y])
  put(memory,0x8500,bytes([0x80,255])*128);put(memory,0x8600,bytes(768));memory[0x9E78]=0;put(memory,0x9CA6,[0,0xE0]);put(memory,0xE000,[0xC5,0x6F,1,1])
  put(memory,0xF0FD,[0,0,31,5,0,0]);put(memory,0xF2ED,[6,10,11,4,0,4]);put(memory,0xF2FD,[3,5,26,18,0,4])
  put(memory,0x7F36,[0,0]);put(memory,0x6FC6,[31,0]);put(memory,0xAA86,[32,0])
  current=0x4B38;offer=current if same else 0x4B39
  put(memory,0x983F,current.to_bytes(2,'little')+bytes([0xF3,0x4A]));put(memory,0x98B0,offer.to_bytes(2,'little')+bytes([0xF3,0x4A]))
  memory[0x99A3]=active;memory[0x99A4]=0x5A;memory[0x6F54]=row
  put(memory,0x9850,[used,capacity,quantity,0xC7]);put(memory,0x98BE,[required,0xB3])
  put(memory,0x984E,credits.to_bytes(2,'little'));put(memory,0x7FFE,[255,63])
  sim.registers[:]=initial;r=sim.registers;r[PC]=0x6E9C;trace=PortTrace(sim);sim.set_tracer(trace)
  halts=0;frame=None;cancel_entry=None;scripts=0
  for steps in range(700000):
   pc=r[PC]
   if pc==0x3FFF:break
   if pc==0x6EB1:frame=bytes(memory[r[SP]:r[SP]+14])
   if pc==0x6F5D:cancel_entry=(r[H],r[D])
   if pc==0xC000 and memory.o7ffd&7==6:scripts+=1
   if memory[pc]==0x76:
    assert pc in (0xC089,0x6F3A,0x6F3B,0x6F9A,0x6F9B),hex(pc)
    r[PC]+=1;halts+=1;continue
   sim.opcodes[memory[pc]]()
  else:raise AssertionError(('instruction_limit',name,hex(r[PC]),r[SP]))
  assert frame==bytes.fromhex('3a5c68244200c936c56f1f00ff3f'),(name,frame.hex())
  assert r[H]*256+r[L]==0x6FC5 and r[D:E+1]==initial[D:E+1] and r[B]==initial[B]
  assert (r[C],r[A],r[SP])==(pointer_y>>3,255,0x8000) and r[8:12]==initial[8:12]
  assert memory[0x6F54]==255 and memory.o7ffd==0x10 and memory[0x6306]==0x10
  assert r[F]==(0x44 if pointer_y==0 else compare_flags(0,pointer_y>>3))
  assert bytes(memory[0xE000:0xE002])==(bytes([1,1]) if pointer_y==0 else bytes([0xC5,0x6F]))
  if pointer_y==0:assert memory[0x9A82]==0
  expected_credits=max(0,credits-1000) if name=='cancel' else credits+1000 if name=='complete_refresh' else credits
  assert int.from_bytes(bytes(memory[0x984E:0x9850]),'little')==expected_credits
  if name in ('accept','wrap_accept'):
   assert (memory[0x99A3],memory[0x99A4],memory[0x9850],memory[0x9852],memory[0x9853])==(1,0,(used+required)&255,(quantity+required)&255,10),(name,[memory[x] for x in (0x99A3,0x99A4,0x9850,0x9852,0x9853)],scripts)
  elif name=='cancel':
   high_left,high_right=cancel_entry;expected=0 if high_left*256+quantity<high_right*256+required else (quantity-required)&255
   assert memory[0x99A3]==0 and memory[0x9852]==expected and scripts==1
  elif name=='complete_refresh':assert memory[0x99A3]==0 and memory[0x99A4]==1 and memory[0x9852]==quantity-required and scripts==1
  elif name=='reject':assert memory[0x99A3]==0 and memory[0x9850]==used and memory[0x9852]==quantity
  else:assert memory[0x99A3]==active and memory[0x9852]==quantity
  results.append(dict(branch=name,pointer_y=pointer_y,credits=credits,quantity=quantity,final_quantity=memory[0x9852],halt_wakeups=halts))
  wakeups+=halts;max_steps=max(max_steps,steps)
 report=dict(passed=True,cases=len(fixtures),results=results,max_instructions=max_steps,halt_fixture_wakeups=wakeups,
  method='original_complete_mission_action_with_last_draw_handler_no_geometry_action_real_drawers_LANG_and_close',
  entry='6E9C',prefix_RepaintAndFlag_executed=True,close_menu_row_match_and_mismatch=True,frame_bytes=14,
  model_rom_sha256=hashlib.sha256(bytes(memory.roms[1])).hexdigest(),emulator_rom_match_verified=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionActionFlowVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

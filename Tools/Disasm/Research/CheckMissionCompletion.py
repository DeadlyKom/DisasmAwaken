"""Полный DrawItem32, выдача награды и единственная вложенная перерисовка без IRQ."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));_,_,banks=make_context();banks=[bytearray(b) for b in banks]
 entry=next(e for e in manifest['entries'] if e['slot']==5);lang=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=lang
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=completed=wakeups=0;max_steps=0;branches={};results=[]
 # Проверка каждого отказа допуска и границ денежного переполнения в полном рисователе.
 fixtures=[('inactive',0,0,True,15,15,1000,500),('other_state',255,0,True,15,15,1000,500),
  ('wrong_first',1,0,False,15,15,1000,500),('already_completed',1,1,True,15,15,1000,500),
  ('too_little',1,0,True,14,15,1000,500)]
 for credits,reward in ((0,0),(0,65535),(65000,535),(65000,536),(65535,0),(65535,1),(1000,2000)):
  for quantity in (15,255):fixtures.append(('complete',1,0,True,quantity,15,credits,reward))
 fixtures=[(*fixture,width) for fixture in fixtures for width in (31,32)]
 for name,active,guard,same,quantity,required,credits,reward,width in fixtures:
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x10)
  memory[0x6306]=0x10;memory[0x6548]=1;memory[0x9B16]=0x5A;put(memory,0x6307,[50,100])
  put(memory,0x8500,bytes([0x80,255])*128);put(memory,0x8600,bytes([0x33])*768)
  put(memory,0xF0FD,[0,0,width,5,0,0]);put(memory,0xF2ED,[6,10,11,4,0,4]);put(memory,0xF2FD,[3,5,26,18,0,4])
  put(memory,0x7F36,[0,0]);put(memory,0x6FC6,[31,0]);put(memory,0xAA86,[32,0])
  put(memory,0x983F,bytes([0x38,0x4B,0xF3,0x4A]));put(memory,0x98B0,bytes([0x38 if same else 0x39,0x4B,0xF3,0x4A]))
  memory[0x99A3]=active;memory[0x99A4]=guard;memory[0x9852]=quantity;memory[0x98BE]=required
  put(memory,0x984E,credits.to_bytes(2,'little'));put(memory,0x98BC,reward.to_bytes(2,'little'));put(memory,0x7FFE,[255,63])
  sim.registers[:]=initial;r=sim.registers;r[PC]=0xAA85;trace=PortTrace(sim);sim.set_tracer(trace)
  entries=offers=scripts=halts=0;completion_states=[]
  for steps in range(700000):
   pc=r[PC]
   if pc==0x3FFF:break
   if pc==0xC089:
    assert memory[pc]==0x76;r[PC]+=1;halts+=1;continue
   if pc==0xAA85:entries+=1;completion_states.append((memory[0x99A3],memory[0x99A4]))
   if memory[pc]==0xCD and memory[(pc+1)&65535]==0x14 and memory[(pc+2)&65535]==0xAC:offers+=1
   if pc==0xC000 and memory.o7ffd&7==6:scripts+=1
   sim.opcodes[memory[pc]]()
  else:raise AssertionError(('instruction_limit',name,hex(r[PC]),r[SP],memory.o7ffd,entries))
  success=name=='complete';expected_credits=65000 if credits+reward>65535 else credits+reward
  assert int.from_bytes(bytes(memory[0x984E:0x9850]),'little')==(expected_credits if success else credits),(name,credits,reward)
  assert memory[0x9852]==(quantity-required if success else quantity)
  assert (memory[0x99A3],memory[0x99A4])==((0,1) if success else (active,guard))
  assert (entries,offers,scripts)==((2,1,1) if success else (1,0,0)),(name,entries,offers,scripts,completion_states)
  assert r[10:12]==initial[10:12] and (success or r[8:10]==initial[8:10]) and r[SP]==0x8000 and memory.o7ffd==0x10 and memory[0x6306]==0x10
  if success:assert completion_states==[(1,0),(0,1)]
  branches[name]=branches.get(name,0)+1;completed+=success;cases+=1;wakeups+=halts;max_steps=max(max_steps,steps)
  results.append(dict(branch=name,status_width=width,credits=credits,reward=reward,final_credits=int.from_bytes(bytes(memory[0x984E:0x9850]),'little'),quantity=quantity,halt_wakeups=halts))
 report=dict(passed=True,cases=cases,completed=completed,branches=branches,max_instructions=max_steps,
  halt_fixture_wakeups=wakeups,recursive_draw_count_on_completion=2,results=results,
  method='complete_original_DrawItem32_caption_printing_system_name_script_reward_offer_and_recursive_redraw',
  model_rom_sha256=hashlib.sha256(bytes(memory.roms[1])).hexdigest(),emulator_rom_match_verified=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionCompletionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

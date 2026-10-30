"""Исходная строка состояния, выбор полицейского статуса и полные вложенные печати."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put


def main():
 _,_,banks=make_context();memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 def after_lf(base,index):
  for _ in range(index+1):
   while memory[base]!=10:base+=1
   base+=1
  return base
 cases=disabled=0
 # Проверка всех значений статусного байта с разными числами денег, загрузки и ранга.
 for status in range(256):
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x10)
  put(memory,0x8500,bytes([0x80,255])*128);put(memory,0x8600,bytes([0x33])*768);put(memory,0xF0FD,[0,0,31,8,0,0])
  put(memory,0x7F36,[0,0]);put(memory,0x7FFE,[255,63]);memory[0x984B]=status
  score=(status*257)&65535;credits=(65535-status*193)&65535
  put(memory,0x984C,score.to_bytes(2,'little')+credits.to_bytes(2,'little'));put(memory,0x9850,[status,255-status])
  sim.registers[:]=initial;r=sim.registers;r[PC]=0x7F35;prints=[];numbers=[];rank_entry=False
  for _ in range(60000):
   if r[PC]==0x3FFF:break
   if r[PC] in (0x7F48,0x7F60,0x7F64,0x7F6F):prints.append(r[H]*256+r[L])
   if r[PC] in (0x7F6C,0x7F78,0x7F86):numbers.append((0xBC01 if r[PC]==0x7F6C else 0xBBBE,r[B]*256+r[C]))
   if r[PC]==0xAC74:rank_entry=True
   sim.opcodes[memory[r[PC]]]()
  else:raise AssertionError(('instruction_limit',status,hex(r[PC])))
  status_text=after_lf(0xEA3B,min(status>>5,3));caption=after_lf(0xEA89,0)
  assert prints[:3]==[caption,status_text,after_lf(caption,0)],(status,prints)
  assert numbers==[(0xBC01,credits),(0xBBBE,status),(0xBBBE,255-status)] and rank_entry
  assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and r[SP]==0x8000
  assert r[D]*256+r[E]==score and memory[0xBD26]==1
  cases+=1
 # Проверка отключённого первого байта без изменения состояния.
 for value in range(256):
  sim.registers[:]=initial;memory[0x7F35]=0xC9;put(memory,0x7FFE,[255,63]);memory[0x984B]=value
  sim.run(start=0x7F35,stop=0x3FFF)
  assert sim.registers[:12]==initial[:12] and sim.registers[16:24]==initial[16:24] and sim.registers[SP]==0x8000
  disabled+=1
 report=dict(passed=True,cases=cases,disabled_cases=disabled,
  method='complete_original_status_draw_registration_fill_strings_numbers_and_player_rank',
  status_index='min(byte_984B_shift_right_5,3)',low_five_bits_ignored_by_status_selection=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StatusDrawVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

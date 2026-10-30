"""Развилки основного цикла на исходных инструкциях, без подмены проверки игровым запуском."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckGlyphRenderer import compare_flags
from CheckWorldSignature import logical_flags


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 def prepare(reset=True):
  if reset:
   memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x10);memory[0x6306]=0x10
  sim.registers[:]=initial;put(memory,0x7FFE,[255,63]);trace=PortTrace(sim);sim.set_tracer(trace);return sim.registers,trace
 def run(entry,stops):
  r=sim.registers;r[PC]=entry
  for _ in range(4096):
   if r[PC] in stops:return r[PC]
   sim.opcodes[memory[r[PC]]]()
  raise AssertionError(('limit',hex(entry),hex(r[PC])))
 # Проверка начальных записей до первой игровой зависимости.
 r,trace=prepare();memory[0x9AB7]=0x77;memory[0x9A99]=0x99
 assert run(0x9A59,{0xA91B})==0xA91B
 assert memory[0x9AB7]==memory[0x9A99]==0 and memory[0xA9A9]==0x80 and r[SP]==0x7FFC
 # Отдельная граница после GenerateMarket, его вызов не считается исполненным этой моделью.
 r,trace=prepare();memory[0xA9A9]=0x80;assert run(0x9A68,{0x9C77})==0x9C77
 assert memory[0xA9A9]==0 and r[SP]==0x7FFC
 # Проверка настоящего выбора LANG перед начальным сценарием.
 r,trace=prepare();assert run(0x9A6F,{0xC000})==0xC000
 assert memory[0x983A]==15 and memory.o7ffd==0x16 and trace.writes==[(0x7FFD,0x16)]
 assert r[SP]==0x7FFC and bytes(memory[0x7FFC:0x7FFE])==bytes([0x7C,0x9A])
 enabled=pulses=transitions=actions=0
 # Проверка запроса перестроения для всех байтов EventEnabled, до HALT или RebuildInterface.
 for value in range(256):
  r,trace=prepare();memory[0x9A82]=value;target=run(0x9A81,{0x9C77,0x9A87})
  assert target==(0x9C77 if value==0 else 0x9A87) and r[SP]==(0x7FFC if value==0 else 0x7FFE)
  assert (r[A],r[F])==(value,logical_flags(value)|0x10);enabled+=1
 # Проверка чтения и сброса импульса ISR, до сценария либо следующей развилки.
 for value in range(256):
  r,trace=prepare();memory[0x9A99]=value;memory[0x9A82]=0xA5
  target=run(0x9A98,{0xC000,0x9AB6})
  if value:
   assert target==0xC000 and memory[0x9A99]==memory[0x9A82]==0 and memory[0x983A]==16
   assert memory.o7ffd==0x16 and trace.writes==[(0x7FFD,0x16)] and r[SP]==0x7FFC
  else:assert target==0x9AB6 and memory[0x9A82]==0xA5 and not trace.writes and r[SP]==0x7FFE
  pulses+=1
 # Проверка точного диапазона запроса перехода, сравнивается знак результата DEC, а не исходного байта.
 for value in range(256):
  r,trace=prepare();r[F]=(value*73)&255;memory[0x9AB7]=value
  result=(value-1)&255;target=run(0x9AB6,{0x9AC2,0x7E5A})
  expected=0x7E5A if 2<=value<=128 else 0x9AC2
  flags=((value*73)&1)|(result&0xA8)|2|(0x40 if result==0 else 0)|(0x10 if not value&15 else 0)|(4 if value==128 else 0)
  assert target==expected and (r[A],r[F])==(result,flags)
  assert memory[0x9AB7]==(result if value in range(1,129) else value) and r[SP]==0x7FFE
  transitions+=1
 # Проверка всех пар текущего и предыдущего объединённого кода, реальная MergeActionInputs исполняется.
 r,trace=prepare()
 for previous in range(256):
  for current in range(256):
   r,trace=prepare(False);memory[0x9AD0]=previous
   memory[0x66EC]=memory[0x6585]=memory[0x66ED]=0;memory[0x658A]=current
   target=run(0x9ACB,{0x9A81,0x9ADE,0x9AE4})
   expected=0x9A81 if not (previous|current) else 0x9AE4 if current>=previous else 0x9ADE
   assert target==expected and memory[0x9AD0]==current and (r[A],r[C],r[D])==(current,current,previous)
   assert r[F]==(logical_flags(0) if not (previous|current) else compare_flags(current,previous))
   assert r[SP]==0x7FFE and r[B]==initial[B] and r[E]==initial[E] and r[H:L+1]==initial[H:L+1]
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];actions+=1
 report=dict(passed=True,event_enabled_cases=enabled,pulse_cases=pulses,transition_cases=transitions,action_pairs=actions,
  method='original_main_loop_control_boundaries_real_page_calls_and_input_merge',
  previous_action_is_self_modified_operand=True,launch_codes_are_2_through_128=True,
  drawing_executed=False,script_executed=False,callbacks_executed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MainLoopControlVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

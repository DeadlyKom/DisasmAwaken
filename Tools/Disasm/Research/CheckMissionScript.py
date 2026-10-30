"""Исходный LANG от CA8F для события 17, с реальным разбором условий и командой T."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,PC,SP
from CheckRowHighlight import make_context
from CheckWeightedLoad import reference


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 entry=next(e for e in manifest['entries'] if e['slot']==5)
 lang=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();_,_,banks=make_context()
 original=bytearray(65536);original[0x4000:0x8000]=bytes(banks[5]);original[0x8000:0xC000]=bytes(banks[2]);original[0xC000:0xC000+len(lang)]=lang
 memory=original.copy();sim=Simulator(memory);rng=random.Random(0x6F7D)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 maximum=0;paths=set();cases=1024
 for case in range(cases):
  memory[:]=original
  # Создание разных таблиц веса и игровых количеств без изменения исследуемого LANG.
  for base,count in ((0x94FA,30),(0x9829,219)):
   memory[base:base+count]=bytes(rng.randrange(256) for _ in range(count))
  for base,count in ((0x95F1,30),(0x9633,14)):
   for i in range(count):memory[base+2*i]=rng.randrange(4)
  memory[0x984A]=case&255;memory[0x9852]=case&255;memory[0x983A]=17
  memory[0x7FFE:0x8000]=bytes([255,63]);before=bytes(memory[0x9829:0x9904]);first_sum=reference(memory,0xC0DB)[0]
  oracle=memory.copy();oracle[0x9850]=first_sum;expected=reference(oracle,0xC0DB)[0]
  sim.registers[:]=initial;r=sim.registers;r[PC]=0xC000;commands=[]
  for steps in range(50000):
   if r[PC]==0x3FFF:break
   if r[PC] in (0xC0DB,0xC0E7):commands.append(r[PC])
   sim.opcodes[memory[r[PC]]]()
  else:raise AssertionError(('instruction_limit',case,hex(r[PC])))
  after=bytearray(memory[0x9829:0x9904]);after[0x9850-0x9829]=before[0x9850-0x9829]
  assert bytes(after)==before and memory[0x9850]==expected and commands==[0xC0DB,0xC0DB,0xC0E7],(case,commands,memory[0x9850],expected,[(hex(0x9829+i),a,b) for i,(a,b) in enumerate(zip(before,after)) if a!=b])
  assert r[SP]==0x8000 and r[10:12]==initial[10:12]
  maximum=max(maximum,steps);paths.add(tuple(commands))
 report=dict(passed=True,cases=cases,method='original_LANG_event_17_full_interpreter_and_weighted_load',
  executed_command_paths=[[hex(x) for x in path] for path in sorted(paths)],max_instructions=maximum,
  event_decimal=17,event_hex='11',weighted_sum_runs=2,other_game_fields_preserved=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionScriptVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

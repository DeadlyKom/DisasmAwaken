"""Перенесённый выход станции до TR-DOS и продолжение после отдельно заданной загрузки."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC,IFF
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 def load(slot):
  e=next(e for e in manifest['entries'] if e['slot']==slot);return (ROOT/(e['path']+'.sectors.bin')).read_bytes()
 music=load(10);banks[3][0x1B00:0x1B00+len(music)]=music
 action=load(17);memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x1F);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0
 for case in range(256):
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x1F)
  memory[0x6306]=0x16;put(memory,0x4200,memory[0x7EC0:0x7FC0]);put(memory,0x5000,bytes([0xA5])*768)
  state=bytes((case+73*i)&255 for i in range(512));put(memory,0x4000,state)
  sim.registers[:]=initial;r=sim.registers;trace=PortTrace(sim);sim.set_tracer(trace)
  sim.run(start=0x4200,stop=0x3D13)
  assert (r[A],r[B],r[C],r[H]*256+r[L],r[D]*256+r[E],r[SP],r[10]*256+r[11])==(0,0,14,0x4251,0x5CE6,0x7FFC,0x5C3A)
  assert bytes(memory[0x5CDD:0x5CE6])==b'ACTION  C' and memory[0x5CF9]==0 and r[IFF]==0
  assert memory[0x5000]==0 and bytes(memory[0x5001:0x5300])==bytes([0xA5])*767
  expected=[(0x7FFD,0x13)]+[p for reg in range(13,-1,-1) for p in ((0xFFFD,reg),(0xBFFD,0))]+[(0x7FFD,0x10),(0x7FFD,0x18)]
  assert trace.writes==expected and memory.o7ffd==0x18 and memory[0x6306]==0x10
  assert bytes(memory[0x7FFC:0x7FFE])==bytes([0x36,0x42]) and r[8:10]==initial[8:10] and r[16:24]==initial[16:24]
  # Моделирование только постусловия успешной загрузки, реальный TR-DOS здесь не исполняется.
  put(memory,0x6000,action);r[A]=case;r[F]=case;r[B]=case;r[C]=case;r[D]=case;r[E]=case;r[H]=case;r[L]=case
  r[SP]=0x7FFE;r[PC]=0x4236
  sim.run(stop=0x6000)
  assert bytes(memory[0x9BBD:0x9DBD])==state and bytes(memory[0x4000:0x4200])==state
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[SP])==(0x4200,0x9DBD,0,0,0x6000)
  assert r[A]==case and r[IFF]==0 and memory.o7ffd==0x18
  cases+=1
 report=dict(passed=True,cases=cases,method='original_relocated_station_exit_real_music_and_explicit_disk_postcondition',
  real_music_initializer_executed=True,real_bank_switches=True,only_one_5000_byte_cleared=True,
  disk_load_substituted=True,trdos_executed=False,action_entry_executed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StationExitVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

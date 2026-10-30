"""Исходные подготовка строки окна, банковая обёртка и команды M/m без рисования и заглушек."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import logical_flags


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 lang=(ROOT/(e['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=lang
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases={'fixed':0,'banked':0,'commands':0}
 def prepare(page,kind):
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(page);memory[0x6306]=page
  put(memory,0x6E8B,[10,0]);put(memory,0x9CA6,[0xDE,0xF3]);memory[0x9A82]=0xA5
  record=[0xA0,0xB0,1,1,0xAB,0xCD,0x12,0x34,3,4,9,7,0x8A,0x6E,0x56,0x78]
  # Создание исходного физического экземпляра и списка в настоящем банке 0.
  memory.banks[0][0x30FD+160:0x30FD+176]=bytes(record)
  for pointer,key in ((0x5000,30),(0x5008,31),(0x5010,10)):put(memory,pointer,[0x21,key,0,0xC9])
  pointers=[] if kind==0 else [0x5000,0x6E8A if kind==1 else 0x5010,0x5008]
  data=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes([1,1]);memory.banks[0][0x33DE:0x33DE+132]=bytes([0x55])*132;memory.banks[0][0x33DE:0x33DE+len(data)]=data
  chosen=0x5010 if kind==2 else 0x6E8A;expected=[0x5000,0x5008,chosen] if kind else [chosen]
  put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;trace=PortTrace(sim);sim.set_tracer(trace)
  return r,trace,chosen,expected
 def check_common(r,chosen,pointers):
  assert r[H]*256+r[L]==chosen and r[D]*256+r[E]==10
  assert memory.banks[0][0x30FD+160:0x30FD+164]==bytes([3,4,9,7]) and memory[0x9A82]==0
  data=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes([1,1]);assert memory.banks[0][0x33DE:0x33DE+len(data)]==data
  assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
 for page in (0x10,0x18):
  for kind in range(3):
   for row in range(256):
    r,trace,chosen,pointers=prepare(page,kind);r[A]=row;r[F]=(row*73)&255;sim.run(start=0xA85F,stop=0x3FFF)
    assert (r[A],r[F],r[B],r[C],r[SP])==(row,(row*73)&255,0x36,0xC9,0x8000)
    assert memory[0x6E91]==row and not trace.writes and memory.o7ffd==page and r[8:10]==initial[8:10]
    check_common(r,chosen,pointers);cases['fixed']+=1
 for page in (0x16,0x1E):
  for kind in range(3):
   for row in range(256):
    r,trace,chosen,pointers=prepare(page,kind);r[A]=row;sim.run(start=0xA86B,stop=0x3FFF)
    assert (r[A],r[F],r[B],r[C],r[SP])==(page,logical_flags(page),0x36,0xC9,0x8000)
    assert memory[0x6E91]==row and trace.writes==[(0x7FFD,page&0xF8|0x10),(0x7FFD,page)] and memory.o7ffd==page
    check_common(r,chosen,pointers);cases['banked']+=1
   for entry in (0xC0EC,0xC100):
    for number in list(range(256))+[256,65535,65536]:
     r,trace,chosen,pointers=prepare(page,kind);r[8],r[9]=0xB0,0;r[SP]=0x7FF0;put(memory,0x7FF0,[255,63]);text=str(number).encode()+b'\x00';put(memory,0xB000,list(text));memory[0xC028]=0x7A
     sim.run(start=entry,stop=0xC00C)
     assert memory[0x6E91]==((number-1)&255) and memory[0xC028]==(1 if entry==0xC0EC else 0x7A)
     assert (r[A],r[F],r[SP])==(page,logical_flags(page),0x7FF0) and r[8]*256+r[9]==0xB000+len(text)-1
     assert trace.writes==[(0x7FFD,page&0xF8|0x10),(0x7FFD,page)]
     check_common(r,chosen,pointers);cases['commands']+=1
 report=dict(passed=True,method='original_text_row_queue_restore_bounds_and_M_m_commands',cases=cases,
  actual_restore_item_bounds=True,existing_alias_by_index_tested=True,drawing_executed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/QueuedTextRowVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

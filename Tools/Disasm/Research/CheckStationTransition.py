"""Команда W и фиксированная подготовка перехода до входа перенесённого кода 4200."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,I,IM,IFF
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckGlyphRenderer import compare_flags
from CheckMatrixKey import add_flags


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();banks[6][:len(source)]=source
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},{'iff':1,'im':2},False)
 cases=returns=0
 for command in (False,True):
  for selected in range(256):
   for extra in (0,255):
    memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x16)
    memory[0x6306]=0x16;memory[0x9849]=selected;memory[0x98AA]=extra;memory[0x9906]=(selected*73)&255
    memory[0x983D]=0x37;memory[0x983E]=0xA9;memory[0x9AB7]=0x52
    put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;trace=PortTrace(sim);sim.set_tracer(trace)
    old_add=memory[0x9906];expected_state=bytes(memory[0x983B:0x9A3B]);expected_state=expected_state[:2]+bytes([0xA9,0x37])+expected_state[4:]
    if extra!=255:
     changed=bytearray(expected_state);changed[0x9906-0x983B]=(old_add+30)&255;expected_state=bytes(changed)
    expected_code=bytes(memory[0x7EC0:0x7FC0])
    target=0x3FFF if selected==255 else 0x4200
    sim.run(start=0xC103 if command else 0x7E5A,stop=target)
    assert memory[0x9AB7]==(255 if command else 0x52)
    assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    if selected==255:
     assert (r[A],r[F],r[SP])==(255,compare_flags(255,255),0x8000)
     assert r[2:8]==initial[2:8] and memory.o7ffd==0x16 and not trace.writes
     assert r[IFF]==1 and r[IM]==2 and memory[0x9906]==old_add;returns+=1
    else:
     flags=0x51 if extra==255 else add_flags(old_add,30)
     last=(0x37+expected_code[-1])&255;flags=(flags&0xC1)|(last&8)|((last&2)<<4)
     assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[SP])==(0x37,flags,0x7FC0,0x4300,0,0,0x7FFE)
     assert memory.o7ffd==0x1F and memory[0x6306]==0x16 and trace.writes==[(0x7FFD,0x1F)]
     assert bytes(memory.banks[7][0x1800:0x1B00])==bytes(768) and bytes(memory[0x5800:0x5B00])==bytes(768)
     assert bytes(memory[0x4000:0x4200])==expected_state and bytes(memory[0x4200:0x4300])==expected_code
     assert r[IFF]==0 and r[IM]==1 and r[I]==0x3F and memory[0x9906]==(old_add if extra==255 else (old_add+30)&255)
    cases+=1
 report=dict(passed=True,cases=cases,guarded_returns=returns,
  method='original_W_and_fixed_transition_until_relocated_4200',all_selection_bytes=True,
  copied_state_and_code_checked=True,page_shadow_deliberately_not_updated=True,
  relocated_loader_executed=False,interface_callback_executed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StationTransitionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

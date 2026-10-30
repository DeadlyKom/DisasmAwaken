"""Оригинальные сканеры порогов, включая различие порядка баз во втором входе."""
from pathlib import Path
import sys,json,random
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import signature
from CheckGlyphRenderer import compare_flags


def main():
 _,_,base=make_context();base=[bytearray(b) for b in base]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 lang=(ROOT/(e['path']+'.sectors.bin')).read_bytes();base[6][:len(lang)]=lang
 memory=SliceableMemory(banks=[b.copy() for b in base],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFC,'BC':0x365D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 rng=random.Random(0xC4EF);count=0
 for entry,thresholds,weights,n in ((0xC4EF,0x95F0,0x988E,30),(0xC596,0x98F6,0x9632,14)):
  for variant in range(256):
   for pattern in range(6):
    memory.banks=[b.copy() for b in base];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x16)
    memory[0x6306]=0x16;put(memory,0x7FFC,[0xE3,0xA7,255,63])
    put(memory,0x983F,[0x38,0x4B,0x57,0x13,variant]);size=signature(0x4B38,0x1357,variant)['size']
    for i in range(n):
     memory[thresholds+2*i]=(size if pattern==0 else size+1 if pattern==1 else rng.randrange(256))
     memory[weights+i]=(0 if pattern==2 else 255 if pattern==3 else rng.randrange(1,255))
    failure=next((i for i in range(n) if memory[weights+i] not in (0,255) and size<memory[thresholds+2*i]),None)
    sim.registers[:]=initial;trace=PortTrace(sim);sim.set_tracer(trace);sim.run(start=entry,stop=0x3FFF);r=sim.registers
    expected=int(failure is None);expected_hl=thresholds+2*(failure if failure is not None else n)
    assert (r[A],r[D],r[E],r[H]*256+r[L],r[B],r[C],r[SP])==(expected,0,expected,expected_hl,n-failure if failure is not None else 0,0x5D,0x8000)
    if failure is not None:assert r[F]==compare_flags(size,memory[thresholds+2*failure])
    else:assert r[F]==(0x44 if memory[weights+n-1] in (0,255) else compare_flags(size,memory[thresholds+2*(n-1)]))
    assert memory[0xC509]==size and memory.o7ffd==0x16 and memory[0x6306]==0x16
    assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
    assert trace.writes==[(0x7FFD,0x11),(0x7FFD,0x10),(0x7FFD,0x16)]
    count+=1
 report=dict(passed=True,cases=count,method='original_threshold_sets_with_real_key_size',second_entry_uses_thresholds_98F6_and_weights_9632=True,
  all_variants=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ThresholdSetsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

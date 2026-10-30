"""Исходная команда T, включая фактический HL после поиска команды."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckWeightedLoad import reference


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 memory=original.copy();sim=Simulator(memory);rng=random.Random(0xC0DB)
 initial=get_registers({'SP':0x7FF0,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 direct=dispatched=0
 for dispatch in (False,True):
  for case in range(256):
   memory[:]=original
   for address in list(range(0x94FA,0x9518))+list(range(0x9829,0x9904)):memory[address]=rng.randrange(256)
   for base,count in ((0x95F1,30),(0x9633,14)):
    for i in range(count):memory[base+2*i]=rng.randrange(4)
   memory[0x984A]=case;memory[0xB000:0xB002]=b'T\0';memory[0xC01C:0xC01E]=bytes([240,127])
   sim.registers[:]=initial;r=sim.registers;index=0xC0DB if dispatch else case%33
   if dispatch:
    sim.run(start=0xC00C,stop=0xC0DB)
    assert r[H]*256+r[L]==0xC0DB and r[8]*256+r[9]==0xB001
   else:r[H],r[L]=index>>8,index&255
   expected=reference(memory,index);sim.run(start=0xC0DB,stop=0xC00C)
   value,flags,total,hl,de=expected
   assert memory[0x9850]==value and (r[A],r[F],r[C],r[B],r[H]*256+r[L],r[D]*256+r[E])==(value,flags,total,0,hl,de)
   assert r[SP]==0x7FF0 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24]
   assert memory[0xC884]+256*memory[0xC885]==(0x9852+2*index)&65535
   if dispatch:dispatched+=1
   else:direct+=1
 report=dict(passed=True,direct_cases=direct,command_dispatch_cases=dispatched,
  method='original_command_T_dispatch_and_complete_weighted_load',normal_HL_is_handler_address=True,
  command_DE_67AE_is_overwritten=True,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/TonnageCommandVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

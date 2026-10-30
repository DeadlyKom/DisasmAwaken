"""Все байты трёх исходных диспетчеров до входа обработчика либо SkipLine."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckGlyphRenderer import compare_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 found=missing=0
 for entry,anchor,count in ((0xC7B6,0xCA4F,7),(0xC7C3,0xCA3A,7),(0xC7D0,0xC980,36)):
  records=[(memory[anchor+3*i],memory[anchor+3*i+1]+256*memory[anchor+3*i+2]) for i in range(1,count+1)]
  for code in range(256):
   sim.registers[:]=initial;r=sim.registers;memory[0xB000]=code;memory[0x7FFE:0x8000]=bytes([255,63])
   match=next(((i,handler) for i,(symbol,handler) in enumerate(records) if symbol==code),None)
   target=match[1] if match else 0xC01B;sim.run(start=entry,stop=target)
   assert r[8]*256+r[9]==0xB001 and r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
   assert r[D]==0 and r[E]==3 and r[C]==0xC9
   if match:
    i,handler=match
    assert (r[A],r[F],r[B],r[H]*256+r[L],r[SP])==(handler&255,compare_flags(code,code),count-i,handler,0x7FFE)
    found+=1
   else:
    assert (r[A],r[F],r[B],r[H]*256+r[L],r[SP])==(code,compare_flags(code,records[-1][0]),0,anchor+3*count,0x7FFC)
    assert memory[0x7FFC:0x7FFE]==bytes([0xDD,0xC7]);missing+=1
 report=dict(passed=True,method='original_three_field_dispatchers_until_handler_or_skip',found_cases=found,missing_cases=missing,
  all_256_bytes_per_dispatcher=True,error_retains_find_token_return=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/FieldDispatchersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Исходные загрузчики байтов и слова в отдельный стек выражений."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A00,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 byte_cases=word_cases=0
 for entry,address in ((0xC241,0x9850),(0xC24C,0x9851),(0xC25B,0x983A),(0xC261,0x984B),(0xC244,None)):
  for value in range(256):
   for flags in range(256):
    sim.registers[:]=initial;r=sim.registers;r[F]=flags;r[A]=value if address is None else 0x5A
    if address is not None:memory[address]=value
    memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=entry,stop=0x3FFF)
    assert (r[A],r[F],r[SP])==(value,flags,0x8000) and memory[0xB800:0xB802]==bytes([value,0])
    assert r[2:12]==initial[2:12] and r[16:22]==initial[16:22] and r[22]*256+r[23]==0xB802
    byte_cases+=1
 for entry,value in ((0xC252,1),(0xC257,0)):
  for flags in range(256):
   sim.registers[:]=initial;r=sim.registers;r[F]=flags;memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=entry,stop=0x3FFF)
   assert (r[A],r[F],r[SP])==(value,flags if value else 0x44,0x8000) and memory[0xB800:0xB802]==bytes([value,0])
   assert r[2:12]==initial[2:12] and r[16:22]==initial[16:22] and r[22]*256+r[23]==0xB802
   byte_cases+=1
 for value in range(65536):
  sim.registers[:]=initial;r=sim.registers;r[F]=value&255;memory[0x984E:0x9850]=value.to_bytes(2,'little');memory[0x7FFE:0x8000]=bytes([255,63])
  sim.run(start=0xC1B5,stop=0x3FFF)
  assert memory[0xB800:0xB802]==value.to_bytes(2,'little') and r[D]*256+r[E]==value and r[20]*256+r[21]==value
  assert (r[A],r[F],r[SP])==(0x5A,value&255,0x8000) and r[H]*256+r[L]==0x1357 and r[B]*256+r[C]==0x36C9
  assert r[8:12]==initial[8:12] and r[16:20]==initial[16:20] and r[22]*256+r[23]==0xB802
  word_cases+=1
 report=dict(passed=True,method='original_byte_pushes_and_word_fallthrough_into_expression_push',byte_cases=byte_cases,word_cases=word_cases,
  alternate_DE_difference_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ExpressionPushesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

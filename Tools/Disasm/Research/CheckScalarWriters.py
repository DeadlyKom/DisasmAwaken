"""Исходные фабрики исполняемых писателей и их CPU-стековые вызовы операторов."""
from pathlib import Path
from itertools import product
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 factory=invocations=operators=0
 for entry,invoke,store,field,word in ((0xC642,0xC648,0xC652,0x984E,True),(0xC657,0xC65D,0xC669,0x984B,False),(0xC66E,0xC674,0xC680,0x9851,False)):
  for flags in range(256):
   sim.registers[:]=initial;r=sim.registers;r[F]=flags;memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=entry,stop=0x3FFF)
   assert memory[0xB800:0xB802]==invoke.to_bytes(2,'little') and r[D]*256+r[E]==invoke and r[20]*256+r[21]==invoke
   assert (r[A],r[F],r[SP],r[22]*256+r[23])==(0x5A,flags,0x8000,0xB802) and r[H]*256+r[L]==0x1357
   assert r[B:C+1]==initial[B:C+1] and r[8:12]==initial[8:12] and r[16:20]==initial[16:20]
   factory+=1
  # Проверка полного слова и всех комбинаций старого/нового байта с тремя старшими байтами RHS.
  inputs=((0xA55A,right) for right in range(65536)) if word else ((old,low+256*high) for old,low,high in product(range(256),range(256),(0,1,255)))
  for old,right in inputs:
   memory[field:field+2]=(old if word else old|0xE300).to_bytes(2,'little')
   sim.registers[:]=initial;r=sim.registers;r[SP]=0x7FFA;r[B],r[C]=right>>8,right&255
   memory[0x7FFA:0x7FFE]=bytes([0xD4,0xC4,255,63]);sim.run(start=invoke,stop=0x3FFF)
   assert int.from_bytes(memory[field:field+(2 if word else 1)],'little')==(right if word else right&255)
   assert (r[D]*256+r[E],r[H]*256+r[L],r[B]*256+r[C],r[A],r[F],r[SP])==(right,0xC4D4,right,0x5A if word else right&255,0x5C,0x7FFE)
   assert memory[0x7FFA:0x7FFC]==store.to_bytes(2,'little') and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
   invocations+=1
  # Проверка реальных операций сложения/вычитания с насыщением, без заглушек.
  for old,right,operator in product((0,1,127,128,255,256,32767,65535),(0,1,127,255,256,32767,65535),(0xC488,0xC491)):
   left=old if word else old&255
   sim.registers[:]=initial;r=sim.registers;r[H],r[L]=operator>>8,operator&255;r[D],r[E]=left>>8,left&255;r[B],r[C]=right>>8,right&255
   memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=operator,stop=0x3FFF);expected=sim.registers.copy();result=expected[D]*256+expected[E]
   assert result==(min(left+right,65535) if operator==0xC488 else max(left-right,0))
   memory[field:field+2]=(old if word else left|0xE300).to_bytes(2,'little')
   sim.registers[:]=initial;r=sim.registers;r[SP]=0x7FFA;r[B],r[C]=right>>8,right&255
   memory[0x7FFA:0x7FFE]=bytes([operator&255,operator>>8,255,63]);sim.run(start=invoke,stop=0x3FFF)
   assert int.from_bytes(memory[field:field+(2 if word else 1)],'little')==(result if word else result&255)
   assert r[2:8]==expected[2:8] and r[F]==expected[F] and r[A]==(expected[A] if word else result&255) and r[SP]==0x7FFE
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
   operators+=1
 report=dict(passed=True,method='original_scalar_writer_factories_closures_and_real_operators',factory_cases=factory,
  copy_invocations=invocations,arithmetic_invocations=operators,byte_store_discards_high_DE=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ScalarWritersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

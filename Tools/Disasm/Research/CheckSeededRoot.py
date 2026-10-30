"""Табличный корень по фактическим байтам KARTA, включая неточные верхние страницы."""
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckWorldSignature import logical_flags
from CheckMarketAccess import add16_flags


def inc_flags(value,flags):
 result=(value+1)&255
 return (flags&1)|(result&0xA8)|(0x40 if not result else 0)|(0x10 if value&15==15 else 0)|(4 if value==127 else 0)


def reference(source,number,input_hl):
 high=number>>8
 if high:
  seed=255-source[0x2B00+high];base=source[0x2C00+high]+256*source[0x2D00+high]
  # Состояние после выбора исходных таблиц, не заменять их идеальным квадратом.
  flags=0x80|(seed&0x28)|0x12
  remainder=(base+number)&65535;flags=add16_flags(base,number,flags)
  odd=(-2*seed-1)&65535;a=seed;output_de=number;limit=6
 else:
  remainder=number;flags=0x44;odd=65535;a=0;output_de=input_hl;limit=15
 for trial in range(limit):
  total=remainder+odd;flags=add16_flags(remainder,odd,flags);remainder=total&65535
  if total<65536:return a,flags,remainder,odd,output_de
  if trial+1<limit:
   flags=inc_flags(a,flags);a=(a+1)&255;odd=(odd-2)&65535
 flags=inc_flags(a,flags);a=(a+1)&255
 return a,flags,remainder,odd,output_de


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);mismatches=[]
 for number in range(65536):
  sim.registers[:]=initial;r=sim.registers;r[D],r[E]=number>>8,number&255
  sim.run(start=0xE838,stop=0x3FFF);expected=reference(source,number,0x1357)
  assert (r[A],r[F],r[H]*256+r[L],r[B]*256+r[C],r[D]*256+r[E])==expected,(number,list(r),expected)
  assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
  if number>>8:
   assert (r[16],r[17])==(source[0x2C00+(number>>8)],0xA8 if source[0x2B00+(number>>8)]==255 else 0xA9)
  else:assert r[16:18]==initial[16:18]
  if r[A]!=math.isqrt(number):mismatches.append(number)
 report=dict(passed=True,cases=65536,method='original_seeded_root_against_actual_table_recurrence_and_integer_sqrt',
  integer_sqrt_mismatches=len(mismatches),first_mismatch=mismatches[0] if mismatches else None,
  last_mismatch=mismatches[-1] if mismatches else None,
  mismatch_high_bytes=sorted({n>>8 for n in mismatches}),
  input_0_through_7281_matches_integer_sqrt=not any(n<=7281 for n in mismatches),
  table_bytes_preserved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SeededRootVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

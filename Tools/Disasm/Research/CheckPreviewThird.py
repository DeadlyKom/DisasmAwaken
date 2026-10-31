"""Окно третьей координаты D3D с проверкой исходных шагов и всех оборачивающихся сумм."""
from pathlib import Path
from itertools import chain
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from Analyze import payload
from CheckGlyphRenderer import compare_flags


def main():
 raw=payload(6);m=bytearray(65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=bytes([255,63]);s=Simulator(m);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=accepted=wrapped=0;expected=bytearray(m[0xC000:])
 inputs=chain(((word,step) for word in range(65536) for step in (32,65504)),((word,step) for word in (0,512,4095) for step in range(65536)))
 for word,step in inputs:
  m[0xCDC4:0xCDC6]=word.to_bytes(2,'little');s.registers[:]=initial;r=s.registers;r[H],r[L]=step>>8,step&255
  # Независимая модель принимает обёрнутую сумму по всему допустимому числовому интервалу.
  result=(word+step)&65535;valid=512<=result<=4095;stored=result if valid else word;expected[0xDC4:0xDC6]=stored.to_bytes(2,'little');s.run(start=0xE0B5,stop=0x3FFF)
  high=result>>8;flags=compare_flags(high,2 if high<2 else 16)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==(result,word,high,flags,0x8000)
  assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and m[0xC000:]==expected
  cases+=1;accepted+=valid;wrapped+=word+step>65535
 report=dict(passed=True,cases=cases,accepted=accepted,wrapped_additions=wrapped,all_words_for_both_original_steps=True,all_step_words_for_three_initial_values=True,full_bank_compared=True,full_flags_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewThirdVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

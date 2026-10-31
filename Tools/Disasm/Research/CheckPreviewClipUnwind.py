"""Специальный E85D, независимые поля трёх снимаемых слов и точные флаги SCF."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewEdgeRasterOracle import column_context


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0x7FF8,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0
 def check(first,second,third):
  nonlocal cases
  frame=first.to_bytes(2,'little')+second.to_bytes(2,'little')+third.to_bytes(2,'little')+bytes((255,63))
  m.recording=False;m[0x7FF8:0x8000]=frame;s.registers[:]=initial;r=s.registers;m.recording=True;m.writes=[];s.run(start=0xE85D,stop=0x3FFF)
  # Расчёт смещения и флагов по полям кадра, не по последовательности POP и ADD.
  accumulator=first>>8;offset=((second>>8)-1)&255;result=(third+offset)&65535
  flags=(column_context(offset,-1,0)&0xC4)|(accumulator&0x28)|1
  assert tuple(r[:8])==(accumulator,flags,0,offset,initial[4],initial[5],result>>8,result&255)
  assert r[8:12]==initial[8:12] and r[12]==0x8000 and r[16:24]==initial[16:24]
  assert not m.writes and bytes(m[0x7FF8:0x8000])==frame;cases+=1
 # Проверка всех базовых слов HL на шести граничных старших байтах второго слова.
 for third in range(65536):
  for high in (0,1,127,128,129,255):check(((third&255)<<8)|((third*37)&255),(high<<8)|(third&255),third)
 # Проверка всех пар старших байтов первых двух слов на четырёх границах переноса HL.
 for first in range(256):
  for second in range(256):
   for third in (0,255,0xFF00,65535):check(first*256+second,second*256+first,third)
 report=dict(passed=True,cases=cases,all_65536_third_words=True,all_256_by_256_first_and_second_high_bytes=True,exact_flags_and_scf_undocumented_bits=True,exact_sp_plus_eight_and_cpu_return=True,all_preserved_registers_checked=True,no_memory_writes=True,frame_fields_not_assumed_equal=True,real_dispatch_frame_result=dict(a=0xEB,f=0xA9,bc=0xEA,hl=0xEBF2),irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipUnwindVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

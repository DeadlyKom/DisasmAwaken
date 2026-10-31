"""Проверка каждого байта заголовка и трёх исходных JR масштаба без исполнения перспективы."""
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewModelMatrixOracle import arithmetic


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x6000,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 # Проверка исходной формы трёх самомодифицируемых JR, каждый сопровождается пятью ADD HL,HL.
 for entry in (0xDA1F,0xDA3A,0xDAF8):assert raw[entry-0xC000:entry-0xC000+7]==bytes.fromhex('18fe2929292929')
 cases=0
 for header in range(256):
  for flags in range(0,256,17):
   m.recording=False;m[0x6000]=header;s.registers[:]=initial;r=s.registers;r[F]=flags;m.recording=True;m.writes=[];s.run(start=0xDBD9,stop=0x3FFF)
   value,f=arithmetic(6,header&127,True)
   assert (r[A],r[F],r[B],r[C],r[D],r[E],r[H],r[L],r[SP])==(value,f,header&127,0xC9,0x24,0x7A,0x60,0,0x8000)
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
   assert m.writes==[(0xDA20,value),(0xDA3B,value),(0xDAF9,value)]
   cases+=1
 headers=[]
 for model in range(11):
  pointer=int.from_bytes(raw[0x1000+4*model:0x1002+4*model],'little');header=raw[pointer-0xC000+1];assert header&127 in (2,3)
  headers.append(dict(model=model,pointer=pointer,header=header,exponent=header&127))
 report=dict(passed=True,cases=cases,all_header_bytes_checked=True,all_three_original_self_jumps_checked=True,exact_sub_flags_and_preserved_context=True,exact_three_operand_writes=True,original_headers=headers,consumer_safe_exponents=[1,2,3,4,5,6],invalid_exponents_not_repaired=True,perspective_not_executed=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewProjectionScaleVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in report.items() if k!='original_headers'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

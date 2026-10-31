"""Четыре табличных произведения D518..D54B и точная формула исходной страницы C3."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory,signed


def table(index):
 folded=min(index,255-index)
 return folded*folded//127


def main():
 raw=payload(6);assert list(raw[0x300:0x400])==[table(i) for i in range(256)]
 m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0xC3AD,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0;maximum_error=0
 for entry,factor in ((0xD518,E),(0xD525,B),(0xD532,C),(0xD53F,D)):
  for a in range(256):
   for value in range(256):
    s.registers[:]=initial;r=s.registers;r[A]=a;r[F]=(a*11+value*37)&255;r[factor]=value;expected_context=list(r[2:6])
    # Расчёт индексов суммы и разности знаковых половин, второй индекс использует полный исходный множитель.
    half_a=signed(a,8)//2;half_b=signed(value,8)//2;difference=(half_a-half_b)&255;summed=(half_a-half_b+value)&255
    first=table(difference);second=table(summed);answer=(second-first)&255
    flags=(answer&0xA8)|(0x40 if answer==0 else 0)|(0x10 if (second&15)<(first&15) else 0)|2|int(second<first)
    expected_context[E-2]=first;m.recording=True;m.writes=[];s.run(start=entry,stop=0x3FFF)
    assert (r[A],r[F],r[H],r[L],r[SP])==(answer,flags,0xC3,summed,0x8000)
    assert r[2:6]==expected_context and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and m.writes==[]
    if a!=128 and value!=128:maximum_error=max(maximum_error,abs(signed(answer,8)*127-signed(a,8)*signed(value,8)))
    cases+=1
 report=dict(passed=True,cases=cases,all_operand_byte_pairs_in_four_entries=True,table_bytes_checked=256,table_formula='floor(min(i,255-i)^2/127)',independent_table_difference_and_sub_flags=True,maximum_product_error_numerator_over_127=maximum_error,no_memory_writes=True,all_preserved_context_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewLookupProductsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

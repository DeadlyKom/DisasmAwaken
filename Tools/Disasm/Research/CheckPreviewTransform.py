"""Три скалярных произведения EB7E, перенос отрицательного помощника и раннее переполнение."""
from pathlib import Path
import json,sys,random,collections
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory,signed
INPUTS=(0xEB7F,0xEB8D,0xEBA0)
COEFFICIENTS=((0xD567,0xD574,0xD586),(0xD599,0xD5A6,0xD5B8),(0xD5CB,0xD5D8,0xD5EA))
OUTPUTS=(0xDAF6,0xDA38,0xDA16)
CONTINUATIONS=((0xEB8B,0xEB99,0xEBAC),(0xEBC2,0xEBD1,0xEBE5),(0xEBFB,0xEC0A,0xEC1E))


def adc16(x,y,carry):
 total=x+y+carry;value=total&65535
 flags=((value>>8)&0xA8)|(0x40 if value==0 else 0)|(0x10 if (x&4095)+(y&4095)+carry>4095 else 0)|(4 if (~(x^y)&(x^value)&32768) else 0)|int(total>65535)
 return value,flags


def main():
 m=Memory([0]*65536);raw=payload(6);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x3FFF,'^HL':0x47AD,'^DE':0x369C,'^BC':0x58BE,'^AF':0x69CF},None,False);outcomes=collections.Counter();cases=0
 def check(coords,matrix):
  nonlocal cases
  m.recording=False
  for ptr,value in zip(INPUTS,coords):m[ptr]=value&255;m[ptr+1]=value>>8
  for ptrs,values in zip(COEFFICIENTS,matrix):
   for ptr,value in zip(ptrs,values):m[ptr]=value
  expected_outputs=[0xA15B,0xB26C,0xC37D]
  for ptr,value in zip(OUTPUTS,expected_outputs):m[ptr]=value&255;m[ptr+1]=value>>8
  expected_writes=[];stop=None
  # Расчёт трёх строк с тем самым Carry знакового помощника, а не обычное матричное сложение.
  for row in range(3):
   for term in range(3):
    coefficient=matrix[row][term];word=coords[term];cv=signed(coefficient,8);vv=signed(word,16);product=0 if coefficient==128 else abs(cv)*abs(vv);magnitude=product//128;negative=bool((coefficient^(word>>8))&128);part=(-magnitude if negative else magnitude)&65535;carry=int(negative and magnitude!=0);de=magnitude if negative else abs(vv);a=coefficient^(word>>8);upper=product>>15;alt_flags=(upper&0x28)|(0x40 if upper==0 else 0)|(0x10 if ((product>>16)&15)*2+((product>>15)&1)>15 else 0);continuation=CONTINUATIONS[row][term];expected_writes.extend(((0xEB7C,continuation&255),(0xEB7D,continuation>>8)))
    if term==0:stack=part
    else:
     result,flags=adc16(part,stack,carry)
     if flags&4:stop=(row,term);break
     if term==1:stack=result
   if stop is not None:break
   expected_outputs[row]=result;expected_writes.extend(((OUTPUTS[row],result&255),(OUTPUTS[row]+1,result>>8)))
  s.registers[:]=initial;m.writes=[];m.recording=True;s.run(start=0xEB7E,stop=0x3FFF);r=s.registers
  assert (r[H]*256+r[L],r[D]*256+r[E],r[2]*256+r[3],r[A],r[F],r[16],r[17],r[SP])==(result,de,0x3600,a,flags,upper,alt_flags,stack),(coords,matrix,stop,tuple(r[:8]),result,flags,r[SP],stack)
  assert r[18:24]==[0x58,0xBE,continuation>>8,continuation&255,0x47,0xAD] and r[8:12]==initial[8:12] and m.writes==expected_writes
  assert [m[p]+256*m[p+1] for p in OUTPUTS]==expected_outputs
  outcomes['complete' if stop is None else f'overflow_row_{stop[0]+1}_term_{stop[1]+1}']+=1;cases+=1
 identity=((127,0,0),(0,127,0),(0,0,127));all_positive=((127,127,127),)*3
 # Проверка всех слов в координатах для разреженной и максимально плотной положительной матрицы.
 for value in range(65536):
  check((value,value,value),identity);check((value,value,value),all_positive)
 # Проверка смешанных знаков, порядка ранних выходов и нештатного коэффициента 80 на воспроизводимой выборке.
 rng=random.Random(0xEB7E)
 for _ in range(16384):check(tuple(rng.randrange(65536) for _ in range(3)),tuple(tuple(rng.randrange(256) for _ in range(3)) for _ in range(3)))
 report=dict(passed=True,cases=cases,outcomes=dict(outcomes),all_coordinate_words_in_two_matrix_families=True,independent_integer_product_and_adc16_flags=True,negative_helper_carry_included=True,untouched_outputs_after_overflow_checked=True,exact_self_modification_and_output_writes=True,sp_is_partial_sum_not_cpu_stack=True,alternate_and_index_registers_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewTransformVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

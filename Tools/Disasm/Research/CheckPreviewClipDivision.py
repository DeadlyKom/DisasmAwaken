"""Оригинальный EA01, числовая модель, точные флаги и проверка совпадения перенесённого алгоритма Map."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from InspectZ80 import decoder
from CheckPreviewCoordinateMultiply import Memory
from CheckSignedDivision import expected


def main():
 raw=payload(6);other=payload(7);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 # Проверка фактических байтов обеих версий, перенос допускается только для абсолютных JP внутри функции.
 map_memory=bytearray(65536);map_memory[0xC000:0xC000+len(other)]=other
 left=decoder(map_memory).disassemble(0xDCFB,0xDDB0,'h');right=decoder(m).disassemble(0xEA01,0xEAB6,'h');assert len(left)==len(right)
 shifted=0
 for a,b in zip(left,right):
  assert b.address-a.address==0xD06 and len(a.bytes)==len(b.bytes)
  if a.operation.startswith('JP '):
   assert a.bytes[0]==b.bytes[0] and int.from_bytes(b.bytes[1:],'little')-int.from_bytes(a.bytes[1:],'little')==0xD06;shifted+=1
  else:assert a.bytes==b.bytes
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE},None,False);cases=wide=0
 def check(number,divisor,selector):
  nonlocal cases
  raw_number=number&0xFFFFFFFF;carry=selector&1;alt_carry=(selector>>1)&1;s.registers[:]=initial;r=s.registers
  r[6]=raw_number>>24;r[7]=(raw_number>>16)&255;r[0]=(raw_number>>8)&255;r[1]=(128 if divisor<0 else 0)|carry
  r[16]=raw_number&255;r[17]=0x5C|alt_carry;r[4]=(divisor>>8)&255;r[5]=divisor&255;r[8]=(selector>>2)&255
  ix_high=r[8];m.recording=True;m.writes=[];s.run(start=0xEA01,stop=0x3FFF)
  result,flags,alt_flags,bc,denominator,ix=expected(number,divisor,carry,alt_carry,0x36C9)
  assert tuple(r[:8])==(result>>8,flags,bc>>8,bc&255,denominator>>8,denominator&255,result>>8,result&255),(number,divisor,r[:8],result,flags)
  assert (r[16],r[17],r[8],r[9])==(result&255,alt_flags,ix_high,ix&255)
  assert r[10:12]==initial[10:12] and r[12]==0x8000 and r[18:24]==initial[18:24] and not m.writes;cases+=1
 divisors=(1,2,9,255,256,32767,-1,-9,-255,-32768)
 # Проверка всех младших слов числителя и их отрицательных дополнений на десяти делителях.
 for divisor in divisors:
  for value in range(65536):check(value,divisor,value);check(-value-1,divisor,value)
 rng=random.Random(0xEA01)
 for divisor in divisors:
  for _ in range(1024):
   value=rng.randrange(abs(divisor)*65536);check(value,divisor,value);check(-value-1,divisor,value);wide+=2
 report=dict(passed=True,cases=cases,wide_input_cases=wide,original_map_and_d3d_instruction_bytes_equal_after_internal_jp_relocation=True,relocated_absolute_jumps=shifted,actual_d3d_execution=True,independent_numeric_quotient_and_flag_formula=True,negative_numerator_and_quotient_use_ones_complement=True,denominator_sign_is_input_s=True,exact_main_alternate_and_index_context=True,all_ix_high_bytes_preserved=True,no_memory_writes=True,zero_divisor_tested=False,quotient_overflow_tested=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipDivisionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Деление HL:A:A' на DE, независимые частное и флаги при допустимом 16-битном результате."""
from pathlib import Path
import json,random,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckSignedMultiply import sbc16_flags
from ReferenceControlsPointRespawn import refresh


def refresh_layout(source):
 # Проверка физических команд и обеих развёрнутых восьмибитных половин деления.
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 entry=next(row for row in manifest['entries'] if row['slot']==7)
 assert source==disk[entry['offset']:entry['offset']+len(source)]
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
 rows=[row for region in flow if region['name']=='Map' for row in region['instructions']
       if 0xDCFB<=row['address']<0xDDB0]
 for row,following in zip(rows,rows[1:]+[dict(address=0xDDB0)]):
  raw=bytes.fromhex(row['hex'])
  assert row['slot']==7 and row['offset']==row['address']-0xC000
  assert source[row['offset']:row['offset']+len(raw)]==raw
  assert row['address']+len(raw)==following['address']
 def block(first,end):return b''.join(bytes.fromhex(row['hex']) for row in rows if first<=row['address']<end)
 assert block(0xDCFB,0xDD1F).hex()=='dd2e00f20dddeb444d210000b7ed42ebdd2ccb7c280e082f082f444d21000037ed42dd2c'
 bit=bytes.fromhex('17ed6aed52300119')
 assert block(0xDD1F,0xDD5F)==bit*8
 assert block(0xDD5F,0xDD61).hex()=='1708'
 assert block(0xDD61,0xDDA1)==bit*8
 assert block(0xDDA1,0xDDB0).hex()=='17dd2d20046f0867c92f6f082f67c9'
 # Расчёт независимых частей префикса, все DD/CB/ED добавляют отдельную выборку M1.
 def m1(first,end):return sum(2 if bytes.fromhex(row['hex'])[0] in (0xCB,0xED,0xDD,0xFD) else 1
                            for row in rows if first<=row['address']<end)
 assert m1(0xDCFB,0xDD01)+m1(0xDD0D,0xDD11)==6
 assert m1(0xDD01,0xDD0D)==10 and m1(0xDD11,0xDD1F)==12
 assert m1(0xDD1F,0xDD26)==6 and m1(0xDD26,0xDD27)==1
 assert m1(0xDD5F,0xDD61)==2 and m1(0xDDA1,0xDDA6)==4
 assert m1(0xDDA6,0xDDAA)==4 and m1(0xDDAA,0xDDB0)==6
 return sha256(block(0xDCFB,0xDDB0)).hexdigest()


def refresh_cost(number,divisor):
 # Расчёт числа восстановлений остатка по битам положительного математического частного.
 negative_numerator=int(number<0);negative_divisor=int(divisor<0)
 unsigned=(-number-1 if negative_numerator else number)//abs(divisor)
 assert 0<=unsigned<65536
 return 130+12*negative_numerator+10*negative_divisor-2*(negative_numerator^negative_divisor)-unsigned.bit_count()


def expected(number,divisor,carry,alt_carry,initial_bc):
 raw=number&0xFFFFFFFF;negative_count=int(number<0)+int(divisor<0);magnitude=(~raw)&0xFFFFFFFF if number<0 else raw
 denominator=abs(divisor);q=magnitude//denominator
 if q>=65536:raise ValueError('Вне проверяемого договора, частное не помещается в слово')
 result=q if negative_count%2==0 else q^65535
 # Флаги верхнего байта берутся из восьмой попытки деления до EX AF,AF'.
 trial=2*((magnitude>>9)%denominator)+((magnitude>>8)&1)
 flags=(sbc16_flags(trial,denominator,0)&0xC4)|((result>>8)&0x28)|(1 if negative_count else carry)
 if negative_count%2==0:flags|=0x12
 alt_flags=(0x80 if negative_count==0 else 0)|((result&255)&0x28)|0x12|alt_carry if negative_count%2==0 else 0x42|alt_carry
 bc=(raw>>16) if number<0 else (divisor&65535) if divisor<0 else initial_bc
 return result,flags,alt_flags,bc,denominator,0x2400|((negative_count-1)&255)


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);cases=wide=0
 code_sha=refresh_layout(source);initial_r_values=set();costs=set();refresh_cases=0
 def check(number,divisor,selector):
  nonlocal refresh_cases
  raw=number&0xFFFFFFFF;carry=selector&1;alt_carry=(selector>>1)&1
  sim.registers[:]=initial;r=sim.registers
  r[H],r[L]=(raw>>24)&255,(raw>>16)&255;r[A]=(raw>>8)&255;r[F]=(0x80 if divisor<0 else 0)|carry
  r[16]=raw&255;r[17]=0x5C|alt_carry;r[D],r[E]=(divisor>>8)&255,divisor&255
  # Проверка всех разрядов R, его начальное значение не является числовым аргументом алгоритма.
  initial_r=((raw^(raw>>16)^abs(divisor))*73)&255;initial_r_values.add(initial_r);r[15]=initial_r
  sim.run(start=0xDCFB,stop=0x3FFF)
  m1=refresh_cost(number,divisor);costs.add(m1);refresh_cases+=1
  assert r[15]==refresh(initial_r,m1),(number,divisor,initial_r,m1,r[15])
  result,flags,alt_flags,bc,denominator,ix=expected(number,divisor,carry,alt_carry,0x36C9)
  assert (r[H]*256+r[L],r[A],r[F],r[16],r[17],r[B]*256+r[C],r[D]*256+r[E],r[8]*256+r[9])==(result,result>>8,flags,result&255,alt_flags,bc,denominator,ix),(number,divisor,selector,list(r),(result,flags,alt_flags,bc,denominator,ix))
  assert r[SP]==0x8000 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24]
 divisors=(1,2,9,255,256,32767,-1,-9,-255,-32768)
 for divisor in divisors:
  for value in range(65536):
   check(value,divisor,value);check(-value-1,divisor,value);cases+=2
 rng=random.Random(0xDCFB)
 for divisor in divisors:
  for _ in range(1024):
   value=rng.randrange(abs(divisor)*65536);check(value,divisor,value);check(-value-1,divisor,value);wide+=2
 assert refresh_cases==cases+wide and initial_r_values==set(range(256)) and min(costs)==114 and max(costs)==152
 report=dict(passed=True,word_input_cases=cases,wide_input_cases=wide,
  method='original_32_to_16_division_against_integer_quotient_and_independent_flag_formula',
  negative_numerator_uses_ones_complement=True,negative_quotient_uses_ones_complement=True,
  denominator_sign_is_input_F_sign=True,zero_divisor_tested=False,overflow_cases_tested=False,
  refresh_checked_cases=refresh_cases,all_initial_R_values_observed=True,
  independent_all_inputs_times_all_R_product_exhausted=False,
  refresh_original_code_sha256=code_sha,observed_M1_values=sorted(costs),
  refresh_formula='130+12*n+10*d-2*(n XOR d)-popcount(q)',
  refresh_unsigned_quotient_is_before_final_complement=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SignedDivisionVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

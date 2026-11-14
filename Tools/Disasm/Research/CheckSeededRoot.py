"""Табличный корень по фактическим байтам KARTA, включая неточные верхние страницы."""
from pathlib import Path
import json,math,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckWorldSignature import logical_flags
from CheckMarketAccess import add16_flags
from ReferenceControlsPointRespawn import refresh


def refresh_layout(source):
 # Проверка настоящих секторов и полного развёрнутого кода, повторные попытки не являются вызовами.
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 entry=next(row for row in manifest['entries'] if row['slot']==7)
 assert source==disk[entry['offset']:entry['offset']+len(source)]
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
 rows=[row for region in flow if region['name']=='Map' for row in region['instructions']
       if 0xE838<=row['address']<0xE8BE]
 for row,following in zip(rows,rows[1:]+[dict(address=0xE8BE)]):
  raw=bytes.fromhex(row['hex'])
  assert row['slot']==7 and row['offset']==row['address']-0xC000
  assert source[row['offset']:row['offset']+len(raw)]==raw
  assert row['address']+len(raw)==following['address']
 def block(first,end):return b''.join(bytes.fromhex(row['hex']) for row in rows if first<=row['address']<end)
 assert block(0xE838,0xE852).hex()=='7aa728336f26eb7e244f2f0806ff03cb21cb100b7e24666f0819'
 assert block(0xE852,0xE86F)==bytes.fromhex('09d00b0b3c')*5+bytes.fromhex('09d03cc9')
 assert block(0xE86F,0xE874).hex()=='eb01ffffaf'
 assert block(0xE874,0xE8BE)==bytes.fromhex('09d03c0b0b')*14+bytes.fromhex('09d03cc9')
 # Расчёт стоимости префикса, SLA C и RL B требуют по две выборки M1.
 prefix=sum(2 if bytes.fromhex(row['hex'])[0] in (0xCB,0xED,0xDD,0xFD) else 1
            for row in rows if row['address']<0xE852)
 assert prefix==23
 return sha256(block(0xE838,0xE8BE)).hexdigest()


def refresh_cost(source,number,result):
 # Расчёт числа успешных попыток из независимого числового результата, без наблюдения пути CPU.
 if number<256:
  assert 0<=result<=15
  return 80 if result==15 else 8+5*result
 seed=255-source[0x2B00+(number>>8)]
 successful=(result-seed)&255
 assert 0<=successful<=6
 return 52 if successful==6 else 25+5*successful


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
 code_sha=refresh_layout(source);costs=set();initial_r_values=set()
 for number in range(65536):
  sim.registers[:]=initial;r=sim.registers;r[D],r[E]=number>>8,number&255
  # Проверка младших семи разрядов и сохранения старшего при разных исходных R.
  initial_r=((number*73)^(number>>8))&255;initial_r_values.add(initial_r);r[15]=initial_r
  sim.run(start=0xE838,stop=0x3FFF);expected=reference(source,number,0x1357)
  m1=refresh_cost(source,number,expected[0]);costs.add(m1)
  assert r[15]==refresh(initial_r,m1),(number,initial_r,m1,r[15])
  assert (r[A],r[F],r[H]*256+r[L],r[B]*256+r[C],r[D]*256+r[E])==expected,(number,list(r),expected)
  assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
  if number>>8:
   assert (r[16],r[17])==(source[0x2C00+(number>>8)],0xA8 if source[0x2B00+(number>>8)]==255 else 0xA9)
  else:assert r[16:18]==initial[16:18]
  if r[A]!=math.isqrt(number):mismatches.append(number)
 assert initial_r_values==set(range(256)) and min(costs)==8 and max(costs)==80
 report=dict(passed=True,cases=65536,method='original_seeded_root_against_actual_table_recurrence_and_integer_sqrt',
  integer_sqrt_mismatches=len(mismatches),first_mismatch=mismatches[0] if mismatches else None,
  last_mismatch=mismatches[-1] if mismatches else None,
  mismatch_high_bytes=sorted({n>>8 for n in mismatches}),
  input_0_through_7281_matches_integer_sqrt=not any(n<=7281 for n in mismatches),
  refresh_checked_cases=65536,all_initial_R_values_observed=True,
  independent_all_inputs_times_all_R_product_exhausted=False,
  refresh_original_code_sha256=code_sha,observed_M1_values=sorted(costs),
  refresh_formula_uses_independent_numeric_result_and_original_table_seed=True,
  refresh_formulas=dict(small_early='8+5*A',small_exhausted=80,
    table_early='25+5*k, k=(A-(255-EB[d])) modulo 256',table_exhausted=52),
  table_bytes_preserved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SeededRootVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

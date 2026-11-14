"""Исходное знаковое умножение карты, включая граничный код 8000 и три ядра."""
from pathlib import Path
import json,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckWorldSignature import logical_flags
from ReferenceControlsPointRespawn import refresh


def refresh_layout(source):
 # Проверка физического источника и закрытой исходной области трёх ядер.
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 entry=next(row for row in manifest['entries'] if row['slot']==7)
 assert source==disk[entry['offset']:entry['offset']+len(source)]
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
 rows=[row for region in flow if region['name']=='Map' for row in region['instructions']
       if 0xDB63<=row['address']<0xDCFB]
 for row,following in zip(rows,rows[1:]+[dict(address=0xDCFB)]):
  raw=bytes.fromhex(row['hex'])
  assert row['slot']==7 and row['offset']==row['address']-0xC000
  assert source[row['offset']:row['offset']+len(raw)]==raw
  assert row['address']+len(raw)==following['address']
  assert raw[:2] not in (b'\xed\x4f',b'\xed\x5f')
 def m1(first,end):return sum(2 if bytes.fromhex(row['hex'])[0] in (0xCB,0xED,0xDD,0xFD) else 1
                            for row in rows if first<=row['address']<end)
 # Проверка цены нормализации знаков и точного выбора каждого ядра.
 assert m1(0xDB63,0xDB6A)+m1(0xDB71,0xDB75)==9
 assert m1(0xDB6A,0xDB71)==m1(0xDB75,0xDB7C)==7
 assert m1(0xDB7C,0xDB82)==4 and m1(0xDB82,0xDB87)==3
 assert m1(0xDC4F,0xDC53)==3 and m1(0xDC53,0xDC54)==1
 assert m1(0xDC3F,0xDC41)==2 and m1(0xDC41,0xDC4F)==10
 # Проверка полного ядра, семь поисковых сдвигов и четырнадцать развёрнутых хвостов.
 assert m1(0xDB87,0xDB8F)==4
 for pc in range(0xDB8F,0xDBAB,4):assert m1(pc,pc+4)==2
 for pc in range(0xDBAB,0xDC37,10):
  assert m1(pc,pc+4)==4 and m1(pc+4,pc+10)==5
 assert m1(0xDC37,0xDC3B)==4 and m1(0xDC3B,0xDC3F)==4
 # Проверка байтово-словного ядра, цена поиска, каждого добавления и сдвига.
 assert m1(0xDC54,0xDC57)==3
 for pc in range(0xDC57,0xDC6F,3):assert m1(pc,pc+3)==2
 assert m1(0xDC6F,0xDC72)==1
 for pc in range(0xDC72,0xDC9C,6):
  assert m1(pc,pc+2)==2 and m1(pc+2,pc+6)==3
 assert m1(0xDC9C,0xDC9E)==2 and m1(0xDC9E,0xDCA5)==4
 # Проверка байтового ядра, RR E требует две выборки, RRA одну.
 for pc in range(0xDCA5,0xDCC5,4):assert m1(pc,pc+4)==3
 assert m1(0xDCC5,0xDCC8)==1
 for pc in range(0xDCC8,0xDCF2,6):
  assert m1(pc,pc+1)==1 and m1(pc+1,pc+6)==4
 assert m1(0xDCF2,0xDCF6)==4 and m1(0xDCF6,0xDCFB)==3
 return sha256(b''.join(bytes.fromhex(row['hex']) for row in rows)).hexdigest()


def refresh_cost(left,right):
 # Расчёт числа сдвигов и сложений по модулям входов, путь исполняемого CPU не читается.
 x,y=abs(signed(left)),abs(signed(right))
 negative_left=int(bool(left&32768));negative_right=int(bool(right&32768))
 prefix=9+7*(negative_left+negative_right)
 suffix=2+10*(negative_left^negative_right)
 if x<256 and y<256:
  selection=7
  core=28 if x==0 else 37-((x&-x).bit_length()-1)+x.bit_count()
 elif x<256 or y<256:
  selection=8 if x<256 else 7
  byte=x if x<256 else y
  core=24 if byte==0 else 23+(byte.bit_length()-1)+2*byte.bit_count()
 else:
  selection=7
  # Учёт исходного принудительного AddWide08 после потери единственного бита 15.
  effective=256 if y==32768 else y
  bit=effective.bit_length()-1
  assert 8<=bit<=14
  core=38+3*bit+4*effective.bit_count()
 return prefix+selection+core+suffix


def step_refresh_witnesses(source,initial):
 # Проверка абсолютного счёта M1, одного совпадения R недостаточно при полном обороте 128.
 fixtures=((0,0),(0,65535),(1,1),(128,3),(255,255),(0,256),(256,0),(1,256),(256,1),
           (256,256),(256,32768),(32768,256),(32768,32767),(65535,32767),
           (32767,32769),(32768,32768),(256,4351))
 results=[]
 for left,right in fixtures:
  memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;memory[0x7FFE:0x8000]=bytes([255,63])
  cpu=Simulator(memory);cpu.registers[:]=initial;r=cpu.registers
  r[PC]=0xDB63;r[15]=0x95;r[H],r[L]=left>>8,left&255;r[D],r[E]=right>>8,right&255;m1=0
  for _ in range(1000):
   pc=r[PC]
   if pc==0x3FFF:break
   first,second=memory[pc],memory[(pc+1)&65535]
   assert first!=0x76 and (first,second) not in ((0xED,0x4F),(0xED,0x5F))
   assert not (first in (0xDD,0xFD) and second in (0xDD,0xFD,0xED))
   m1+=2 if first in (0xCB,0xED,0xDD,0xFD) else 1
   cpu.run()
   assert r[15]==refresh(0x95,m1)
  else:raise AssertionError(('Не завершился контроль M1',left,right))
  assert m1==refresh_cost(left,right) and r[SP]==0x8000,(left,right,m1)
  results.append(dict(left=left,right=right,observed_M1=m1))
 return results


def signed(value):return value if value<32768 else value-65536


def sbc16_flags(left,right,carry):
 total=left-right-carry;result=total&65535
 return ((result>>8)&0xA8)|(0x40 if result==0 else 0)|(((left^right^result)>>8)&0x10)|(((left^right)&(left^result)&0x8000)>>13)|2|(total<0)


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 step_witnesses=step_refresh_witnesses(source,initial)
 memory[0x7FFE:0x8000]=bytes([255,63]);cases=defects=0;paths={'8x8':0,'8x16':0,'16x16':0}
 code_sha=refresh_layout(source);costs={key:set() for key in paths};initial_r_values=set()
 for fixed in (0,1,255,256,32767,32768,65535):
  for variable in range(65536):
   for left,right in ((variable,fixed),(fixed,variable)):
    x,y=signed(left),signed(right);mx,my=abs(x),abs(y);large=mx>=256 and my>=256;small=mx<256 and my<256
    # Полное ядро пропускает старший бит и при отсутствии оставшихся старших битов принудительно добавляет разряд 8.
    defect=large and right==32768;magnitude=mx*256 if defect else mx*my
    expected=(-magnitude if (left^right)&32768 else magnitude)&0xFFFFFFFF
    sim.registers[:]=initial;r=sim.registers;r[H],r[L]=left>>8,left&255;r[D],r[E]=right>>8,right&255
    # Проверка изменения R по независимой формуле цены выбранного ядра.
    initial_r=(left^(right*73)^(right>>8))&255;initial_r_values.add(initial_r);r[15]=initial_r
    sim.run(start=0xDB63,stop=0x3FFF)
    m1=refresh_cost(left,right);family='16x16' if large else '8x8' if small else '8x16';costs[family].add(m1)
    assert r[15]==refresh(initial_r,m1),(left,right,initial_r,m1,r[15])
    assert ((r[H]*256+r[L])<<16)|(r[D]*256+r[E])==expected,(left,right,hex(expected),list(r))
    a=(left>>8)^(right>>8);negative=a&128
    flags=sbc16_flags(0,magnitude>>16,int(bool(magnitude&65535))) if negative else logical_flags(a)
    bc=magnitude>>16 if negative else 0 if large else initial[B]*256 if not small else initial[B]*256+initial[C]
    ix=magnitude&65535 if large else 0x2468
    assert (r[A],r[F],r[B]*256+r[C],r[8]*256+r[9],r[SP])==(a,flags,bc,ix,0x8000),(left,right,list(r),flags,bc,ix)
    assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
    assert r[14]==initial[14] and r[26:28]==initial[26:28]
    paths['16x16' if large else '8x8' if small else '8x16']+=1;cases+=1;defects+=defect
 assert initial_r_values==set(range(256)) and min(min(v) for v in costs.values())==42 and max(max(v) for v in costs.values())==175
 report=dict(passed=True,cases=cases,paths=paths,second_operand_8000_full_kernel_cases=defects,
  method='original_signed_multiply_all_words_against_seven_boundaries_both_orders',
  extreme_operand_asymmetry_preserved=True,all_output_registers_and_flags_checked=True,
  refresh_checked_cases=cases,all_initial_R_values_observed=True,
  independent_all_word_pairs_and_all_R_product_exhausted=False,
  refresh_original_code_sha256=code_sha,observed_M1_by_kernel={key:sorted(value) for key,value in costs.items()},
  refresh_formula_uses_operand_magnitudes_bit_counts_and_signs=True,
  refresh_second_operand_8000_forces_effective_multiplier_256=True,
  refresh_absolute_M1_step_witnesses=step_witnesses,
  preserved_I_IM_IFF_checked_for_original_model_initial_state=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SignedMultiplyVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

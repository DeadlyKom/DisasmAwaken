"""HELP DB00, независимая раскладка строк, весь буфер указателей и граница завершающего LDIR."""
import collections,json,random
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckJustifiedText import reference as layout
from skoolkit.simutils import PC,SP


def expected(text,selector,width,height,widths,bc):
 pointer=0
 for _ in range(selector+1):pointer=text.index(10,pointer)+1
 pointers=[];x=0
 for number in range(1025):
  pointers.append(0xE3E2+pointer)
  result=layout(0xAD35,text[pointer:],widths,x,8,width,height,bc,number>>8,number&255)
  consumed,x,y,a,f,bc,_,_,_=result
  assert consumed or f&1,('outside_progress_contract',selector,width,height)
  pointer+=consumed
  if f&1:return pointers,x,y,a
 raise AssertionError('outside_capacity_contract')


def main():
 _,_,base=make_context();raw=payload(8);base[7][0x1B00:0x1B00+len(raw)]=list(raw);fixture=Fixture(base);m=fixture.memory;s=fixture.sim;initial=fixture.initial
 widths=list(m[0x8900:0x8A00]);counts=collections.Counter();maximum=0;actual_records=raw[0x8E2:].count(10)-1;rng=random.Random(0xDB00)
 def check(text,selector,width,height,boundary=False):
  nonlocal maximum
  m.out7ffd(0x17);m[0x6306]=0x17;put(m,0xE3E2,text);put(m,0xDB7C,bytes([0xA7])*2048)
  for address,value in ((0xAEAB,height),(0xAEB3,width),(0xAEBB,0),(0xAEBF,0),(0xAEC7,0),(0xAECB,0),(0x6320,0xA7),(0x6321,0xA5)):m[address]=value
  put(m,0xAED5,(0x68,0x48,0x26));m[0xBD26]=1;put(m,0x7FFE,(255,63));s.registers[:]=initial;r=s.registers;r[0]=selector;s.run(start=0xDB57,stop=0x3FFF)
  pointers,x,y,a=expected(list(text),selector,width,height,widths,initial[2]*256+initial[3]);n=len(pointers);maximum=max(maximum,n)
  guard=m[0xE37C];before_screen=bytes(m.banks[5][:6912]);put(m,0x7FFE,(255,63));s.registers[:]=initial;r=s.registers
  # Проверка исходного полного прохода, для N=1024 остановка до разрушительного LDIR с BC=FFFF.
  s.run(start=0xDB00,stop=0xDB3E if boundary else 0x3FFF)
  if boundary:
   assert n==1024 and (r[2]*256+r[3],r[6]*256+r[7],r[4]*256+r[5])==(65535,0xE37C,0xE37D)
   assert m[0xE37C]==0 and r[SP]==0x7FFC;counts['capacity_boundary_stopped_before_ldir']+=1;return
  assert 1<=n<=1023
  cache=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes(2048-2*n)
  assert bytes(m[0xDB7C:0xE37C])==cache and m[0xE37C]==guard
  flags=((a&2)<<4)|(a&8)
  assert tuple(r[:8])==(a,flags,0,0,n>>8,n&255,0xE3,0x7B),(selector,width,height,n,r[:8],a,flags)
  assert r[8]*256+r[9]==0xDB7C+2*n and r[10:12]==initial[10:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
  assert (m[0x6320],m[0x6321])==(x,y) and bytes(m[0xAED5:0xAED8])==bytes((0x68,0x48,0x26)) and bytes(m.banks[5][:6912])==before_screen
  counts['normal_index_passes']+=1;counts['rows_indexed']+=n
 # Проверка всех реально отделённых LF-записей дискового HELP, разных размеров и раннего выхода по высоте.
 text=raw[0x8E2:]+bytes([10])*1024
 for selector in range(actual_records):
  for width in (96,168,248):
   for height in (8,13,24,192):check(text,selector,width,height)
 # Проверка каждого байта селектора на читаемых искусственных записях, поиск использует настоящий SkipLfRecords.
 for selector in range(256):
  text=bytes([10])*(selector+1)+b'ONE TWO THREE FOUR\rFIVE SIX\n'+bytes([10])*1024
  check(text,selector,96,192)
 # Проверка предельных числа строк, заполнение последнего свободного нулевого слова и исходный счётчик FFFF.
 for number in (1,2,127,128,255,256,511,512,1022,1023,1024):
  text=b'\n'+b'A '*(number-1)+bytes([10])*1024
  check(text,0,8,192,boundary=number==1024)
 # Проверка отсутствия продвижения при высоте 14, остановка после первого повторённого указателя.
 m.out7ffd(0x17);m[0x6306]=0x17;put(m,0xE3E2,b'\nONE TWO THREE FOUR FIVE SIX SEVEN\n'+bytes([10])*1024)
 m[0xDB01]=0;m[0xAEB3]=64;m[0xAEAB]=14;put(m,0x7FFE,(255,63));s.registers[:]=initial
 s.run(start=0xDB00,stop=0xDB13)
 for row in range(16):
  first=s.registers[6]*256+s.registers[7];s.run();s.run(stop=0xDB13)
  if s.registers[6]*256+s.registers[7]==first:break
 else:raise AssertionError('nonprogress_not_reproduced')
 assert s.registers[4]*256+s.registers[5]==row+1
 counts['nonprogress_stopped_before_repeated_store']+=1
 report=dict(passed=True,cases_by_path=dict(counts),actual_disk_records=actual_records,all_256_selector_bytes=True,entire_2048_byte_cache_and_end_guard_checked=True,
  independent_lf_selection_and_justified_row_layout=True,exact_main_index_alternate_context=True,final_flags_from_actual_zero_fill_ldi=True,
  maximum_rows_probed=maximum,safe_complete_domain_rows=[1,1023],n_1024_yields_ldir_count_65535=True,destructive_boundary_ldir_not_executed=True,
  glyph_prefix_restored=True,no_bitmap_writes=True,nonprogress_height_14_proved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpLineIndexVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

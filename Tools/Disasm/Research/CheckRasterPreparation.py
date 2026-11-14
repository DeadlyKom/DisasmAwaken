"""Исходные адреса двух растровых краёв, маски и ограниченный поиск строки."""
from pathlib import Path
import collections,json,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC,R,I,IM,IFF
from ReferenceControlsPointRespawn import refresh
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address
from CheckWorldSignature import logical_flags


def seek_M1(y,count,down,first_row=16,height=128):
 assert 0<=y<height and 0<=count<256
 start=first_row+y
 if down:
  n=min(count,height-y);q0=start//8+1;q1=(start+n)//8
  blocks=max(0,q1-q0+1);thirds=0 if not blocks else q1//8-(q0-1)//8
  boundary=count>=height-y
  last_block=count>0 and count<height-y and (start+count)%8==0
  return 20+5*n+18*blocks-3*thirds-int(boundary)+int(last_block)
 n=min(count,y);q0=(start-n+8)//8;q1=start//8
 blocks=max(0,q1-q0+1);thirds=0 if not blocks else q1//8-(q0-1)//8
 boundary=count>y
 last_block=count>0 and count<=y and (start-count+1)%8==0
 return 20+5*n+20*blocks-3*thirds+16*int(boundary)+int(last_block)


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 for slot in (4,7):
  row=next(x for x in manifest['entries'] if x['slot']==slot)
  assert (ROOT/(row['path']+'.sectors.bin')).read_bytes()==disk[row['offset']:row['offset']+row['allocated_length']]
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x96C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 points=reset=seek=0
 point_costs=collections.Counter();point_initial_R_codes={0xE514:set(),0xE52E:set()};witnesses=[]
 span_initial_R_codes=set();span_refresh_cases=0
 seek_costs=collections.Counter();seek_initial_R_codes={0xE5E3:set(),0xE621:set()};seek_witnesses=[]
 def run(entry):
  nonlocal span_refresh_cases
  memory[0x7FFE:0x8000]=bytes([255,63])
  if entry in point_initial_R_codes:
   x,y=sim.registers[A],sim.registers[C];initial_r=(x+y)&255;k=x&7
   cost=22+4*k if entry==0xE514 else 57-4*k
   sim.registers[R]=initial_r;sim.registers[I]=initial_r
   sim.registers[IM]=(x^y)%3;sim.registers[IFF]=(x^y)&1
   preserved_special=tuple(sim.registers[i] for i in (I,IM,IFF))
   point_initial_R_codes[entry].add(initial_r)
   if x<8 and y in (0,128):
    sim.registers[PC]=entry;m1=0
    # Подсчёт абсолютных M1, вращение маски и NEG учитывают префиксы отдельно.
    for _ in range(128):
     pc=sim.registers[PC]
     if pc==0x3FFF:break
     opcode=memory[pc]
     assert opcode not in (0xDD,0xFD)
     assert memory[pc:pc+2] not in (b'\xed\x4f',b'\xed\x5f')
     m1+=2 if opcode in (0xCB,0xED) else 1
     sim.opcodes[opcode]()
     assert sim.registers[R]==refresh(initial_r,m1)
    else:raise AssertionError(('point_instruction_limit',entry,x,y))
    assert m1==cost
    witnesses.append(dict(entry=entry,X=x,Y=y,initial_R=initial_r,final_R=sim.registers[R],observed_M1=m1))
   else:sim.run(start=entry,stop=0x3FFF)
   assert sim.registers[R]==refresh(initial_r,cost)
   assert tuple(sim.registers[i] for i in (I,IM,IFF))==preserved_special
   point_costs[entry,cost]+=1
  elif entry in seek_initial_R_codes:
   y,count=sim.registers[A],sim.registers[B];down=entry==0xE621
   cost=seek_M1(y,count,down);initial_r=(y+count)&255
   sim.registers[R]=initial_r;sim.registers[I]=initial_r
   sim.registers[IM]=(y^count)%3;sim.registers[IFF]=(y^count)&1
   preserved_special=tuple(sim.registers[i] for i in (I,IM,IFF))
   seek_initial_R_codes[entry].add(initial_r)
   column=memory[0xE62C if down else 0xE5EE]
   if column==0 and y in (0,7,8,63,127) and count in (0,1,8,128,255):
    sim.registers[PC]=entry;m1=0
    # Сопоставление абсолютных M1 длинных поисков с формулой по числу групп.
    for _ in range(2000):
     pc=sim.registers[PC]
     if pc==0x3FFF:break
     opcode=memory[pc]
     assert opcode not in (0xDD,0xFD)
     assert memory[pc:pc+2] not in (b'\xed\x4f',b'\xed\x5f')
     m1+=2 if opcode in (0xCB,0xED) else 1
     sim.opcodes[opcode]()
     assert sim.registers[R]==refresh(initial_r,m1)
    else:raise AssertionError(('seek_instruction_limit',entry,y,count))
    assert m1==cost,(entry,y,count,m1,cost)
    seek_witnesses.append(dict(entry=entry,Y=y,count=count,initial_R=initial_r,final_R=sim.registers[R],observed_M1=m1))
   else:sim.run(start=entry,stop=0x3FFF)
   assert sim.registers[R]==refresh(initial_r,cost),(entry,y,count,cost)
   assert tuple(sim.registers[i] for i in (I,IM,IFF))==preserved_special
   seek_costs[entry,cost]+=1
  elif entry==0xE5D8:
   initial_r=sim.registers[L];sim.registers[R]=initial_r;sim.registers[I]=initial_r
   sim.registers[IM]=initial_r%3;sim.registers[IFF]=initial_r&1
   preserved_special=tuple(sim.registers[i] for i in (I,IM,IFF));before=bytes(memory)
   span_initial_R_codes.add(initial_r);sim.registers[PC]=entry;m1=0
   # Проверка семи инструкций сброса масок и неизменности всей памяти.
   for _ in range(8):
    pc=sim.registers[PC]
    if pc==0x3FFF:break
    opcode=memory[pc];assert opcode not in (0xCB,0xED,0xDD,0xFD)
    sim.opcodes[opcode]();m1+=1
    assert sim.registers[R]==refresh(initial_r,m1)
   else:raise AssertionError('span_instruction_limit')
   assert m1==7 and bytes(memory)==before
   assert tuple(sim.registers[i] for i in (I,IM,IFF))==preserved_special
   span_refresh_cases+=1
  else:sim.run(start=entry,stop=0x3FFF)
  assert sim.registers[8:12]==initial[8:12] and sim.registers[16:24]==initial[16:24] and sim.registers[SP]==0x8000
 # Проверка всех байтовых координат обоих краёв, адреса сравниваются с независимым чтением таблиц.
 for y in range(256):
  for x in range(256):
   high=memory[0xEE00+y];low=(memory[0xEF00+y]+memory[0xF000+x])&255;address=high*256+low;mask=128>>(x&7)
   for entry in (0xE514,0xE52E):
    sim.registers[:]=initial;r=sim.registers;r[A]=x;r[C]=y;run(entry)
    if entry==0xE514:
     assert (r[H]*256+r[L],r[D],r[E],r[B],r[C],r[A],r[F])==(address,0x24,low,mask,x,0,0x43 if x&7==0 else 0x42)
    else:
     assert (r[H]*256+r[L],r[D],r[E],r[B],r[C],r[A],r[F])==(address,0x24,0x7A,0x96,mask,0x96,0x43 if x&7==7 else 0x42)
     assert memory[0xDFB8]==0x96
    points+=1
 # Проверка масок полного внутреннего пролёта для всех младших байтов левого адреса.
 for low in range(256):
  sim.registers[:]=initial;r=sim.registers;r[L]=low;run(0xE5D8);value=(low&224)|1
  assert (r[H],r[L],r[D],r[E],r[B],r[C],r[A],r[F])==(0x13,low,0x24,value,128,1,value,logical_flags(value));reset+=1
 upper=bitmap_address(16,0);lower=bitmap_address(144,0)
 memory[0xDFBA:0xDFBE]=upper.to_bytes(2,'little')+lower.to_bytes(2,'little')
 # Проверка всех счётчиков поиска и всех внутренних строк при обоих направлениях.
 fixtures=[(0,y,count) for y in range(128) for count in range(256)]
 fixtures += [(column,y,count) for column in (1,31) for y in (0,1,7,8,63,120,127) for count in range(256)]
 for column,y,count in fixtures:
  for entry,down,operand in ((0xE5E3,False,0xE5EE),(0xE621,True,0xE62C)):
   memory[operand]=column;sim.registers[:]=initial;r=sim.registers;r[A]=y;r[B]=count;run(entry)
   expected_y=min(128,y+count) if down else max(0,y-count)
   crossed=count>=8-(y&7) if down else count>(y&7)
   de=(lower if down else upper) if crossed else 0x247A
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F])==(bitmap_address(16+expected_y,column),de,count,y,y,0x5C),(entry,column,y,count)
   seek+=1
 assert all(codes==set(range(256)) for codes in point_initial_R_codes.values())
 assert sum(point_costs.values())==points
 assert all(codes==set(range(256)) for codes in seek_initial_R_codes.values())
 assert sum(seek_costs.values())==seek
 assert span_refresh_cases==reset and span_initial_R_codes==set(range(256))
 report=dict(passed=True,edge_coordinate_cases=points,reset_mask_cases=reset,seek_cases=seek,
  method='original_raster_edge_addresses_masks_and_bounded_row_seek_all_counts_rows_and_coordinate_bytes',
  seek_restores_AF=True,seek_returns_C_equal_input_A=True,upper_inclusive_lower_exclusive=True,
  original_zero_OR_seek_cases=65536,synthetic_nonzero_OR_seek_cases=7168,
  game_writer_of_OR_operands_established=False,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False,
  point_refresh_verification=dict(cases=points,left_M1='22+4*(X AND 7)',right_M1='57-4*(X AND 7)',
   initial_R_codes_by_entry={str(e):sorted(v) for e,v in point_initial_R_codes.items()},
   cost_profiles=[dict(entry=e,M1=m1,cases=n) for (e,m1),n in sorted(point_costs.items())],
   witnesses=witnesses,witness_count=len(witnesses),original_disk_sha256=manifest['sha256'],
   I_IM_IFF_preserved=True,independent_R_X_Y_product_proved=False,every_instruction_R_checked_only_in_witnesses=True),
  seek_refresh_verification=dict(cases=seek,first_bitmap_row=16,height=128,
   initial_R_codes_by_entry={str(e):sorted(v) for e,v in seek_initial_R_codes.items()},
   cost_profiles=[dict(entry=e,M1=m1,cases=n) for (e,m1),n in sorted(seek_costs.items())],
   witnesses=seek_witnesses,witness_count=len(seek_witnesses),M1_from_independent_block_counts=True,
   I_IM_IFF_preserved=True,independent_R_input_product_proved=False,every_instruction_R_checked_only_in_witnesses=True),
  span_refresh_verification=dict(cases=span_refresh_cases,exact_M1=7,
   initial_R_codes=sorted(span_initial_R_codes),every_instruction_R_checked=True,
   whole_memory_unchanged=True,I_IM_IFF_preserved=True,independent_R_L_product_proved=False))
 old=json.loads((ROOT/'Tools/Disasm/Reports/RasterPreparationVerification.json').read_bytes())
 assert all(report[k]==v for k,v in old.items())
 (ROOT/'Tools/Disasm/Reports/RasterPreparationVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(dict(passed=True,points=points,witnesses=len(witnesses),seek=seek,reset=reset,seek_witnesses=len(seek_witnesses),maximum_seek_M1=max(m1 for _,m1 in seek_costs)),ensure_ascii=False))


if __name__=='__main__':main()

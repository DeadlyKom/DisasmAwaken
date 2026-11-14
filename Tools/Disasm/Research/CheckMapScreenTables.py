"""Четыре исходные страницы адресов строк, горизонтальных байтов и одноразрядных масок карты."""
from pathlib import Path
import json,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC,R,I,IM,IFF
from ReferenceControlsPointRespawn import refresh
from CheckRowHighlight import make_context


def reference(memory,x,y):
 px,py=(x+8)&255,(y+16)&255;high=memory[0x8200+py];low=memory[0x8300+py]|memory[0x8400+px]
 column=low&31;low&=224;rows_high=[];rows_low=[]
 for _ in range(256):
  rows_high.append(high);rows_low.append(low);high=(high+1)&255
  if high&7==0:
   total=low+32;low=total&255
   if total<256:high=(high-8)&255
 return bytes(rows_high+rows_low+[(column+i//8)&255 for i in range(256)]+[128>>(i&7) for i in range(256)]),high*256+low,column


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes();assert sha256(disk).hexdigest()==manifest['sha256']
 for slot in (4,7):
  row=next(x for x in manifest['entries'] if x['slot']==slot)
  assert (ROOT/(row['path']+'.sectors.bin')).read_bytes()==disk[row['offset']:row['offset']+row['allocated_length']]
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 coords=sorted({(x,y) for x in range(256) for y in (0,1,7,175,191,240,255)}|{(x,y) for y in range(256) for x in (0,1,7,247,248,255)})
 flow=next(x for x in json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes()) if x['name']=='Map')
 ops=[x for x in flow['instructions'] if x['slot']==7 and 0xC49B<=x['address']<0xC4E5]
 assert len(ops)==56
 for op in ops:
  raw=bytes.fromhex(op['hex']);assert memory[op['address']:op['address']+len(raw)]==raw
  assert raw[0] not in (0xCB,0xED,0xDD,0xFD)
 group=next(x for x in ops if x['operation'].startswith('JP NZ,'));group_pc=group['address']+len(bytes.fromhex(group['hex']))
 correction=next(x for x in ops if x['operation'].startswith('JR C,'));correction_pc=correction['address']+len(bytes.fromhex(correction['hex']))
 cases=0;initial_R_codes=set();witnesses=[]
 # Проверка таблиц и их граничных байтов для всех входных координат по каждой оси.
 for x,y in coords:
  expected,de,column=reference(memory,x,y);sim.registers[:]=initial;r=sim.registers;r[D],r[E]=y,x
  memory[0xEDFF:0xF201]=bytes([0xA7])*1026;memory[0x7FFE:0x8000]=bytes([255,63])
  initial_r=(x+y)&255;r[R]=initial_r;r[I]=initial_r;r[IM]=(x^y)%3;r[IFF]=(x^y)&1;initial_R_codes.add(initial_r)
  preserved_special=tuple(r[i] for i in (I,IM,IFF))
  if x in (0,1,247,255) and y in (0,7,191,255):
   r[PC]=0xC49B;m1=groups=corrections=0
   for _ in range(6000):
    pc=r[PC]
    if pc==0x3FFF:break
    assert memory[pc] not in (0xCB,0xED,0xDD,0xFD)
    groups+=pc==group_pc;corrections+=pc==correction_pc
    sim.opcodes[memory[pc]]();m1+=1
    assert r[R]==refresh(initial_r,m1)
   else:raise AssertionError('screen_tables_instruction_limit')
   assert (m1,groups,corrections)==(5261,32,28)
   witnesses.append(dict(X=x,Y=y,initial_R=initial_r,final_R=r[R],observed_M1=m1,row_groups=groups,row_corrections=corrections))
  else:sim.run(start=0xC49B,stop=0x3FFF)
  assert r[R]==refresh(initial_r,5261) and tuple(r[i] for i in (I,IM,IFF))==preserved_special
  assert bytes(memory[0xEE00:0xF200])==expected and memory[0xEDFF]==memory[0xF200]==0xA7
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0xF000,de,0,0xC9,column+32,0x42,0x8000)
  assert r[16:18]==[0x80,0xA3] and r[18:24]==initial[18:24] and r[8:12]==initial[8:12];cases+=1
 assert initial_R_codes==set(range(256))
 report=dict(passed=True,cases=cases,method='original_map_screen_tables_against_independent_address_walk_column_and_masks',
  output_bytes_per_case=1024,all_coordinate_bytes_on_each_axis=True,
  out_of_screen_inputs_preserve_actual_lookup_bytes=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False,
  refresh_verification=dict(cases=cases,exact_M1=5261,initial_R_codes=sorted(initial_R_codes),
   witnesses=witnesses,witness_count=len(witnesses),I_IM_IFF_preserved=True,original_disk_sha256=manifest['sha256'],
   every_instruction_R_checked_only_in_witnesses=True,independent_R_coordinate_product_proved=False))
 old=json.loads((ROOT/'Tools/Disasm/Reports/MapScreenTablesVerification.json').read_bytes());assert all(report[k]==v for k,v in old.items())
 (ROOT/'Tools/Disasm/Reports/MapScreenTablesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(dict(passed=True,cases=cases,witnesses=len(witnesses),M1=5261),ensure_ascii=False))


if __name__=='__main__':main()

"""Все записи D0C3, включая зависимость старшего бита половины Y от вычитания в половине X."""
from pathlib import Path
import json,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC,R,I,IM,IFF
from ReferenceControlsPointRespawn import refresh
from CheckRowHighlight import make_context


class WrittenMemory(bytearray):
 track=False
 def __setitem__(self,index,value):
  if self.track:
   assert isinstance(index,int);self.writes.add(index&65535)
  super().__setitem__(index,value)


def expected(memory,max_x,max_y,min_x,min_y):
 writes={}
 def put(address,value,width=1):
  for offset in range(width):writes[address+offset]=(value>>(8*offset))&255
 def group(addresses,value):
  for address in addresses:put(address,value)
 put(0xDAD7,max_y*256+max_x,2);put(0xDAB6,min_y*256+min_x,2);put(0xDACC,max_y*256+min_x,2);put(0xDAC1,min_y*256+max_x,2)
 group((0xD90D,0xD9DA,0xD9ED,0xDA29,0xDA87),max_y);put(0xD468,max_y+1)
 group((0xD8EE,0xD98F,0xD9A2,0xDA3A,0xDA98),min_y)
 group((0xD940,0xD997,0xD9E2,0xDA84,0xDA95,0xDAA7),max_x);put(0xD44D,max_x+1)
 group((0xD921,0xD98C,0xD9D7,0xDA26,0xDA37,0xDA49),min_x)
 group((0xDFBE,0xE0ED,0xE112),max_y);group((0xE078,0xE1DB),(max_x+1)&255)
 half_x=((max_x+1)&255)//2;half_y=(((max_y+1)&255)>>1)|(128 if half_x<2 else 0)
 group((0xE109,0xDFBF,0xE00A,0xE017,0xE021,0xE071,0xE1BA,0xE089,0xE1F3,0xE07E,0xE1E8,0xDFC2,0xDFC1,0xE0E4),half_x)
 group((0xE173,0xE22A,0xE0C3),(half_x-2)&255);group((0xDFC0,0xE006,0xE094,0xE1BE),half_y)
 last_y=(max_y+1)&255;upper=memory[0xEE00]*256+memory[0xEF00];lower=memory[0xEE00+last_y]*256+memory[0xEF00+last_y]
 put(0xDFBC,lower,2);put(0xDFBA,upper,2)
 group((0xE11A,0xE273,0xE5DC),memory[0xF000]);group((0xE0F5,0xE25B,0xE5EE,0xE62C),memory[0xF000+max_x])
 return writes,half_y,upper


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes();assert sha256(disk).hexdigest()==manifest['sha256']
 for slot in (4,7):
  row=next(x for x in manifest['entries'] if x['slot']==slot)
  assert (ROOT/(row['path']+'.sectors.bin')).read_bytes()==disk[row['offset']:row['offset']+row['allocated_length']]
 _,source,banks=make_context();memory=WrittenMemory(65536);memory.writes=set();memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 flow=next(x for x in json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes()) if x['name']=='Map')
 ops=sorted((x for x in flow['instructions'] if x['slot']==7 and 0xD0C3<=x['address']<0xD1AC),key=lambda x:x['address'])
 pointer=0xD0C3;static_M1=0
 # Проверка непрерывного прямолинейного кода до единственного RET.
 for number,row in enumerate(ops):
  raw=bytes.fromhex(row['hex']);assert row['address']==pointer and bytes(memory[pointer:pointer+len(raw)])==raw
  assert not row['operation'].startswith(('JR','JP','CALL','DJNZ','HALT'))
  assert row['operation']=='RET' if number==len(ops)-1 else not row['operation'].startswith('RET')
  static_M1+=2 if raw[0] in (0xCB,0xED,0xDD,0xFD) else 1;pointer+=len(raw)
 assert pointer==0xD1AC and len(ops)==98 and static_M1==102
 cases=injected=0;addresses=None;initial_R_codes=set();witnesses=[]
 # Проверка всех 65536 верхних границ при нулевом минимуме, затем всех 65536 минимальных пар при заданном максимуме.
 for vary_max in (True,False):
  for pair in range(65536):
   max_x,max_y=(pair&255,pair>>8) if vary_max else (239,175);min_x,min_y=(0,0) if vary_max else (pair&255,pair>>8)
   writes,half_y,upper=expected(memory,max_x,max_y,min_x,min_y);sim.registers[:]=initial;r=sim.registers;r[H],r[L]=max_y,max_x;r[D],r[E]=min_y,min_x;r[F]=pair&255
   initial_r=pair&255;r[R]=initial_r;r[I]=initial_r;r[IM]=pair%3;r[IFF]=pair&1;initial_R_codes.add(initial_r)
   preserved_special=tuple(r[i] for i in (I,IM,IFF));memory.writes.clear();memory.track=True
   if pair in (0,1,0x7FFF,0x8000,0xFFFF):
    r[PC]=0xD0C3;m1=0
    for _ in range(100):
     pc=r[PC]
     if pc==0x3FFF:break
     opcode=memory[pc];assert opcode not in (0xCB,0xDD,0xFD)
     m1+=2 if opcode==0xED else 1;sim.opcodes[opcode]()
     assert r[R]==refresh(initial_r,m1)
    else:raise AssertionError('setup_instruction_limit')
    assert m1==102
    witnesses.append(dict(vary_max=vary_max,pair=pair,initial_R=initial_r,final_R=r[R],observed_M1=m1))
   else:sim.run(start=0xD0C3,stop=0x3FFF)
   memory.track=False
   assert r[R]==refresh(initial_r,102) and tuple(r[i] for i in (I,IM,IFF))==preserved_special
   assert memory.writes==set(writes),(pair,vary_max,memory.writes^set(writes))
   assert all(memory[a]==value for a,value in writes.items()),(pair,vary_max)
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[SP])==(0xF000+max_x,upper,0x3600+max_x,memory[0xF000+max_x],0xB0|((max_y+1)&1),0x8000)
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[I]==initial_r
   cases+=1;injected+=bool(half_y&128);addresses=sorted(writes)
 assert initial_R_codes==set(range(256))
 report=dict(passed=True,cases=cases,distinct_written_bytes=len(addresses),target_bytes=addresses,half_y_high_bit_from_half_x_subtract_cases=injected,
  method='original_D0C3_all_maximum_and_minimum_byte_pairs_independent_write_catalog_and_exact_registers',
  half_x_formula='((max_x+1) AND 255) SHR 1',half_y_formula='(((max_y+1) AND 255) SHR 1) OR (128 if half_x<2 else 0)',
  screen_table_builder_input_DE=0,geometry_validity_of_all_input_pairs_asserted=False,
  configured_clipping_execution_tested=False,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False,
  refresh_verification=dict(cases=cases,exact_M1=102,static_instruction_count=98,original_disk_sha256=manifest['sha256'],
   initial_R_codes=sorted(initial_R_codes),witnesses=witnesses,witness_count=len(witnesses),I_IM_IFF_preserved=True,
   every_instruction_R_checked_only_in_witnesses=True,independent_R_boundary_product_proved=False))
 old=json.loads((ROOT/'Tools/Disasm/Reports/MapRasterSetupVerification.json').read_bytes());assert all(report[k]==v for k,v in old.items())
 (ROOT/'Tools/Disasm/Reports/MapRasterSetupVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ('target_bytes','refresh_verification')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

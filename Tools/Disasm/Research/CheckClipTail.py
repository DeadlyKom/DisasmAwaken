"""Исходные углы, разности произведений, запись точки и буквальный специальный стековый выход."""
from pathlib import Path
import json,random,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckSignedMultiply import sbc16_flags
from CheckWorldSignature import logical_flags
from CheckClipIntersections import inc_flags
from ReferenceControlsPointRespawn import refresh
from ClipTailFacts import FUNCTIONS


def refresh_costs(source):
 # Проверка физического источника, байты функций не заменяются последовательностью из текста исходников.
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 entry=next(row for row in manifest['entries'] if row['slot']==7)
 assert source==disk[entry['offset']:entry['offset']+len(source)]
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
 rows=[row for region in flow if region['name']=='Map' for row in region['instructions']
       if 0xDAB0<=row['address']<0xDB63]
 for row in rows:
  raw=bytes.fromhex(row['hex'])
  assert row['slot']==7 and row['offset']==row['address']-0xC000
  assert source[row['offset']:row['offset']+len(raw)]==raw
  assert raw[:2] not in (b'\xed\x4f',b'\xed\x5f')
 # Расчёт стоимости прямых последовательностей с отдельной выборкой каждого префикса ED.
 costs={};blocks={};boundaries=sorted(FUNCTIONS)+[0xDB63]
 for first,end in zip(boundaries,boundaries[1:]):
  block=[row for row in rows if first<=row['address']<end]
  for row,following in zip(block,block[1:]+[dict(address=end)]):
   assert row['address']+len(bytes.fromhex(row['hex']))==following['address']
  blocks[first]=block
  if first<0xDADC:continue
  assert block[-1]['operation']=='RET' and block[-1]['hex']=='c9'
  assert not any(row['operation'].startswith(('JP ','JR ','CALL ','DJNZ ','RET','RST ','HALT')) for row in block[:-1])
  costs[first]=sum(2 if bytes.fromhex(row['hex'])[0] in (0xCB,0xED,0xDD,0xFD) else 1 for row in block)
 costs[0xDB4A]=sum(2 if bytes.fromhex(row['hex'])[0] in (0xCB,0xED,0xDD,0xFD) else 1
                  for row in blocks[0xDB42] if row['address']>=0xDB4A)
 # Проверка единственной развилки, AND полного запрета и RET NZ перед двумя командами записи угла.
 for first,pair in ((0xDAB0,0),(0xDABB,255),(0xDAC6,0xFF00),(0xDAD1,0xFFFF)):
  raw=b''.join(bytes.fromhex(row['hex']) for row in blocks[first])
  assert raw==bytes.fromhex('3a3adea7c011')+pair.to_bytes(2,'little')+bytes.fromhex('c34adb')
  costs[first]=dict(blocked=3,written=5+costs[0xDB4A])
 assert costs[0xDB4A]==10 and costs[0xDB42]==14 and costs[0xDB59]==9
 assert all(costs[pc]==12 for pc in (0xDADC,0xDAF0,0xDB04,0xDB18))
 assert costs[0xDB2C]==costs[0xDB37]==7
 return costs,sha256(b''.join(bytes.fromhex(row['hex']) for row in rows)).hexdigest()


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 costs,code_sha=refresh_costs(source);initial_r_values=set()
 counts=dict(corners=0,product_differences=0,coordinate_differences=0,append_points=0,stack_exits=0)
 def start(entry,sp=0x7FFE):
  sim.registers[:]=initial;sim.registers[SP]=sp;memory[sp:sp+2]=bytes([255,63])
  # Выбор разных начальных R не меняет числовые фикстуры, исходные помощники не читают R.
  initial_r=(entry+sum(counts.values()))&255;initial_r_values.add(initial_r);sim.registers[15]=initial_r
  m1=costs[entry]
  if isinstance(m1,dict):m1=m1['blocked' if memory[0xDE3A] else 'written']
  sim.run(start=entry,stop=0x3FFF)
  assert sim.registers[15]==refresh(initial_r,m1),(entry,initial_r,m1,sim.registers[15])
 def preserved(skip):
  for index in list(range(14))+list(range(16,24)):
   if index not in skip:assert sim.registers[index]==initial[index],(index,list(sim.registers))
 # Проверка всех значений запрета углов и всех положений байтового курсора, включая переход FF к 00.
 for entry,pair in ((0xDAB0,(0,0)),(0xDABB,(255,0)),(0xDAC6,(0,255)),(0xDAD1,(255,255))):
  for block in range(256):
   for cursor in range(256) if block in (0,1,255) else (block,):
    memory[0xDE3A]=block;memory[0xDE3B]=cursor;memory[0xF8FF:0xFA01]=bytes([0xA7])*258;start(entry);r=sim.registers
    expected=bytearray([0xA7]*256)
    if block:
     assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E])==(block,logical_flags(block)|0x10,0x1357,0x247A)
    else:
     expected[cursor],expected[(cursor+1)&255]=pair;after=(cursor+2)&255
     assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E])==(after,inc_flags((cursor+1)&255,0),0xF900+after,pair[1]*256+pair[0])
    assert memory[0xF900:0xFA00]==expected and memory[0xF8FF]==memory[0xFA00]==0xA7
    assert memory[0xDE3B]==(cursor if block else (cursor+2)&255) and r[SP]==0x8000
    preserved({A,F,H,L,D,E,SP});counts['corners']+=1
 rng=random.Random(0xDADC);values=(0,1,0xFFFF,0x10000,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
 # Проверка заёма из младшего слова, переполнения старшего и сохранения DE у четырёх сравнений.
 for entry,left_base,right_base in ((0xDADC,0xDE6B,0xDE73),(0xDAF0,0xDE6B,0xDE77),(0xDB04,0xDE6F,0xDE73),(0xDB18,0xDE6F,0xDE77)):
  fixtures=[(a,b) for a in values for b in values]+[(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(8192)]
  for left,right in fixtures:
   memory[left_base:left_base+4]=left.to_bytes(4,'little');memory[right_base:right_base+4]=right.to_bytes(4,'little');before=bytes(memory[0xDE6B:0xDE7B]);start(entry);r=sim.registers
   borrow=int((left&65535)<(right&65535));expected=((left>>16)-(right>>16)-borrow)&65535
   assert (r[H]*256+r[L],r[B]*256+r[C],r[A],r[F],r[SP])==(expected,right>>16,0x5A,sbc16_flags(left>>16,right>>16,borrow),0x8000)
   assert memory[0xDE6B:0xDE7B]==before;preserved({H,L,B,C,F,SP});counts['product_differences']+=1
 # Проверка обеих разностей координат для всех вторых слов и семи первых граничных слов.
 for entry,offset in ((0xDB2C,0),(0xDB37,2)):
  for first in (0,1,255,256,32767,32768,65535):
   memory[0xDE2F+offset:0xDE31+offset]=first.to_bytes(2,'little')
   for second in range(65536):
    memory[0xDE34+offset:0xDE36+offset]=second.to_bytes(2,'little');start(entry);r=sim.registers
    assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==((second-first)&65535,first,0x5A,sbc16_flags(second,first,0),0x8000)
    preserved({H,L,D,E,F,SP});counts['coordinate_differences']+=1
 # Проверка записи младших байтов второй точки и прямого входа с DE, без переноса адреса в страницу FA.
 for direct in (False,True):
  for cursor in range(256):
   for value in (0,1,255,256,0x7FFF,0x8000,0xFFFF):
    x,y=value,(value*257+3)&65535;memory[0xDE34:0xDE38]=x.to_bytes(2,'little')+y.to_bytes(2,'little');memory[0xDE3B]=cursor
    memory[0xF8FF:0xFA01]=bytes([0xA7])*258;start(0xDB4A if direct else 0xDB42);r=sim.registers
    pair=(0x7A,0x24) if direct else (x&255,y&255);after=(cursor+2)&255;expected=bytearray([0xA7]*256);expected[cursor],expected[(cursor+1)&255]=pair
    assert memory[0xF900:0xFA00]==expected and memory[0xF8FF]==memory[0xFA00]==0xA7 and memory[0xDE3B]==after
    assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==(0xF900+after,pair[1]*256+pair[0],after,inc_flags((cursor+1)&255,initial[F]&1),0x8000)
    preserved({H,L,D,E,A,F,SP});counts['append_points']+=1
 # Проверка специального выхода по точному кадру из трёх снимаемых слов и адреса возврата, без гипотезы о назначении слов.
 for high in range(256):
  for a in range(256):
   w0=(a<<8)|0x5C;w1=(high<<8)|0xC9;w2=(high*257+0xA7)&65535;sp=0x7FF8
   memory[sp:0x8000]=w0.to_bytes(2,'little')+w1.to_bytes(2,'little')+w2.to_bytes(2,'little')+bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[SP]=sp
   # Проверка R специального выхода, три POP не заменяются обычной рамкой CALL.
   initial_r=(high^a)&255;initial_r_values.add(initial_r);r[15]=initial_r
   sim.run(start=0xDB59,stop=0x3FFF);count=(high-1)&255
   assert r[15]==refresh(initial_r,costs[0xDB59])
   flags=(count&0x80)|(0x40 if count==0 else 0)|(4 if high==128 else 0)|(a&0x28)|1
   assert (r[H]*256+r[L],r[B]*256+r[C],r[A],r[F],r[SP])==((w2+count)&65535,count,a,flags,0x8000)
   preserved({H,L,B,C,A,F,SP});counts['stack_exits']+=1
 assert initial_r_values==set(range(256))
 report=dict(passed=True,cases=sum(counts.values()),cases_by_family=counts,method='original_clip_tail_independent_entries_flags_output_page_and_literal_stack_frame',
  corner_gate_all_bytes_checked=True,ordinary_calls_not_substituted_for_special_frame=True,full_dispatch_semantics_proved=False,
  refresh_checked_cases=sum(counts.values()),all_initial_R_values_observed=True,
  initial_R_independent_full_input_product_proved=False,
  original_refresh_proof_code_sha256=code_sha,
  refresh_M1_by_entry={format(pc,'04X'):value for pc,value in costs.items()},
  original_refresh_paths_have_no_LD_R_A_or_LD_A_R=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ClipTailVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

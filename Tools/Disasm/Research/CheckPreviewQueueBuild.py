"""Полный исходный обход EC28 до восстановления SP, независимая очередь и все помощники."""
from pathlib import Path
import json,sys,random,struct,collections
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,PC,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckPreviewTransform import COEFFICIENTS
from CheckWorldSignature import logical_flags
from PreviewQueueOracle import build


def main():
 raw=payload(6);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=synthetic=accepted=0;reasons=collections.Counter();lengths=collections.Counter()
 def check(records,matrix,header_overrides=None):
  nonlocal cases,synthetic,accepted
  overrides=header_overrides or {};pool=bytes((j*37+cases*11)&255 for j in range(256));expected=build(raw,records,matrix,pool,header_overrides=overrides)
  m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0xC700:0xC800]=list(pool)
  # Подготовка существующего исходного списка по фиксированному шагу 64, дополнительные записи только фикстура RAM.
  for index,(coords,model,angles) in enumerate(records):
   address=0xCDC0+64*index;m[address:address+64]=[(j*13+index)&255 for j in range(64)];m[address:address+10]=list(struct.pack('<3H4B',*coords,model,*angles))
  low=(128,129,254,255)[cases%4];end=0xCDC0+64*len(records);m[end]=low;m[end+1]=128
  for row in range(3):
   for column in range(3):m[0xC20D+2*(3*column+row)]=matrix[row][column]
  m[0xC200:0xC203]=[3,5,7];m[0xCF02]=0xA5;m[0xCF03]=0x5A;m[0xCEFA]=0xA7;m[0xCEFB]=0x5B;m[0x7FFE:0x8000]=[255,63]
  for address,value in overrides.items():m[address]=value
  s=Simulator(m);s.registers[:]=initial;s.registers[PC]=0xEC28;m.recording=True;m.writes=[];visited=[]
  for _ in range(30000):
   pc=s.registers[PC]
   if pc==0xEEEE:break
   if pc==0xECB0:visited.append(s.registers[H]*256+s.registers[L])
   s.run()
  else:raise AssertionError(('instruction_limit',records,matrix,hex(s.registers[PC])))
  terminal=0xCDC0+64*expected['terminal'];marker=m[terminal]+256*m[terminal+1];r=s.registers
  assert visited==[0xCDC0+64*i for i in range(expected['terminal']+1)]
  assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E],r[2]*256+r[3],r[SP])==(marker&255,logical_flags(marker&255)|16,marker,expected['de'],expected['bc'],terminal+2),(records,matrix,expected['reasons'],tuple(r[:8]),expected['de'],expected['bc'])
  assert bytes(m[0xC700:0xC800])==expected['pool'] and m[0xCF02]==expected['head'] and m[0xCF03]==expected['free']
  assert m[0xC21E:0xC221]==list(expected['params']) and (m[0xCEFA],m[0xCEFB])==(expected['flags'],expected['model_offset'])
  assert [m[p]+256*m[p+1] for p in (0xDAF6,0xDA38,0xDA16)]==expected['results']
  assert r[8]*256+r[9]==expected['ix'] and r[10]*256+r[11]==expected['iy']
  assert r[16:24]==[*expected['alt_af'],0,64,expected['alt_de']>>8,expected['alt_de']&255,terminal>>8,terminal&255]
  for row in range(3):
   for column in range(3):assert m[COEFFICIENTS[row][column]]==(129 if matrix[row][column]==128 else matrix[row][column])
  allowed=set(range(0xC700,0xC800))|set(range(0xCEFA,0xCF04))|set(range(0xC21E,0xC221))|set(range(0x7FFA,0x7FFE))|{0xEEEF,0xEEF0,0xEB7C,0xEB7D,0xED5C,0xEDC4,0xEDFD}
  for pointers in COEFFICIENTS:allowed.update(pointers)
  for pointer in (0xEB7F,0xEB8D,0xEBA0,0xDAF6,0xDA38,0xDA16):allowed.update((pointer,pointer+1))
  assert all(pointer in allowed for pointer,value in m.writes)
  assert m[0xEEEF:0xEEF1]==[254,127] and m[0x7FFE:0x8000]==[255,63]
  # Исполнение настоящего восстановления CPU-стека, рисующий проход после EEF1 не начинается.
  s.run();assert r[PC]==0xEEF1 and r[SP]==0x7FFE
  reasons.update(expected['reasons']);lengths[len(records)]+=1;accepted+=len(expected['accepted']);cases+=1;synthetic+=bool(overrides)
 identity=((127,0,0),(0,127,0),(0,0,127));matrices=(identity,((0,0,0),)*3,((129,0,0),(0,129,0),(0,0,129)),((127,127,127),)*3,((0,127,0),(129,0,0),(0,0,127)))
 vectors=((0,0,1500),(0,0,0),(0,0,8191),(0,0,8192),(28672,0,1),(0,28672,1),(0,0,28672),(32768,0,1),(32896,0,1),(65535,65535,1500))
 # Проверка всех 11 исходных моделей и различных матриц без изменения оригинальных заголовков.
 for model in range(11):
  for matrix in matrices:
   for index,coords in enumerate(vectors):check([(coords,4*model,(0,index&255,0) if index&1 else (1,2,3))],matrix)
 rng=random.Random(0xEC28)
 for _ in range(1024):
  records=[(tuple(rng.randrange(65536) for j in range(3)),4*rng.randrange(11),tuple(rng.randrange(256) for j in range(3))) for i in range(rng.randrange(5))]
  check(records,tuple(tuple(rng.randrange(256) for j in range(3)) for i in range(3)))
 # Проверка принятой цепочки из четырёх объектов и подготовленных масштабов 1..6, бит 7 заголовка только синтетическая фикстура.
 records=[((0,second,depth),0,(0,i,0)) for i,(second,depth) in enumerate(((10,1500),(30,1700),(20,1200),(0,1600)))]
 pointer=int.from_bytes(raw[0x1000:0x1002],'little')
 for exponent in range(1,7):
  for flag in (0,128):check(records,identity,{pointer+1:exponent|flag})
 report=dict(passed=True,cases=cases,synthetic_header_cases=synthetic,accepted_objects=accepted,record_count_fixtures=dict(lengths),reasons=dict(reasons),all_11_original_model_headers=True,real_transform_bounds_queue_and_sp_restore=True,independent_functional_queue_and_register_oracle=True,dirty_unused_nodes_preserved=True,exact_write_boundaries_checked=True,real_cpu_return_bytes_preserved=True,rendering_pass_not_executed=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewQueueBuildVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

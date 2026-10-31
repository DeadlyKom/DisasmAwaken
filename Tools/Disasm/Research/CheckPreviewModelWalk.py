"""Два полных исходных обхода моделей, реальные данные, производители, генератор и перспектива."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP,PC
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewMatrixComposeOracle import OUTPUT
from PreviewVertexGroupOracle import WORD_TARGETS,BYTE_TARGETS
from PreviewVertexProductsOracle import general,planar
from PreviewModelWalkOracle import walk
from PreviewModelGroups import records
from CheckPreviewVertexProducts import PRODUCT_BYTES


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=vertices=groups=0;entries=collections.Counter();empty_cases=0
 def word(pointer,value):m[pointer]=value&255;m[pointer+1]=value>>8
 def check(entry,model_offset,coefficients,base,centres=(0,0),angle=0,reference=0,empty=False):
  nonlocal cases,vertices,groups,empty_cases
  buffer=bytes((j*37+cases*11)&255 for j in range(272));expected=walk(raw,model_offset,entry,coefficients,angle,reference,base,centres,buffer,empty)
  m.recording=False;m[0xC000:0xC000+len(raw)]=raw;m[0xC5F0:0xC700]=buffer;m[0xD90D]=0xA5;word(0xDA11,0xA55A);word(0xDBB6,0xA55A);word(0xDBC0,0xC35A);m[0x7FF8:0x7FFE]=[0xA5]*6
  for row in range(3):
   for column in range(3):m[OUTPUT[row][column]]=coefficients[row][column]
  for pointer in (*PRODUCT_BYTES,0xD861,0xD869,0xD871,0xD87B):m[pointer]=0xA5
  m[0xCEFB]=model_offset;m[0xC21F]=angle;m[0xC201]=reference
  for pointer,value in zip((0xDA16,0xDA38,0xDAF6,0xDAE7,0xDBA5),(*base,*centres)):word(pointer,value)
  if empty:m[expected['model']['pointer']+2]=0
  s.registers[:]=initial;r=s.registers;r[PC]=entry;m.recording=True;m.writes=[];visited=[]
  for _ in range(100000):
   pc=r[PC]
   if pc==0x3FFF:break
   if pc==(0xD8AA if entry==0xD896 else 0xD84A):visited.append(r[H]*256+r[L])
   s.run()
  else:raise AssertionError('Не завершён обход исходной модели')
  assert visited==[address for address,data in expected['groups']]+[expected['hl']-1]
  assert bytes(m[0xC5F0:0xC700])==expected['buffer'],(entry,model_offset,base,expected)
  assert (r[A],r[F],r[H]*256+r[L],r[B]*256+r[C],r[D]*256+r[E],r[8]*256+r[9],r[10]*256+r[11],r[SP])==(0,0x54,expected['hl'],expected['bc'],expected['de'],expected['ix'],expected['iy'],0x8000),(entry,model_offset,base,empty,r[:12],expected)
  af,bc,de,hl=expected['alternates'];assert tuple(r[16:24])==(*af,bc>>8,bc&255,de>>8,de&255,hl>>8,hl&255)
  assert m[0xD90D]==expected['offset'] and m[0x7FFE:0x8000]==[255,63]
  assert m[0xDA11]+256*m[0xDA12]==(0x7FFA if expected['groups'] else 0xA55A)
  assert all(m[pointer]==6-expected['model']['exponent'] for pointer in (0xDA20,0xDA3B,0xDAF9))
  if expected['planar_coefficients'] is not None:assert [m[p] for p in (0xD861,0xD869,0xD871,0xD87B)]==list(expected['planar_coefficients'])
  else:assert [m[p] for p in (0xD861,0xD869,0xD871,0xD87B)]==[0xA5]*4
  if expected['last'] is not None:
   words,thirds=expected['product_inputs'];assert [m[p]+256*m[p+1] for p in (0xD910,0xD913,0xD916)]==list(words) and [m[p] for p in (0xD956,0xD955,0xD953)]==list(thirds)
   for index,pointer in WORD_TARGETS.items():assert m[pointer]+256*m[pointer+1]==expected['last']['words'][index]
   for index,pointer in BYTE_TARGETS.items():assert m[pointer]==expected['last']['thirds'][index]
   assert m[0x7FFA]+256*m[0x7FFB]==(0xD8BA if entry==0xD896 else 0xD85A)
   assert m[0x7FF8]+256*m[0x7FF9]==(0xD905 if entry==0xD896 else 0xD87F)
   assert m[0x7FFC]+256*m[0x7FFD]==expected['hl']-1
  else:assert m[0x7FFA:0x7FFE]==[0xA5,0xA5,*((0xA9,0xD8) if entry==0xD896 else (0x49,0xD8))]
  success=expected['last_success'] or (0xA55A,0xC35A);assert (m[0xDBB6]+256*m[0xDBB7],m[0xDBC0]+256*m[0xDBC1])==success
  allowed={0xD90D,0xDA20,0xDA3B,0xDAF9,0x7FFC,0x7FFD}
  if entry==0xD819:allowed.update((0xD861,0xD869,0xD871,0xD87B))
  if expected['groups']:
   allowed.update(PRODUCT_BYTES);allowed.update((0xDA11,0xDA12,0x7FF8,0x7FF9,0x7FFA,0x7FFB));allowed.update(p+j for p in WORD_TARGETS.values() for j in range(2));allowed.update(BYTE_TARGETS.values())
  for index,outcome in enumerate(expected['reasons']):
   stack=0xC604+5*index;allowed.update(range(stack-4,stack))
   if outcome=='accepted':allowed.update(range(stack-6,stack-4));allowed.update((0xDBB6,0xDBB7,0xDBC0,0xDBC1))
  actual={p for p,v in m.writes}
  assert actual==allowed,(entry,model_offset,empty,sorted(actual-allowed),sorted(allowed-actual))
  cases+=1;vertices+=expected['vertices'];groups+=len(expected['groups']);empty_cases+=empty;entries[format(entry,'04X')]+=1
 identity=((127,0,0),(0,127,0),(0,0,127));matrices=(identity,((0,0,0),)*3,((127,129,128),(255,1,0),(129,127,255)),((127,127,127),)*3)
 # Проверка всех 22 реальных указателей, обоих входов, матриц и баз без изменения физических моделей.
 for entry in (0xD896,0xD819):
  for model_offset in range(0,44,2):
   for coefficients in matrices:
    for base in ((1500,10,65530),(0,0,0),(32767,32767,32768),(65535,65535,65535)):check(entry,model_offset,coefficients,base,(0x8C00,0x5000),model_offset*5,255-model_offset)
   check(entry,model_offset,identity,(1500,0,0),empty=True)
 # Проверка каждого относительного угла плоского входа на исходной синусоиде.
 for delta in range(256):check(0xD819,2*(delta%22),identity,(1500,0,0),(0x8C00,0x5000),(delta+73)&255,73)
 rng=random.Random(0xD896)
 for _ in range(512):check(rng.choice((0xD896,0xD819)),2*rng.randrange(22),tuple(tuple(rng.randrange(256) for j in range(3)) for i in range(3)),tuple(rng.randrange(65536) for i in range(3)),tuple(rng.randrange(65536) for i in range(2)),rng.randrange(256),rng.randrange(256))
 physical={records(raw,offset)['pointer']:records(raw,offset) for offset in range(0,44,2)}
 report=dict(passed=True,cases=cases,entries=dict(entries),projected_vertices=vertices,processed_groups=groups,synthetic_empty_models=empty_cases,all_22_original_pointer_slots=True,unique_physical_models=len(physical),physical_groups=sum(len(v['groups']) for v in physical.values()),all_relative_planar_angles=True,independent_full_model_walk_and_register_oracle=True,real_products_group_projection_scale_and_cpu_return=True,exact_write_boundaries_checked=True,planar_game_caller_not_established=True,irq_executed=False,native_execution=False,assembly_executed=False,face_pass_not_executed=True)
 (ROOT/'Tools/Disasm/Reports/PreviewModelWalkVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

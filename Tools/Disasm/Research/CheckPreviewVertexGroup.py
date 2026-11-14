"""Все маски генератора D908, исходная перспектива и независимые координаты группы."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewVertexGroupOracle import group,WORD_TARGETS,BYTE_TARGETS


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=vertices=0;reasons=collections.Counter();lengths=collections.Counter()
 def word(pointer,value):m[pointer]=value&255;m[pointer+1]=value>>8
 def check(words,thirds,mask,base,exponent,centres=(0,0),cpu_stack=0x7FFE,alt_seed=None):
  nonlocal cases,vertices
  context=list(initial);context[SP]=cpu_stack;context[14]=cases&255;context[26]=0;context[27]=cases%3
  if alt_seed is not None:context[16:24]=[(alt_seed+37*i)&255 for i in range(8)]
  alternates=(tuple(context[16:18]),context[18]*256+context[19],context[20]*256+context[21],context[22]*256+context[23])
  offset=4+5*(cases%10);buffer=bytes((j*37+cases*11)&255 for j in range(272));expected=group(words,thirds,mask,base,exponent,centres,offset,buffer,initial_alternates=alternates)
  m.recording=False;m[0xC5F0:0xC700]=buffer;m[0xD90D]=offset;word(0xDBB6,0xA55A);word(0xDBC0,0xC35A)
  for pointer,value in zip((0xD910,0xD913,0xD916),words):word(pointer,value)
  m[0xD956]=thirds[0];m[0xD955]=thirds[1];m[0xD953]=thirds[2]
  for pointer,value in zip((0xDA16,0xDA38,0xDAF6,0xDAE7,0xDBA5),(*base,*centres)):word(pointer,value)
  for pointer in (0xDA20,0xDA3B,0xDAF9):m[pointer]=6-exponent
  m.recording=False;word(cpu_stack,0x3FFF);s.registers[:]=context;r=s.registers;r[9]=mask;m.recording=True;m.writes=[];s.run(start=0xD908,stop=0x3FFF)
  assert bytes(m[0xC5F0:0xC700])==expected['buffer'],(words,thirds,mask,base,exponent,expected)
  assert (r[A],r[F],r[H]*256+r[L],r[B]*256+r[C],r[D]*256+r[E],r[8]*256+r[9],r[10]*256+r[11],r[SP])==(*expected['af'],expected['stack'],expected['bc'],expected['de'],expected['ix'],expected['iy'],cpu_stack+2),(words,thirds,mask,base,exponent,r[:12],expected)
  assert tuple(r[16:24])==(*expected['alt_af'],expected['alt_bc']>>8,expected['alt_bc']&255,expected['alt_de']>>8,expected['alt_de']&255,expected['alt_hl']>>8,expected['alt_hl']&255),(mask,r[16:24],expected)
  assert m[0xDA11:0xDA13]==[cpu_stack&255,cpu_stack>>8] and m[0xD90D]==expected['stack']&255 and m[cpu_stack:cpu_stack+2]==[255,63]
  # Проверка фиксированного окна C6, финальный ADD HL,SP очищает H/N/Carry и оставляет только S/Z/PV.
  assert not r[F]&0x3B and all(r[i]==context[i] for i in (14,26,27))
  if mask not in (1,129) and not mask&16:assert r[F]==0x44
  if not mask:
   # Проверка пустой маски, данные комбинаций всё равно готовятся, перспектива и альтернативные пары не меняются.
   assert r[16:24]==context[16:24] and m[0xD90D]==offset
   assert r[A]==offset and r[F]==0x44
  for index,pointer in WORD_TARGETS.items():assert m[pointer]+256*m[pointer+1]==expected['words'][index]
  for index,pointer in BYTE_TARGETS.items():assert m[pointer]==expected['thirds'][index]
  success=expected['last_success'] or (0xA55A,0xC35A)
  assert (m[0xDBB6]+256*m[0xDBB7],m[0xDBC0]+256*m[0xDBC1])==success
  allowed={0xDA11,0xDA12,0xD90D}|{p+j for p in WORD_TARGETS.values() for j in range(2)}|set(BYTE_TARGETS.values())
  for index,outcome in enumerate(expected['reasons']):
   stack=0xC600+offset+5*index;allowed.update(range(stack-4,stack))
   if outcome=='accepted':allowed.update(range(stack-6,stack-4));allowed.update((0xDBB6,0xDBB7,0xDBC0,0xDBC1))
  assert set(p for p,v in m.writes)==allowed
  cases+=1;vertices+=len(expected['vertices']);reasons.update(expected['reasons']);lengths[len(expected['vertices'])]+=1
 # Проверка всех 256 масок на крайних упакованных входах, включая побайтовое отрицание 80 и межбайтовые переносы.
 patterns=(((0,0,0),(0,0,0)),((0x0101,0x0202,0x0303),(1,2,3)),((0x7F7F,0x7F7F,0x7F7F),(127,127,127)),((0x8080,0x8080,0x8080),(128,128,128)),((0xFFFF,0xFFFF,0xFFFF),(255,255,255)),((0x80FF,0xFF80,0x7F01),(129,255,1)))
 for mask in range(256):
  for words,thirds in patterns:
   for exponent in (1,3,6):check(words,thirds,mask,(1500,10,65530),exponent,(0x8C00,0x5000))
 rng=random.Random(0xD908)
 for _ in range(1024):check(tuple(rng.randrange(65536) for i in range(3)),tuple(rng.randrange(256) for i in range(3)),rng.randrange(256),tuple(rng.randrange(65536) for i in range(3)),rng.randrange(1,7),tuple(rng.randrange(65536) for i in range(2)))
 # Проверка нулевой маски с различимыми альтернативными байтами и четырьмя отдельными CPU-стеками.
 for seed in range(256):
  check((0x80FF,0xFF80,0x7F01),(129,255,1),0,(1500,10,65530),1+seed%6,(0x8C00,0x5000),cpu_stack=(0x7FFE,0x8002,0x9FFE,0xBFFE)[seed%4],alt_seed=seed)
 report=dict(passed=True,cases=cases,projected_vertices=vertices,all_256_masks_checked=True,vertices_per_group=dict(lengths),projection_reasons=dict(reasons),special_masks_01_and_81_preserved=True,bytewise_negation_and_rotates_preserved=True,packed_word_carries_preserved=True,independent_numeric_group_and_real_projection=True,all_main_alternate_and_index_registers_checked=True,real_cpu_sp_and_return_restored=True,exact_write_boundaries_checked=True,whole_physical_model_walk_not_executed=True,direct_final_flag_and_I_IM_IFF_conditions_checked=True,zero_mask_alternate_context_cases=256,zero_mask_cpu_stack_positions=[0x7FFE,0x8002,0x9FFE,0xBFFE],R_proved=False,complete_joint_input_product_exhausted=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewVertexGroupVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Независимый полный bitmap исходной заливки, без сборки и IRQ.

Документация: ../../../Docs/PreviewPolygonFill.md#r-полной-заливки-и-неизменность-кодов
"""
from pathlib import Path
from collections import Counter
import json,random
from ProbePreviewPolygon import context,execute,ROOT
from PreviewPolygonOracle import literal_mask_writes,raster,registers
from PreviewEdgeRasterOracle import arithmetic
from Analyze import payload


class PolygonRefresh:
 """Исходные неизменные коды и явно разрешённые изменяемые операнды."""
 def __init__(self,memory):
  flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
  rows=[i for r in flow if r['name']=='D3D' for i in r['instructions'] if 0xD1C0<=i['address']<0xD518]
  modified=json.loads((ROOT/'Tools/Disasm/Reports/ModifiedCode.json').read_text('utf-8'))
  writers=[r for r in modified if r.get('target_region',r['region'])=='D3D' and 0xD1C0<=r['target']<0xD518]
  self.operands={address for row in writers for address in range(row['target'],row['target']+row['size'])}
  assert len(writers)==28 and len(self.operands)==18
  self.cost={};covered=set();raw=payload(6)
  # Проверка исходного кода и исключение записей/чтений R из собственных команд.
  for row in rows:
   pc=row['address'];code=bytes.fromhex(row['hex'])
   assert raw[pc-0xC000:pc-0xC000+len(code)]==code
   assert code not in (bytes.fromhex('ed4f'),bytes.fromhex('ed5f'))
   assert pc not in self.operands
   for offset,value in enumerate(code):
    if pc+offset not in self.operands:assert memory[pc+offset]==value
   self.cost[pc]=2 if code[0] in (0xCB,0xDD,0xED,0xFD) else 1
   covered.update(range(pc,pc+len(code)))
  assert len(rows)==562 and covered==set(range(0xD1C0,0xD518))

 def start(self,r):
  self.initial_r=r;self.m1=0;self.instructions=0

 def before(self,r):
  self.previous_r=r[15];self.increment=self.cost[r[24]]

 def after(self,r):
  # Проверка каждого шага отдельно от конечной суммы modulo 128.
  assert r[15]==(self.previous_r&128)|((self.previous_r+self.increment)&127)
  self.m1+=self.increment;self.instructions+=1

 def finish(self,memory,r):
  # Проверка неизменности всех кодов через полный журнал CPU-записей профиля.
  assert all(not 0xD1C0<=address<0xD518 or address in self.operands for address,value in memory.writes)
  assert r[15]==(self.initial_r&128)|((self.initial_r+self.m1)&127)
  return self.m1,self.instructions


def hull(points):
 points=sorted(set((x,y) for y,x in points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lower=[];upper=[]
 for p in points:
  while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
  lower.append(p)
 for p in reversed(points):
  while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
  upper.append(p)
 return [(y,x) for x,y in lower[:-1]+upper[:-1]]


def main():
 m,s,initial=context();cases=0;outside_writes=0;mode_cases=Counter();literal_rom_attempts=0
 refresh=PolygonRefresh(m);refresh_seeds=set();m1_total=instruction_total=0;refresh_by_mode={}
 masks=bytes(m[0xC000:0xC200])
 # Подготовка ненулевого образца ROM позволяет обнаружить даже ошибочное обнуление вне bitmap.
 m[:0x4000]=[(i*17+93)&255 for i in range(0x4000)];outside_original=bytes(m[:0x4000])
 buffers=(bytes(6144),bytes([255]*6144),bytes((i*37+11)&255 for i in range(6144)),bytes((85,170))*3072)
 def check(vertices,mode):
  nonlocal cases,outside_writes,literal_rom_attempts,m1_total,instruction_total
  source=buffers[cases%4]
  m.recording=False;m[0x4000:0x5800]=source
  if mode < 5:
   expected=raster(source,vertices,mode)
  else:
   expected_memory,expected_writes=literal_mask_writes(m,vertices,mode,masks)
   expected=expected_memory[0x4000:0x5800]
  initial[14]=cases&255;initial[15]=(cases*73)&255;initial[26]=cases&1;initial[27]=cases%3
  refresh_seeds.add(initial[15]);refresh.start(initial[15])
  steps=execute(m,s,initial,vertices,mode,refresh=refresh)
  m1,instructions=refresh.finish(m,s.registers)
  assert instructions==steps and s.registers[14]==initial[14] and s.registers[26:28]==initial[26:28]
  m1_total+=m1;instruction_total+=instructions
  bounds=refresh_by_mode.setdefault(str(mode),[m1,m1]);bounds[0]=min(bounds[0],m1);bounds[1]=max(bounds[1],m1)
  actual=bytes(m[0x4000:0x5800])
  assert actual==expected,(vertices,mode,[(i,actual[i],expected[i]) for i in range(6144) if actual[i]!=expected[i]][:12])
  assert s.registers[6:8]==initial[6:8]
  # Проверка всех основных, альтернативных и индексных регистров по конечной геометрии двух цепочек.
  r=s.registers;out=registers(vertices,mode,masks if mode>=5 else None)
  assert tuple(r[:2])==out['af'] and r[2]*256+r[3]==out['bc'] and r[4]*256+r[5]==out['de'],(vertices,mode,r[:8],out)
  if out['degenerate']:
   assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
   count=len(vertices)*2;value,flags=arithmetic(count,1,True)
   assert tuple(r[16:18])==(value,(flags&254)|(initial[1]&1))
  else:
   assert (r[8]*256+r[9],r[10]*256+r[11])==(out['ix'],out['iy']),(vertices,mode,r[8:12],out)
   assert tuple(r[16:18])==out['alt_af'] and r[18]*256+r[19]==out['alt_bc'] and r[20]*256+r[21]==out['alt_de'] and r[22]*256+r[23]==out['alt_hl'],(vertices,mode,r[16:24],out)
  for p,value in m.writes:
   if 0<=p<0x4000:
    assert value==outside_original[p],(vertices,mode,p,value,outside_original[p]);outside_writes+=1
   else:assert 0x4000<=p<0x5800 or 0x7FFC<=p<0x7FFE or 0xD200<=p<0xD518 or 0xFFD0<=p<0xFFE0,(vertices,mode,p,value)
  # Проверка значений попыток записи в ROM отдельно от подавленных симулятором записей.
  if mode < 5:
   for p,value in m.rom_write_attempts:
    assert value==outside_original[p],(vertices,mode,p,value,outside_original[p]);outside_writes+=1
  else:
   assert [(p,v) for p,v in m.writes if 0x4000<=p<0x5800]==[(p,v) for p,v in expected_writes if p>=0x4000],(vertices,mode)
   assert m.rom_write_attempts==[(p,v) for p,v in expected_writes if p<0x4000],(vertices,mode)
   literal_rom_attempts+=len(m.rom_write_attempts)
  cases+=1;mode_cases[mode]+=1
 # Проверка пяти согласованных режимов, границ байтов, чётных высот и обоих знаков наклона.
 for height in range(1,17):
  for width in range(1,33):
   for mode in range(5):
    check(((3,5),(3,5+width),(3+height,5+width),(3+height,5)),mode)
    check(((3,5),(3+height,5+width),(3+height,5)),mode)
    check(((3,5+width),(3+height,5+width),(3+height,5)),mode)
 # Проверка выпуклых контуров с разными начальными вершинами и строками экранных границ.
 rng=random.Random(0xD41B)
 for _ in range(2048):
  vertices=hull([(rng.randrange(192),rng.randrange(256)) for _ in range(rng.randrange(3,12))])
  if len(vertices)<3:continue
  shift=rng.randrange(len(vertices));vertices=vertices[shift:]+vertices[:shift];check(vertices,rng.randrange(5))
 # Проверка раннего выхода без переключения SP на каждой экранной строке.
 for row in range(192):
  for mode in range(5):check(((row,3),(row,19),(row,37)),mode)
 # Проверка накопления исходной ошибки экранного адреса при схлопывании к колонке 255.
 for height in (2,3,8,16,31,64,127,191):
  for mode in range(5):check(((0,254),(0,255),(height,255)),mode)
 # Наклонные, прямые и вырожденные контуры с буквальными парами для индексов 5..7.
 for mode in range(5,8):
  for height in range(1,17):
   for width in range(1,33):
    check(((3,5),(3,5+width),(3+height,5+width),(3+height,5)),mode)
    check(((3,5),(3+height,5+width),(3+height,5)),mode)
    check(((3,5+width),(3+height,5+width),(3+height,5)),mode)
  for row in range(192):check(((row,3),(row,19),(row,37)),mode)
  for height in (2,3,8,16,31,64,127,191):check(((0,254),(0,255),(height,255)),mode)
  for _ in range(384):
   vertices=hull([(rng.randrange(192),rng.randrange(256)) for _ in range(rng.randrange(3,12))])
   if len(vertices)<3:continue
   shift=rng.randrange(len(vertices));check(vertices[shift:]+vertices[:shift],mode)
 report=dict(passed=True,cases=cases,cases_by_mode=dict(mode_cases),independent_geometric_edge_intersections=True,full_6144_byte_bitmap=True,consistent_fill_modes=[0,1,2,3,4],literal_edge_mask_modes=[5,6,7],normal_game_use_of_modes_5_to_7_proved=False,top_included_bottom_excluded=True,left_included_right_excluded_for_consistent_modes=True,signed_half_up_edge_rounding=True,real_sprite_line_table_setup=True,all_writes_accounted_for=True,ignored_rom_write_attempts_with_unchanged_values=outside_writes,literal_modes_rom_write_attempts=literal_rom_attempts,original_column_255_address_drift_preserved=True,caller_hl_preserved=True,convex_onscreen_profile=True,exact_full_register_contract_proved=True,degenerate_horizontal_contours_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 assert refresh_seeds==set(range(256))
 report.update(full_R_from_original_opcode_M1_checked=True,each_R_increment_and_bit7_checked=True,
  original_instructions_checked=562,original_code_bytes_checked=856,mutable_operand_bytes_checked=18,
  immutable_code_preserved_by_every_CPU_write=True,R_initial_values=256,I_IM_IFF_preserved=True,
  full_m1_total=m1_total,stepped_instructions_total=instruction_total,m1_bounds_by_mode=refresh_by_mode,
  full_joint_R_input_product=False,independent_whole_control_flow_M1_oracle=False,
  hardware_refresh_timing_proved=False)
 (ROOT/'Tools/Disasm/Reports/PreviewPolygonVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

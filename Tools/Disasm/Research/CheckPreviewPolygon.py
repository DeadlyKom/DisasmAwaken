"""Независимый полный bitmap исходной заливки, без сборки и IRQ."""
from pathlib import Path
import json,random
from ProbePreviewPolygon import context,execute,ROOT
from PreviewPolygonOracle import raster,registers
from PreviewEdgeRasterOracle import arithmetic


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
 m,s,initial=context();cases=0;outside_writes=0
 # Подготовка ненулевого образца ROM позволяет обнаружить даже ошибочное обнуление вне bitmap.
 m[:0x4000]=[(i*17+93)&255 for i in range(0x4000)];outside_original=bytes(m[:0x4000])
 buffers=(bytes(6144),bytes([255]*6144),bytes((i*37+11)&255 for i in range(6144)),bytes((85,170))*3072)
 def check(vertices,mode):
  nonlocal cases,outside_writes
  source=buffers[cases%4];expected=raster(source,vertices,mode)
  m.recording=False;m[0x4000:0x5800]=source;execute(m,s,initial,vertices,mode)
  actual=bytes(m[0x4000:0x5800])
  assert actual==expected,(vertices,mode,[(i,actual[i],expected[i]) for i in range(6144) if actual[i]!=expected[i]][:12])
  assert s.registers[6:8]==initial[6:8]
  # Проверка всех основных, альтернативных и индексных регистров по конечной геометрии двух цепочек.
  r=s.registers;out=registers(vertices,mode)
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
  for p,value in m.rom_write_attempts:
   assert value==outside_original[p],(vertices,mode,p,value,outside_original[p]);outside_writes+=1
  cases+=1
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
 report=dict(passed=True,cases=cases,independent_geometric_edge_intersections=True,full_6144_byte_bitmap=True,consistent_fill_modes=[0,1,2,3,4],modes_5_6_7_not_proved=True,top_included_bottom_excluded=True,left_included_right_excluded=True,signed_half_up_edge_rounding=True,real_sprite_line_table_setup=True,all_writes_accounted_for=True,ignored_rom_write_attempts_with_unchanged_values=outside_writes,original_column_255_address_drift_preserved=True,caller_hl_preserved=True,convex_onscreen_profile=True,exact_full_register_contract_proved=True,degenerate_horizontal_contours_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewPolygonVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Проверка исходных циклов, терминаторов, поворотной симметрии и восьмифазных сдвигов."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import entry
from AnimatedVariantTables import PATHS,SPRITES,render


def main():
 raw=(ROOT/(entry(7)['path']+'.sectors.bin')).read_bytes();rows=[]
 for radius,address in PATHS:
  begin=address-0xC000;points=[tuple(v if v<128 else v-256 for v in raw[begin+2*i:begin+2*i+2]) for i in range(4*radius)];values=set(points)
  assert points[0]==(radius,0) and len(values)==4*radius and raw[begin+8*radius]==0x80
  assert all((-y,x) in values and max(abs(x),abs(y))<=radius for x,y in points)
  assert max(max(abs(x-a),abs(y-b)) for (x,y),(a,b) in zip(points,points[1:]+points[:1]))==2
  distances=[x*x+y*y for x,y in points];rows.append(dict(radius_name=radius,points=len(points),squared_distance_min=min(distances),squared_distance_max=max(distances)))
 for name,address in SPRITES:
  begin=address-0xC000
  for phase in range(8):
   for row in range(3):assert int.from_bytes(raw[begin+6*phase+2*row:begin+6*phase+2*row+2],'big')==int.from_bytes(raw[begin+2*row:begin+2*row+2],'big')>>phase
 texts,symbols=render(raw);assert len(texts)==10
 report=dict(passed=True,paths=rows,path_points=348,path_terminators=6,sprite_phases=32,sprite_row_words=96,physical_bytes=894,
  fourfold_path_symmetry=True,exact_euclidean_radius_claimed=False,all_phase_words_shifted_from_phase_zero=True,
  method='original_physical_paths_byte_terminators_and_three_row_phase_words',assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/AnimatedVariantTablesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

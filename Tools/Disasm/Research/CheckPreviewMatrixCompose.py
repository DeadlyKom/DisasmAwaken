"""Проверка композиции матриц и четырёх точных перестановок столбцов D54C."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewModelMatrixOracle import matrix
from PreviewMatrixComposeOracle import compose,SCENE,MODEL,OUTPUT
from ReferenceControlsPointRespawn import refresh


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;branches=collections.Counter();composed_frames=0;m1_by_branch=collections.defaultdict(set)
 def check(scene,model,flags,angle):
  nonlocal cases
  expected=compose(scene,model,flags,angle);m.recording=False;m[0xCEFA]=flags;m[0xC21F]=angle
  for addresses,values in ((SCENE,scene),(MODEL,model)):
   for row in range(3):
    for column in range(3):m[addresses[row][column]]=values[row][column]
  for row in OUTPUT:
   for pointer in row:m[pointer]=0xA5
  initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*73)&255,cases&1,cases%3
  s.registers[:]=initial;m.recording=True;m.writes=[];r=s.registers;r[24]=0xD54C;measured_m1=0
  for _ in range(1024):
   if r[24]==0x3FFF:break
   old_r=r[15];s.run();increment=(r[15]-old_r)&127
   assert increment in (1,2)
   measured_m1+=increment
  else:raise AssertionError('композиция не вернулась')
  assert measured_m1==expected['m1'] and r[15]==refresh(initial[15],expected['m1'])
  assert all(r[i]==initial[i] for i in (14,26,27))
  m1_by_branch[expected['branch']].add(measured_m1)
  wanted_writes=collections.Counter((OUTPUT[row][column],expected['output'][row][column]) for row in range(3) for column in range(3))
  assert collections.Counter((p,v) for p,v in m.writes if p in {q for row in OUTPUT for q in row})==wanted_writes
  assert [[m[p] for p in row] for row in OUTPUT]==expected['output'],(scene,model,flags,angle,expected)
  assert (r[A],r[F],r[SP],r[10]*256+r[11])==(*expected['af'],0x8000,0xCEFA),(scene,flags,angle,r[:12],expected)
  assert r[16:24]==initial[16:24] and m[0x7FFE:0x8000]==[255,63]
  targets={p for row in OUTPUT for p in row}
  if expected['branch'].startswith('quadrant'):
   assert r[H]*256+r[L]==0xC357 and r[B:E+1]==initial[B:E+1] and r[8:10]==initial[8:10]
   assert set(p for p,v in m.writes)==targets
  else:
   assert (r[H]*256+r[L],r[B]*256+r[C],r[D]*256+r[E],r[8],r[9])==(expected['hl'],expected['bc'],expected['de'],expected['ixh'],0x68),(angle,flags,r[:12],expected)
   assert set(p for p,v in m.writes)==targets|{0x7FFC,0x7FFD}
   assert m[0x7FFC]+256*m[0x7FFD]==expected['stack_return']
  cases+=1;branches[expected['branch']]+=1
 # Проверка каждого возможного байта во всех четырёх точных четвертьоборотах, включая нештатный 80.
 for angle in (0,64,128,192):
  for value in range(256):
   scene=tuple(tuple((value+17*row+53*column)&255 for column in range(3)) for row in range(3))
   for flags in (1,129,255):check(scene,((0,0,0),)*3,flags,angle)
 # Проверка всех вторых углов с реальной матрицей модели и фиксированными матрицами сцены.
 scenes=(((127,0,0),(0,127,0),(0,0,127)),((129,127,0),(0,129,127),(127,0,129)),((0,0,0),)*3)
 for angle in range(256):
  values=matrix((0,angle,0),1,raw[0x400:0x500])['values'];model=tuple(tuple(values[3*column+row] for column in range(3)) for row in range(3))
  for scene in scenes:check(scene,model,1,angle)
 rng=random.Random(0xD54C)
 # Проверка произвольных входных операндов отделена от композиции со штатным построителем матрицы.
 for _ in range(4096):
  scene=tuple(tuple(rng.randrange(256) for j in range(3)) for i in range(3));model=tuple(tuple(rng.randrange(256) for j in range(3)) for i in range(3))
  check(scene,model,rng.randrange(256),rng.randrange(256))
 for _ in range(1024):
  angles=tuple(rng.randrange(256) for i in range(3));flags=int(angles[0]==angles[2]==0);scene=tuple(tuple(rng.choice((0,1,127,129,255)) for j in range(3)) for i in range(3))
  # Исполнение настоящего производителя EF5E перед потребителем, без подмены вызовов.
  m.recording=False;m[0xCEFA]=flags;m[0xC21E:0xC221]=angles;s.registers[:]=initial;s.run(start=0xEF5E,stop=0x3FFF)
  model=tuple(tuple(m[p] for p in row) for row in MODEL)
  assert [model[row][column] for column in range(3) for row in range(3)]==list(matrix(angles,flags,raw[0x400:0x500])['values'])
  check(scene,model,flags,angles[1]);composed_frames+=1
 report=dict(passed=True,cases=cases,branches=dict(branches),real_matrix_producer_cases=composed_frames,all_bytes_in_four_quadrants=True,all_second_angles_in_one_axis_path=True,all_nine_composed_operands_checked=True,exact_registers_and_stack_writes_checked=True,independent_functional_composition=True,irq_executed=False,native_execution=False,assembly_executed=False,whole_projection_not_executed=True,direct_full_M1_and_R_scope='ComposePreviewMatrix_invocations_only',I_IM_IFF_preserved_checked=True,coefficient_write_multiplicity_checked=True,M1_by_branch={k:sorted(v) for k,v in m1_by_branch.items()},complete_joint_input_product_exhausted=False)
 (ROOT/'Tools/Disasm/Reports/PreviewMatrixComposeVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

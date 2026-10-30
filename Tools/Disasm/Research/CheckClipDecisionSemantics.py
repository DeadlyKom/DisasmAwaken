"""Проверка раскрытых условий, порядка точек и углов в обоих режимах исходных табличных входов."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from CheckRowHighlight import make_context
from CheckClipGeometry import intersection,classify
from CheckGlyphRenderer import compare_flags


def signed(value,bits):
 value&=(1<<bits)-1
 return value-(1<<bits) if value&(1<<(bits-1)) else value


def matches(condition,first,second,seen,profile):
 flag,code,taken=condition;x1,y1=first;x2,y2=second;max_x,max_y,_,_=profile
 if flag[0]=='seen':result=bool((seen|flag[2])&(1<<flag[1]))
 else:
  if flag[0]=='delta':negative=signed((x2-x1) if flag[1]=='X' else (y2-y1),16)<0
  else:
   # Расчёт четырёх числителей и знака их обёрнутой 32-битной разности, без Z80-флагов симулятора.
   products=dict(Top=y1*(x1-x2),Bottom=(y1-max_y)*(x1-x2),Left=(y1-y2)*x1,Right=(y1-y2)*(x1-max_x))
   negative=signed(products[flag[1]]-products[flag[2]],32)<0
  result=negative if code=='M' else not negative
 return result==taken


def expected(case,first,second,seen,block,profile):
 choices=[(index,path) for index,path in enumerate(case['paths']) if all(matches(c,first,second,seen,profile) for c in path['conditions'])]
 assert len(choices)==1,(case,first,second,seen,block,choices)
 index,path=choices[0];points=[];max_x,max_y,_,_=profile
 for action in path['actions']:
  kind,*args=action
  if kind=='mark':seen|=1<<args[0]
  elif kind=='corner':
   if block==0:points.append(((max_x,max_y),(0,max_y),(max_x,0),(0,0))[args[0]])
  elif kind=='second':points.append(tuple(v&255 for v in second))
  else:
   side=args[0];axis='Y' if side in ('Top','Bottom') else 'X';boundary=dict(Top=0,Bottom=max_y,Left=0,Right=max_x)[side]
   points.append(intersection(first,second,axis,boundary,profile))
 return points,seen,path['exit'],index


def main():
 _,source,_=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FF8,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 decisions=json.loads((ROOT/'Tools/Disasm/Reports/ClipDecisionPaths.json').read_text('utf-8'))
 cases={(c['first'],c['second']):c for c in decisions['cases']};coverage=set();counts=collections.Counter();max_points=0
 profiles=[(255,255,255,255),(15,23,16,24),(63,63,64,64),(127,95,128,96),(207,111,208,112),(239,175,240,176)]
 rng=random.Random(0xD4E6)
 for number,profile in enumerate(profiles):
  max_x,max_y,_,_=profile;memory[0xC000:0xC000+len(source)]=source
  if number:
   # Настройка исходным D0C3, режим BlockCode меняется только в явно описанном прямом табличном входе модели.
   memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[SP]=0x7FFE
   r=sim.registers;r[H],r[L]=max_y,max_x;r[D]=r[E]=0;sim.run(start=0xD0C3,stop=0x3FFF)
  values_x=(-256,-1,0,max_x//2,max_x-1,max_x,max_x+256);values_y=(-256,-1,0,max_y//2,max_y-1,max_y,max_y+256)
  points=[(x,y) for x in values_x for y in values_y];fixtures=[]
  for first in points:
   for second in points:
    for low in range(16 if number==0 else 2):fixtures.append((first,second,(0xF0 if low&1 else 0)|low))
  if number==0:
   representative=[(x,y) for x in (-64,64,319) for y in (-64,64,319)]
   fixtures.extend((a,b,seen) for a in representative for b in representative for seen in range(256))
  fixtures.extend(((rng.randrange(-512,768),rng.randrange(-512,768)),(rng.randrange(-512,768),rng.randrange(-512,768)),rng.randrange(256)) for _ in range(1024))
  for first,second,seen in fixtures:
   c1,c2=classify(first,profile),classify(second,profile);case=cases[c1,c2]
   for block in (0,1):
    wanted,new_seen,exit,path=expected(case,first,second,seen,block,profile)
    def packed(point,code):return b''.join((v&65535).to_bytes(2,'little') for v in point)+bytes([((~code&15)<<4)|code])
    original_points=packed(first,c1)+packed(second,c2);memory[0xDE2F:0xDE39]=original_points
    memory[0xDE39]=seen;memory[0xDE3A]=block;memory[0xDE3B]=0
    memory[0xF8FF:0xFA01]=bytes([0xA7])*258
    memory[0x7FF8:0x7FFE]=bytes([0xDD,0xD4])*3;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial
    sim.run(start=case['entry'],stop=0x3FFF);r=sim.registers
    size=memory[0xDE3B];raw=memory[0xF900:0xF900+size];actual=list(zip(raw[::2],raw[1::2]))
    assert actual==wanted and size==2*len(wanted),(number,first,second,seen,block,exit,actual,wanted)
    assert memory[0xDE39]==new_seen and memory[0xDE3A]==block and memory[0xDE2F:0xDE39]==original_points
    assert memory[0xF8FF]==memory[0xFA00]==0xA7 and memory[0xF900+size:0xFA00]==bytes([0xA7])*(256-size)
    assert r[SP]==0x8000 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24]
    assert (r[A],r[F])==((size,compare_flags(size,4)) if exit=='normal' else (0xD4,0x81))
    coverage.add((c1,c2,path));counts['block_'+str(block)]+=1;counts[exit]+=1;max_points=max(max_points,len(wanted))
 report=dict(passed=True,cases=counts['block_0']+counts['block_1'],cases_by_mode_and_exit=dict(counts),
  physical_pairs_tested=81,semantic_paths_executed=len(coverage),symbolic_paths=241,maximum_output_points=max_points,
  profiles=profiles,all_initial_corner_bytes_tested=True,high_corner_bits_preserved=True,
  method='original_direct_table_entries_against_explicit_semantic_paths_with_integer_sign_tests_and_exact_intersection_quantization',
  decision_paths_derived_from_original_graph=True,independent_geometry_proof=False,
  direct_snapshot_targets_not_live_mutated_table=True,game_reachability_of_all_direct_entries_proved=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ClipDecisionSemanticsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

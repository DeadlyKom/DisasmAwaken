"""Реальные входы D3D против явных условий, исходной арифметики и действий путей."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from Analyze import payload
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from CheckClipGeometry import classify
from PreviewFaceProductOracle import product,signed
from CheckGlyphRenderer import compare_flags


def expected(case,first,second,seen,block,profile):
 c0,r0=first;c1,r1=second;max_col,max_row,_,_=profile
 # Расчёт фактических произведений, сохраняется порядок аргументов E869.
 products={side:product(a&65535,b&65535,initial_bc=0)['result'] for side,a,b in (
  ('Top',r0,c0-c1),('Bottom',r0-max_row,c0-c1),('Left',r0-r1,c0),('Right',r0-r1,c0-max_col))}
 def matches(condition):
  flag,code,taken=condition
  if flag[0]=='seen':result=bool((seen|flag[2])&(1<<flag[1]))
  else:
   value=(c1-c0 if flag[1]=='X' else r1-r0)&65535 if flag[0]=='delta' else (products[flag[1]]-products[flag[2]])&0xFFFFFFFF
   negative=bool(value&(0x8000 if flag[0]=='delta' else 0x80000000));result=negative if code=='M' else not negative
  return result==taken
 selected=[(i,p) for i,p in enumerate(case['paths']) if all(matches(c) for c in p['conditions'])]
 assert len(selected)==1
 index,path=selected[0];points=[]
 for kind,*args in path['actions']:
  if kind=='mark':seen|=1<<args[0]
  elif kind=='corner':
   if block==0:points.append(((max_col,max_row),(0,max_row),(max_col,0),(0,0))[args[0]])
  elif kind=='second':points.append((c1&255,r1&255))
  else:
   side=args[0];horizontal=side in ('Top','Bottom');den=signed((r1-r0 if horizontal else c1-c0)&65535)
   number=products[side];negative=bool(number&0x80000000);unsigned=(number^0xFFFFFFFF) if negative else number
   assert den and unsigned<abs(den)*65536,('outside_arithmetic_contract',first,second,side)
   quotient=unsigned//abs(den)
   if negative!=(den<0):quotient^=65535
   coordinate=(quotient+(c0 if horizontal else r0))&65535;low=coordinate&255
   if horizontal:
    col=0 if coordinate&32768 else max_col if coordinate>>8 else low;points.append((col,0 if side=='Top' else max_row))
   else:
    row=0 if coordinate&32768 else low if low<192 else max_row;points.append((0 if side=='Left' else max_col,row))
 return points,seen,path['exit'],index


def main():
 raw=payload(6);m=bytearray(65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0x7FF8,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 decisions=json.loads((ROOT/'Tools/Disasm/Reports/PreviewClipDecisionPaths.json').read_text('utf-8'));cases={(c['first'],c['second']):c for c in decisions['cases']}
 profiles=((15,23,16,24),(63,63,64,64),(127,95,128,96),(207,111,208,112),(239,175,240,176),(255,255,256,256))
 rng=random.Random(0xE1EC);coverage=set();counts=collections.Counter();maximum=0
 for number,profile in enumerate(profiles):
  max_col,max_row,_,_=profile;m[0x7FFE:0x8000]=bytes((255,63));s.registers[:]=initial;r=s.registers;r[12]=0x7FFE;r[6]=max_row;r[7]=max_col;r[4]=r[5]=0
  # Настройка настоящим E011, все четыре нижних предела нулевые.
  s.run(start=0xE011,stop=0x3FFF)
  vx=(-256,-1,0,max_col//2,max_col-1,max_col,max_col+256);vy=(-256,-1,0,max_row//2,max_row-1,max_row,max_row+256)
  points=[(x,y) for x in vx for y in vy]
  fixtures=[(a,b,(0xF0 if seen&1 else 0)|seen) for a in points for b in points for seen in range(16 if number==0 else 2)]
  if number==0:
   representatives=[(x,y) for x in (-64,7,319) for y in (-64,11,319)]
   fixtures.extend((a,b,seen) for a in representatives for b in representatives for seen in range(256))
  fixtures.extend(((rng.randrange(-512,768),rng.randrange(-512,768)),(rng.randrange(-512,768),rng.randrange(-512,768)),rng.randrange(256)) for _ in range(1024))
  for first,second,seen in fixtures:
   c0,c1=classify(first,profile),classify(second,profile);case=cases[c0,c1]
   def packed(point,code):return b''.join((v&65535).to_bytes(2,'little') for v in point)+bytes((((~code&15)<<4)|code,))
   for block in (0,1):
    wanted,new_seen,exit,index=expected(case,first,second,seen,block,profile)
    m[0xC22C:0xC231]=packed(first,c0);m[0xC23C:0xC241]=packed(second,c1);m[0xC24F]=seen;m[0xC250]=block;m[0xC22B]=0;m[0xC7FF:0xC901]=bytes([0xA7])*258
    m[0x7FF8:0x7FFE]=bytes((8,0xEB))*3;m[0x7FFE:0x8000]=bytes((255,63));s.registers[:]=initial
    # Проверка исходного обработчика со всеми настоящими вложенными вызовами и кадром EAB6.
    s.run(start=case['entry'],stop=0x3FFF);r=s.registers;size=m[0xC22B];actual=list(zip(m[0xC800:0xC800+size:2],m[0xC801:0xC800+size:2]))
    assert actual==wanted and size==2*len(wanted),(number,first,second,seen,block,actual,wanted)
    assert m[0xC24F]==new_seen and m[0xC250]==block and m[0xC22C:0xC231]==packed(first,c0) and m[0xC23C:0xC241]==packed(second,c1)
    assert m[0xC7FF]==m[0xC900]==0xA7 and m[0xC800+size:0xC900]==bytes([0xA7])*(256-size)
    assert r[12]==0x8000 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24]
    if exit=='normal':assert (r[0],r[1],r[4]*256+r[5])==(size,compare_flags(size,4),0xEB08)
    else:assert (r[0],r[1],r[2]*256+r[3],r[6]*256+r[7])==(0xEB,0xA9,0xEA,0xEBF2)
    coverage.add((c0,c1,index));counts['block_'+str(block)]+=1;counts[exit]+=1;maximum=max(maximum,len(wanted))
 report=dict(passed=True,cases=counts['block_0']+counts['block_1'],cases_by_mode_and_exit=dict(counts),physical_pairs=81,semantic_paths_executed=len(coverage),symbolic_paths=241,
  maximum_output_points=maximum,profiles=profiles,all_initial_corner_bytes_tested=True,high_corner_bits_preserved=True,
  real_e011_and_all_d3d_arithmetic=True,independent_geometry_proof=False,decision_paths_derived_from_original_graph=True,
  all_final_registers_proved=False,exact_normal_and_special_frame_returns=True,irq_executed=False,native_execution=False,assembly_executed=False)
 assert len(coverage)==241
 (ROOT/'Tools/Disasm/Reports/PreviewClipCaseSemanticsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Исследование порядка геометрических пересечений D48B независимым интервальным методом, без сборки."""
from pathlib import Path
from fractions import Fraction
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,SP,H,L,D,E
from CheckRowHighlight import make_context
from CheckClipSegment import record,outcode


def intersection(first,second,axis,boundary,profile=(255,255,255,255)):
 max_x,max_y,_,_=profile
 x1,y1=first;x2,y2=second
 if axis=='Y':number=(y1-boundary)*(x1-x2);den=y2-y1;origin=x1
 else:number=(y1-y2)*(x1-boundary);den=x2-x1;origin=y1
 assert den
 magnitude=-number-1 if number<0 else number
 q=magnitude//abs(den)
 assert q<65536
 if (number<0)!=(den<0):q^=65535
 v=(q+origin)&65535
 if axis=='Y':return (0 if v&32768 else max_x if v>>8 else v,boundary)
 return (boundary,0 if v&32768 else (v&255) if (v&255)<192 else max_y)


def classify(point,profile):
 x,y=point;_,_,stop_x,stop_y=profile
 return (2 if x<0 else 1 if x>=stop_x else 0)|(8 if y<0 else 4 if y>=stop_y else 0)


def expected(first,second,original_rules=False,profile=(255,255,255,255)):
 max_x,max_y,_,_=profile
 c1,c2=classify(first,profile),classify(second,profile)
 if c1==0:first,second=second,first;c1,c2=c2,c1
 if c1&c2:return [],'common_outside'
 if c1==c2==0:return [second],'both_inside'
 lo,hi=Fraction(0),Fraction(1);entries=[];exits=[]
 # Поиск интервала внутри прямоугольника по четырём неравенствам, без таблицы игровых обработчиков.
 for axis,index in (('X',0),('Y',1)):
  maximum=(max_x,max_y)[index]
  a,b=first[index],second[index];delta=b-a
  if not delta:
   if a<0 or a>maximum:return [],'parallel_outside'
   continue
  for boundary,lower in ((0,True),(maximum,False)):
   t=Fraction(boundary-a,delta)
   entering=lower==(delta>0)
   if entering and t>lo:lo=t;entries=[(axis,boundary)]
   elif entering and t==lo:entries.append((axis,boundary))
   if not entering and t<hi:hi=t;exits=[(axis,boundary)]
   elif not entering and t==hi:exits.append((axis,boundary))
 if lo>hi:return [],'miss'
 # При совпадении параметров исходный порядок обхода углов различает вход и выход.
 if original_rules:
  preferred_entry={5:('Y',max_y),6:('X',0),9:('X',max_x),10:('Y',0)}.get(c1)
  preferred_exit={5:('X',max_x),6:('Y',max_y),9:('Y',0),10:('X',0)}.get(c2)
  entry=preferred_entry if preferred_entry in entries else entries[0] if entries else None
  exit=preferred_exit if preferred_exit in exits else exits[0] if exits else None
 else:
  entry=entries[0] if entries else None;exit=exits[0] if exits else None
 if entry is None and c1:
  entry=next((axis,(max_x,max_y)[index]) for axis,index in (('X',0),('Y',1)) if first[index]==(max_x,max_y)[index])
 if exit is None and c2:
  exit=next((axis,(max_x,max_y)[index]) for axis,index in (('X',0),('Y',1)) if second[index]==(max_x,max_y)[index])
 if original_rules and lo==hi and c1 and c2:
  clockwise=(('Y',0),('X',max_x),('Y',max_y),('X',0))
  if (clockwise.index(entry)+1)%4==clockwise.index(exit):return [],'touch'
 return [intersection(first,second,*entry,profile),second if not c2 else intersection(first,second,*exit,profile)],'touch' if lo==hi else 'cross'



def main(configured=False):
 _,source,_=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'IX':0x2468,'IY':0x5C3A},None,False)
 counts=collections.Counter();mismatches=[];pairs=collections.Counter();baseline_mismatches=0
 profiles=[(255,255,255,255)] if not configured else [(15,23,16,24),(63,63,64,64),(127,95,128,96),(207,111,208,112),(239,175,240,176)]
 rng=random.Random(0xD4DD)
 for profile in profiles:
  max_x,max_y,_,_=profile;memory[0xC000:0xC000+len(source)]=source
  memory[0x7FFE:0x8000]=bytes([255,63])
  if configured:
   # Обновление границ настоящим установщиком, классификатор получает Max+1, а не дисковый порог FF.
   sim.registers[:]=initial;r=sim.registers;r[H],r[L]=max_y,max_x;r[D]=r[E]=0
   sim.run(start=0xD0C3,stop=0x3FFF)
  vx=sorted(set((-512,-256,-1,0,1,127,254,255,256,511,512,767,max_x-1,max_x,max_x+1)))
  vy=sorted(set((-512,-256,-1,0,1,127,254,255,256,511,512,767,max_y-1,max_y,max_y+1)))
  points=[(x,y) for x in vx for y in vy]
  fixtures=[(first,second) for first in points for second in points]
  fixtures.extend(((rng.randrange(-512,768),rng.randrange(-512,768)),(rng.randrange(-512,768),rng.randrange(-512,768))) for _ in range(4096))
  # Проверка настоящего входа, включая обмен, таблицу, все арифметические вызовы и общий выход.
  for first,second in fixtures:
   def packed(point):
    c=classify(point,profile)
    return b''.join((v&65535).to_bytes(2,'little') for v in point)+bytes([((~c&15)<<4)|c])
   memory[0xDE2F:0xDE39]=packed(first)+packed(second);memory[0xDE39]=0;memory[0xDE3A]=0
   memory[0xF900:0xFA00]=bytes([0xA7])*256;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial
   sim.run(start=0xD48B,stop=0x3FFF)
   assert sim.registers[SP]==0x8000
   raw=memory[0xF900:0xF900+memory[0xDE3B]];actual=list(zip(raw[::2],raw[1::2]));wanted,kind=expected(first,second,True,profile)
   baseline_mismatches+=actual!=expected(first,second,False,profile)[0]
   pairs[classify(first,profile),classify(second,profile)]+=1;counts[kind]+=1
   if actual!=wanted:mismatches.append(dict(profile=profile,first=first,second=second,actual=actual,expected=wanted,kind=kind))
 report=dict(passed=not mismatches,cases=sum(counts.values()),outcode_pairs=len(pairs),cases_by_geometry=dict(counts),
  mismatch_count=len(mismatches),examples=mismatches,
  method='rational_slab_interval_with_original_directed_corner_ties_and_ones_complement_quantization',
  ordinary_slab_mismatches=baseline_mismatches,
  corner_block=1,configured_windows_tested=configured,profiles=profiles,all_case_algorithms_independently_proved=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/('Tools/Disasm/Reports/'+('ConfiguredClipGeometryVerification' if configured else 'ClipGeometryVerification')+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='examples'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

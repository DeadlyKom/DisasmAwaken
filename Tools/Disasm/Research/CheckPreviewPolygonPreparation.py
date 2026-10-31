"""Подготовка D41B до CheckLastRow, ранний выход и оба верхних переходника кольца."""
import json,random
from ProbePreviewPolygon import context,ROOT
from PreviewEdgeRasterOracle import arithmetic,column_context,address
from PreviewPolygonOracle import PATTERNS
from skoolkit.simutils import PC,SP


def main():
 m,s,initial=context();cases=0
 def check(vertices,mode,carry):
  nonlocal cases
  m.recording=False;m[0xC800:0xC800+2*len(vertices)]=[b for y,x in vertices for b in (x,y)]
  count=2*len(vertices);m[0xC22B]=count;m[0xC23B]=mode;m[0x7FFE:0x8000]=[255,63]
  s.registers[:]=initial;r=s.registers;r[1]=(r[1]&254)|carry;r[PC]=0xD41B;saved=r[:];m.recording=True;m.writes=[]
  for _ in range(4096):
   if r[PC] in (0xD23A,0x3FFF):break
   s.run()
  else:raise AssertionError(('preparation_limit',vertices,mode))
  low=min(y for y,x in vertices);high=max(y for y,x in vertices)
  assert m[0x7FFC:0x7FFE]==[saved[7],saved[6]] and m[0xD35F]==count-1
  if low==high:
   _,flags=arithmetic(count,1,True)
   assert r[PC]==0x3FFF and r[SP]==0x8000
   assert r[:8]==[high,0x42|(high&0x28),0,1,low,high,saved[6],saved[7]]
   assert tuple(r[16:18])==(count-1,(flags&254)|carry)
   assert r[8:12]==saved[8:12] and r[18:24]==saved[18:24]
   assert {p for p,v in m.writes}=={0x7FFC,0x7FFD,0xD35F}
  else:
   first=next(i for i,p in enumerate(vertices) if p[0]==low);left=right=first
   while vertices[(left-1)%len(vertices)][0]==low:left=(left-1)%len(vertices)
   while vertices[(right+1)%len(vertices)][0]==low:right=(right+1)%len(vertices)
   lx=vertices[left][1];rx=vertices[right][1];screen=address(low,lx)
   assert r[PC]==0xD23A and r[SP]==0xFFE0
   assert r[:8]==[low,arithmetic(0,screen&255)[1],screen>>8,screen&255,0xD1,((low&7)<<5)|(rx>>3),0xC0,right*2],(vertices,mode,r[:8])
   assert (r[8]*256+r[9],r[10]*256+r[11])==((((low&7)<<13)+lx*32+mode*2)&65535,(((low&7)<<13)+rx*32+mode*2+16)&65535)
   assert tuple(r[16:18])==(PATTERNS[mode][0],arithmetic(mode,mode)[1]) and r[18:24]==saved[18:24]
   expected={0xD35F:count-1,0xD23B:high,0xD23F:low,0xD243:low,0xD290:left*2+1,0xD291:0xC8,0xD358:right*2+1,0xD359:0xC8,0xD20C:PATTERNS[mode][1],0xD257:0,0xD4C7:screen&0xE0,0xD27E:0xFC,0xD27F:0x7F,0x7FFC:saved[7],0x7FFD:saved[6]}
   assert dict(m.writes)==expected and len(m.writes)==len(expected),(vertices,mode,m.writes,expected)
  cases+=1
 # Проверка каждого чётного размера 6..254 и разных начальных позиций плоской верхней цепочки.
 for count in range(3,128):
  vertices=[(7,31)]*(count-1)+[(190,211)]
  for mode in range(8):
   for carry in (0,1):check(vertices,mode,carry)
 # Проверка горизонтального выхода на каждой экранной строке.
 for row in range(192):
  for mode in range(8):
   for carry in (0,1):check(((row,3),(row,19),(row,37)),mode,carry)
 rng=random.Random(0xD41B)
 for _ in range(4096):
  vertices=[(rng.randrange(192),rng.randrange(256)) for _ in range(rng.randrange(3,128))]
  for carry in (0,1):check(vertices,rng.randrange(8),carry)
 wrappers=0
 # Проверка двух верхних переходников на всех входных F и всех индексах кольца.
 for flags in range(256):
  for left in (False,True):
   for index in (range(1,256,2) if left else range(256)):
    s.registers[:]=initial;r=s.registers;r[1]=flags;r[6]=0xC8;r[7]=0 if left else index;r[16]=index;saved=r[:]
    saved[7]=(index+1)&255 if left else 1
    if left:saved[1]=column_context((index+1)&255,1,flags&1)
    m.writes=[];s.run(start=0xD40F if left else 0xD416,stop=0xD452 if left else 0xD462)
    assert r[:13]==saved[:13] and r[16:24]==saved[16:24] and not m.writes;wrappers+=1
 report=dict(passed=True,cases=cases,wrapper_cases=wrappers,all_even_contour_lengths_6_through_254=True,all_eight_preparation_modes=True,all_192_horizontal_exit_rows=True,both_input_carries=True,exact_main_alternate_and_index_context=True,exact_order_independent_operand_values_and_write_count=True,no_screen_writes=True,temporary_sp_and_cpu_hl_checked=True,all_wrapper_flags_and_indices=True,stop_before_scanline_loop=True,full_modes_5_6_7_rasterization_proved=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewPolygonPreparationVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

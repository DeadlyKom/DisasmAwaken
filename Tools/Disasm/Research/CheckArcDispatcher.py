"""Диспетчер четырёх положений центра, корни с исходным Carry и независимые растровые рекурсии."""
from pathlib import Path
import json,math,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckSymmetricArc import reference as both_reference
from CheckSingleEdgeArc import reference as single_reference
from CheckGlyphRenderer import compare_flags


def reference(raw,radius,b,c,quadrant,mode,width,height):
 hx,hy=width//2,height//2;max_y=height-1;screen=bytearray(raw)
 fields=dict(OffsetY=0xA7,OffsetX=0xA7,RowY=0xA7,CenterX=0xA7,StartY=0xA7,LeftMask=0xA7,RasterDown=0xA7,SqrtTarget=0xA7A7)
 if radius<9:return screen,fields,'small_radius'
 positive_x=bool(quadrant&1);above=bool(quadrant&2)
 center_x=(hx+(b if positive_x else -b))&255;center_y=(hy+(-c if above else c))&255
 fields.update(OffsetY=c,OffsetX=b,RowY=center_y,CenterX=center_x)
 left_bound=8;right_bound=8+width-1;bottom=16+height

 def root(argument,carry=0):
  target=(radius*radius-argument*argument-carry)&65535;fields['SqrtTarget']=target
  result=math.isqrt(target);fields['StartY']=result;return result

 def draw(left_edge,down,row,left,right,counter_x,counter_y,limit=0,both=False):
  nonlocal screen
  state=(left,right,16+row,counter_x&255,counter_y&255,0,'vertical')
  fields['RasterDown']=int(down)
  if both:screen,_=both_reference(screen,0,0,0,down,mode,16,bottom,state,True)
  else:screen,_=single_reference(screen,0,0,0,left_edge,down,mode,16,bottom,state,limit)

 def draw_pair(limit):
  left=(8+((hx+b-radius)&255)) if positive_x else left_bound
  right=right_bound if positive_x else 8+((hx+radius-b)&255)
  if not positive_x:fields['LeftMask']=b
  for down in (True,False):draw(positive_x,down,center_y,left,right,-radius,0,limit)

 def far_pair(limit):
  far=hx+b;start=root(far)
  for down,row in ((False,max(0,center_y-start)),(True,min(height,center_y+start))):
   draw(positive_x,down,row,left_bound,right_bound,-far,start,limit)

 def near_vertical(carry,limit,both):
  start=root(c,carry);row=0 if above else max_y
  if both:
   fields['RowY']=row;left=8+((center_x-start)&255);right=8+((center_x+start)&255)
   fields['LeftMask']=128>>((center_x-start)&7)
   draw(True,above,row,left,right,-start,c,both=True)
  else:
   left=8+((hx+b-start-1)&255) if positive_x else left_bound
   right=right_bound if positive_x else 8+((start+hx-b)&255)
   if not positive_x:fields['LeftMask']=b
   draw(positive_x,above,row,left,right,-start,c,limit)

 def far_vertical(limit):
  far=hx+b;start=root(far);steps=(start-c)&255
  row=min(height,steps) if above else max(0,max_y-steps)
  draw(positive_x,above,row,left_bound,right_bound,-far,start,limit)

 if b<hx and c<hy:
  # Центр внутри обеих половин, сравнения радиуса различают ноль, одну и две боковые границы.
  if b+radius<hx:
   left=8+((center_x-radius)&255);right=8+((center_x+radius)&255);fields['LeftMask']=128>>((center_x-radius)&7)
   for down in (False,True):draw(True,down,center_y,left,right,-radius,0,both=True)
   return screen,fields,'inside_full_span'
  if radius<b+hx:
   draw_pair((b-hx+2)&255);return screen,fields,'inside_one_side_pair'
  far_pair((b-hx+1)&255);return screen,fields,'inside_two_x_borders'
 if b>=hx and c<hy:
  # Центр вне X, до входа в окно отбрасывается касание, затем проверяется достижение дальней границы.
  outside=b-hx
  if radius<=outside:return screen,fields,'outside_x_rejected'
  if radius-outside<width:
   draw_pair(0);return screen,fields,'outside_x_one_side_pair'
  far_pair(0);return screen,fields,'outside_x_two_borders'
 if b<hx:
  # Центр вне Y, строгий заём сравнения с ближней X-границей передаёт единицу в корень.
  c-=hy;fields['OffsetY']=c
  if radius<c:return screen,fields,'outside_y_rejected'
  cross=radius*radius-c*c
  if cross<(hx-b)*(hx-b):
   near_vertical(1,0,True);return screen,fields,'outside_y_both_edges'
  limit=(b-hx+3)&255
  if cross>=(hx+b)*(hx+b):
   far_vertical(limit);return screen,fields,'outside_y_far_vertical'
  near_vertical(1,limit,False);return screen,fields,'outside_y_one_edge'
 # Центр вне обеих осей, оба локальных смещения сначала сохранены в состоянии, заём корня равен нулю.
 b-=hx;c-=hy;fields['OffsetX']=b;fields['OffsetY']=c
 cross=radius*radius-c*c
 if cross<0 or cross<b*b:return screen,fields,'outside_xy_rejected'
 reaches_far=b+width<256 and cross>=(b+width)*(b+width)
 b+=hx;fields['OffsetX']=b
 if reaches_far:
  far_vertical(0);return screen,fields,'outside_xy_far_vertical'
 near_vertical(0,0,False);return screen,fields,'outside_xy_one_edge'


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 cases=0;paths={};rng=random.Random(0xDFC3)
 addresses={'OffsetY':0xDFAF,'OffsetX':0xDFB0,'RowY':0xDFB1,'CenterX':0xDFB2,'StartY':0xDFB3,'LeftMask':0xDFB8,'RasterDown':0xDFB9}
 for profile,(width,height) in enumerate(((16,24),(64,64),(128,128),(240,176))):
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=height-1,width-1;r[D]=r[E]=0;sim.run(start=0xD0C3,stop=0x3FFF)
  def check(radius,b,c,q,mode,pattern):
   nonlocal cases
   raw=bytes([pattern])*0x1B00;expected,fields,path=reference(raw,radius,b,c,q,mode,width,height)
   memory[0x4000:0x5B00]=raw;memory[0xDFAB:0xDFAF]=bytes([c,b,q,radius]);memory[0xDFAF:0xDFB4]=bytes([0xA7])*5
   memory[0xDFB6:0xDFBA]=bytes([0xA7])*4;memory[0xDFC4]=1 if mode==0x38 else 0
   sim.registers[:]=initial;r=sim.registers;r[F]=(radius^b^c)&255;r[17]=(q*37)&255
   sim.run(start=0xDFC3,stop=0x3FFF)
   assert memory[0x4000:0x5B00]==expected,(width,height,radius,b,c,q,mode,pattern,path,[(hex(i+0x4000),a,v) for i,(a,v) in enumerate(zip(memory[0x4000:0x5B00],expected)) if a!=v][:12])
   for field,address in addresses.items():assert memory[address]==fields[field],(width,height,radius,b,c,q,path,field,memory[address],fields[field])
   assert int.from_bytes(memory[0xDFB6:0xDFB8],'little')==fields['SqrtTarget'],(width,height,radius,b,c,q,path,'sqrt_target')
   assert all(memory[address]==mode for address in (0xE426,0xE438,0xE44F,0xE460))
   assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[14]==initial[14]
   if radius<9:assert (r[A],r[F])==(radius,compare_flags(radius,9)) and r[16:24]==initial[16:24][:1]+[(q*37)&255]+initial[18:24]
   cases+=1;paths[path]=paths.get(path,0)+1
  xs=sorted({0,1,width//2-1,width//2,width//2+1,127,191,255});ys=sorted({0,1,height//2-1,height//2,height//2+1,127,191,255})
  # Проверка граничных смещений во всех квадрантах, двух режимах и двух прежних рисунках.
  for radius in range(256) if profile==3 else (0,8,9,15,40,80,120,160,200,255):
   for b in xs:
    for c in ys:
     for q in range(4):
      for mode in (0x38,0x30):
       for pattern in (0,0xA7):check(radius,b,c,q,mode,pattern)
  # Проверка независимых байтов параметров, включая старшие разряды QuadrantCode.
  for _ in range(4096):check(rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.choice((0x38,0x30)),0xA7)
  print(json.dumps(dict(profile=[width,height],cases_so_far=cases),ensure_ascii=False),flush=True)
 report=dict(passed=True,cases=cases,paths=paths,method='original_entire_DFC3_with_independent_four_center_cases_integer_square_roots_and_pixel_recurrences_full_bitmap_and_work_fields',
  window_profiles=[[16,24],[64,64],[128,128],[240,176]],all_radius_bytes_in_base_profile=True,
  input_square_root_borrow_preserved=True,quadrant_high_bits_randomized=True,
  arbitrary_window_profiles_proved=False,full_C000_proved=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ArcDispatcherVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

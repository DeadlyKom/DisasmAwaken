"""Выбор шага панорамирования, исходное ограничение Sign и полный внутренний цикл с двумя HALT."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckSignedMultiply import sbc16_flags
from CheckMapSectorTables import reference as sector_reference
from CheckVisibleMapPoints import visible_points
from CheckInsetFrame import bitmap_address


def updated(origin,dx,dy):
 old_x,old_y=origin
 def axis(old,delta):
  candidate=(old+delta)&65535
  return old if candidate&32768 else candidate
 x,y=axis(old_x,dx),axis(old_y,dy);old_high=((old_y>>8)<<8)|(old_x>>8);new_high=((y>>8)<<8)|(x>>8)
 changed=int(old_high!=new_high)
 return x,y,changed,(old_high-new_high)&65535,sbc16_flags(old_high,new_high,0) if changed else 0x44


def direction(geometry,px,py):
 x,y,width,height=geometry;packed=(((y<<8)|x)*8)&65535
 rx=(px-(packed&255))&255;ry=(py-(packed>>8))&255
 threshold=(((5*width)&255)+(width>>2))>>1;vertical=((height<<2)|(height>>6))&255
 if rx<threshold:return -8,0
 if rx-threshold>=threshold:return 8,0
 return 0,-8 if ry<vertical else 8


def main():
 station,map_source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:]=bytes(banks[0]);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0xF1AD,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 updater_cases=direction_cases=whole=steps=0
 input_cases=0
 # Проверка исходного RRA после объединения для всех байтов, включая неописанные биты F 3 и 5.
 for code in range(256):
  memory[0x66EC]=memory[0x6585]=memory[0x658A]=0;memory[0x66ED]=code;sim.registers[:]=initial
  sim.run(start=0x6D05,stop=0x6D09);r=sim.registers
  expected=(code&0x80)|(0x40 if code==0 else 0)|(4 if code.bit_count()%2==0 else 0)|((code>>1)&0x28)|(code&1)
  assert r[A]==code>>1 and r[F]==expected and r[2:15]==initial[2:15] and r[16:24]==initial[16:24];input_cases+=1
 def check(start,origin,delta,geometry=None,pointer=None):
  nonlocal steps
  old_x,old_y=origin;dx,dy=delta;memory[0x6300:0x6304]=bytes([old_x&255,old_y&255,old_x>>8,old_y>>8]);memory[0x6D7B]=0xA7
  memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers
  if geometry is not None:memory[0xF1AD:0xF1B1]=bytes(geometry);memory[0x6307:0x6309]=bytes(pointer)
  else:r[H],r[L]=dy&255,dx&255
  x,y,changed,difference,flags=updated(origin,dx,dy);sim.run(start=start,stop=0x6CFE)
  assert memory[0x6300:0x6304]==bytes([x&255,y&255,x>>8,y>>8]) and memory[0x6D7B]==changed
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[SP])==(difference,((dy&255)<<8)|(dx&255),((y>>8)<<8)|(x>>8),changed,flags,0x7FFE),(start,origin,delta,geometry,pointer,list(r))
  assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];steps+=bool(changed)
 # Проверка каждого 16-битного начала обеих осей и четырёх направлений, Sign проверяется после оборачиваемого сложения.
 for value in range(65536):
  for delta in ((-8,0),(8,0),(0,-8),(0,8)):
   check(0x6CAA,(value,(value*313+0xA7F5)&65535),delta);updater_cases+=1
 # Проверка всех байтов ширины и горизонтальной позиции, включая перенос упакованного начала.
 for width in range(256):
  geometry=((width*13)&255,(width*17)&255,width,(width*37)&255)
  for px in range(256):
   py=(px*53+width)&255;delta=direction(geometry,px,py)
   check(0x6C6E,(((width*257)^(px*313))&65535,((px*257)^(width*149))&65535),delta,geometry,(px,py));direction_cases+=1
 # Проверка всех байтов высоты и вертикальной позиции в принудительно выбранной средней X-зоне.
 for height in range(256):
  geometry=(1,1,20,height)
  for py in range(256):
   delta=direction(geometry,83,py);check(0x6C6E,(height*257,py*257),delta,geometry,(83,py));direction_cases+=1
 baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912))
 for scenario in ((origin,iterations) for origin in ((0,0),(0x00FC,0x12FC),(0x7FFC,0x7FFC),(0xFFF8,0xFFF8)) for iterations in (1,2,3)):
  origin,iterations=scenario
  for pointer in ((8,43),(78,43),(48,8),(48,78)):
   for mode in (0,1):
    m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);m[0x6306]=0x10;s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
    put(m,0x6DA9,[11,0]);put(m,0xF1AD,[1,1,12,12,0,0]);put(m,0x6307,pointer);put(m,0x7FFE,[255,63]);s.registers[:]=initial;r=s.registers
    r[B],r[C],r[D],r[E]=1,1,12,12;s.run(start=0xC233,stop=0x3FFF)
    # Подготовка действительных экранных таблиц и отсечения для нулевых запросов в полном панорамировании.
    m.out7ffd(0x11);m[0x6306]=0x11;put(m,0x7FFE,[255,63]);s.registers[:]=initial;r[D],r[E]=8,8;s.run(start=0xC49B,stop=0x3FFF)
    put(m,0x7FFE,[255,63]);s.registers[:]=initial;r[H],r[L]=71,79;r[D]=r[E]=0;s.run(start=0xD0C3,stop=0x3FFF);m.out7ffd(0x10);m[0x6306]=0x10
    old_x,old_y=origin;put(m,0x6300,[old_x&255,old_y&255,old_x>>8,old_y>>8]);put(m,0x6304,[80,72])
    m[0x6D75]=m[0x6D90]=0;m[0x6D7B]=0xA7;m[0x99B4]=mode
    put(m,0x983F,bytes([0xF0])*4+bytes([0]));put(m,0x9844,bytes([0xF0])*4+bytes([0]));put(m,0x988E,[0,0]);m[0x990A]=0x80;m[0x993D]=0xFF;m[0x99A3]=0x80;put(m,0x6309,[0x3D,0x99])
    put(m,0x8600,bytes(768));put(m,0x9A8D,[255,255]);put(m,0x9A90,[0x58,0x9A]);m[0x6548]=1;m[0x9B16]=0
    for address in (0x66EC,0x6585,0x66ED,0x658A):m[address]=0
    def sectors(x,y):
     result=bytearray(1024)
     for base,sx,sy in ((0,x,y),(256,(x+1)&255,y),(512,x,(y+1)&255),(768,(x+1)&255,(y+1)&255)):result[base:base+256]=sector_reference(sx,sy)[0]
     return result
    m.banks[1][0x3200:0x3600]=list(sectors(old_x>>8,old_y>>8));dx,dy=direction((1,1,12,12),*pointer);x,y,changed,_,_=updated(origin,dx,dy);new_sectors=sectors(x>>8,y>>8)
    def compose(previous,world_x,world_y,raw):
     result=bytearray(previous)
     for row in range(72):
      address=bitmap_address(24+row,2)-0x4000;result[address:address+10]=bytes([0 if mode else 255])*10
     for _,px,py in visible_points(raw,world_x&255,world_y&255,80,72):
      sx,sy=16+px,24+py;result[bitmap_address(sy,sx//8)-0x4000]^=128>>(sx&7)
     return result
    clean=bytearray(baseline);snapshot=bytearray(baseline);put(m,0x4000,baseline);put(m,0x7FFE,[255,63]);s.registers[:]=initial;r[PC]=0x6C6E;trace.writes.clear();wakeups=completed=0
    for step in range(300000*iterations):
     if r[PC]==0x3FFF:break
     if r[PC]==0x6D05 and m.o7ffd&7==0:
      # Проверка завершённого рисунка каждой итерации до чтения действия и подготовки следующего шага.
      if completed:x,y,changed,_,_=updated((x,y),dx,dy);new_sectors=sectors(x>>8,y>>8)
      expected_clean=compose(clean,x,y,new_sectors);expected=pointer_image(list(expected_clean),station,*pointer)
      assert m[0x6300:0x6304]==[x&255,y&255,x>>8,y>>8] and m[0x6D7B]==changed and m[0x6D75]==m[0x6D90]==0
      assert m[0x4000:0x5B00]==expected and m.banks[7][:6912]==list(snapshot) and m.banks[1][0x3200:0x3600]==list(new_sectors),(origin,pointer,mode,iterations,completed)
      clean=expected_clean;snapshot=bytearray(expected);completed+=1;m[0x66ED]=int(completed<iterations)
     halt=(r[PC]==0xC14B and m.o7ffd&7==1) or (r[PC]==0x6D4A and m.o7ffd&7==0)
     if halt:assert m[r[PC]]==0x76;r[PC]+=1;wakeups+=1
     else:s.run()
    else:raise AssertionError('Панорамирование не вернулось за заданное число шагов')
    assert completed==iterations and r[A]==0 and r[F]==0x44 and r[8:12]==initial[8:12] and r[SP]==0x8000 and m[0x6306]==0x10 and wakeups==2*iterations
    assert [v for port,v in trace.writes if port==0x7FFD]==[0x17,0x18,0x19,0x18,0x10]*iterations;whole+=1
 report=dict(passed=True,all_word_origin_cases=updater_cases,byte_geometry_direction_cases=direction_cases,sector_high_change_cases=steps,
  whole_pan_branch_cases=whole,maximum_normal_step=8,negative_candidate_is_undone_not_clamped=True,wrapped_positive_candidate_accepted=True,
  method='original_pan_direction_and_origin_update_integer_model_then_real_shadow_refresh_independent_bitmap_composition',
  full_outer_6C0D_dispatcher_tested=False,whole_branch_iterations=[1,2,3],action_tail_flag_cases=input_cases,completed_pan_steps=192,empty_stored_lists=True,zero_arc_radius=True,pointer_owner_code=0,
  explicit_halt_wakeups=384,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapPanVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

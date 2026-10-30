"""Станционный 6D58, реальные строители и настройка, банковый C000 и независимый секторный bitmap."""
from pathlib import Path
from itertools import product
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckInsetFrame import bitmap_address
from CheckMapScreenTables import reference as screen_reference
from CheckMapSectorTables import reference as sector_reference
from CheckMapRasterSetup import expected as setup_reference
from CheckVisibleMapPoints import visible_points


def main():
 station,map_source,banks=make_context();baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912));cases=rejected=pixels=0
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 def fixture(rectangle=(1,1,12,12),page=0x10):
  memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);memory[0x6306]=page
  put(memory,0x6DA9,[11,0]);put(memory,0xF0FD+16*11,bytes(rectangle)+bytes([0,0]));put(memory,0x4000,baseline);put(memory,0x7FFE,[255,63])
  sim=Simulator(memory);trace=PortTrace(sim);sim.set_tracer(trace);sim.registers[:]=initial
  return memory,sim,trace
 # Проверка раннего отказа геометрии до записи размеров, масок и переключения банков.
 for rectangle in ((128,1,8,8),(1,128,8,8),(1,1,3,8),(1,1,8,3),(30,1,8,8),(1,22,8,8)):
  memory,sim,trace=fixture(rectangle);put(memory,0x6304,[0xA7,0x5A]);memory[0x6D75]=memory[0x6D7B]=memory[0x6D90]=0xA7
  sim.run(start=0x6D58,stop=0x3FFF);r=sim.registers
  assert not r[F]&1 and r[SP]==0x8000 and not trace.writes and memory[0x6304:0x6306]==[0xA7,0x5A]
  assert memory[0x6D75]==memory[0x6D7B]==memory[0x6D90]==0xA7 and memory[0x4000:0x5B00]==list(baseline)
  assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24];rejected+=1
 # Проверка полного байта каждого запроса, двух режимов показа и трёх мировых начал.
 for rectangle,(screen_code,sector_code,clip_code),page,world,mode in product(
  ((0,0,4,4),(1,1,12,12),(0,0,32,24)),product((0,1,0x80,0xFF),repeat=3),(0x10,0x18),
  ((0,0,0,0),(64,128,7,11),(255,255,255,255)),(0,1)):
  x,y,width,height=rectangle;w,h=8*(width-2),8*(height-3);ox,oy,hx,hy=world
  memory,sim,trace=fixture(rectangle,page);r=sim.registers
  # Настройка внутреннего окна настоящим C233 до входа рисователя содержимого.
  r[B],r[C],r[D],r[E]=y,x,height,width;sim.run(start=0xC233,stop=0x3FFF)
  put(memory,0x6300,bytes(world));memory[0x99B4]=mode;memory[0x6D75]=screen_code;memory[0x6D7B]=sector_code;memory[0x6D90]=clip_code
  put(memory,0x983F,bytes([0xF0])*4+bytes([0]));put(memory,0x9844,bytes([0xF0])*4+bytes([0]));put(memory,0x988E,[0,0])
  memory[0x990A]=0x80;memory[0x993D]=0xFF;memory[0x99A3]=0x80;put(memory,0x6309,[0x3D,0x99])
  expected_screen,_,_=screen_reference(memory,8*x,8*y)
  memory.banks[1][0x2E00:0x3200]=[0xA7]*1024 if screen_code else list(expected_screen)
  expected_sectors=bytearray((i*73+(i>>3)*19+17)&255 for i in range(1024))
  if sector_code:
   for base,sx,sy in ((0,hx,hy),(256,(hx+1)&255,hy),(512,hx,(hy+1)&255),(768,(hx+1)&255,(hy+1)&255)):
    expected_sectors[base:base+256]=sector_reference(sx,sy)[0]
  memory.banks[1][0x3200:0x3600]=[0xA7]*1024 if sector_code else list(expected_sectors)
  wanted_setup,_,_=setup_reference(dict(enumerate(expected_screen,0xEE00)),w-1,h-1,0,0)
  old_setup={a:memory.banks[1][a-0xC000] for a in wanted_setup}
  put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;trace.writes.clear();sim.run(start=0x6D58,stop=0xC000)
  assert memory.o7ffd==(page|1) and memory[0x6304:0x6306]==[w,h] and r[A]==mode
  assert memory[0xEE00:0xF200]==list(expected_screen) and memory[0xF200:0xF600]==list(expected_sectors)
  assert all(memory[a]==v for a,v in (wanted_setup if clip_code else old_setup).items())
  assert memory[0x4000:0x5B00]==list(baseline)
  expected=bytearray(baseline)
  for _,px,py in visible_points(expected_sectors,ox,oy,w,h):
   sx,sy=8*x+8+px,8*y+16+py;expected[bitmap_address(sy,sx//8)-0x4000]^=128>>(sx&7);pixels+=1
  sim.run(stop=0xC14B);assert memory[0xC14B]==0x76;r[PC]=0xC14C;sim.run(stop=0x3FFF)
  assert memory[0x4000:0x5B00]==list(expected),(rectangle,screen_code,sector_code,clip_code,page,world,mode)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(expected_sectors[-1]*256+expected_sectors[-2],(oy<<8)|ox,0,(1-h)&255,0,0x44,0x8000)
  assert r[10:12]==initial[10:12] and memory[0x6D75]==0 and memory[0x6D90]==0 and memory[0x6D7B]==sector_code
  assert memory[0x6300:0x6304]==list(world) and memory[0x6306]==page and memory.o7ffd==page
  assert [v for port,v in trace.writes if port==0x7FFD]==[page|1,page]
  assert memory.banks[1][0x22E:0x230]==[0xFC,0x7F] and memory.banks[1][0x1FC4]==mode
  cases+=1
 wrapper_cases=wrapper_rejections=wrapper_wakeups=0
 # Проверка полного рисователя записи 11, включая рамку, три установки запросов и последовательный вход 6D58.
 for rectangle,flags,mode,page in product(((0,0,4,4),(1,1,12,12),(0,0,32,24),(1,1,3,6)),(0,0xE1),(0,1),(0x10,0x18)):
  x,y,width,height=rectangle;memory,sim,trace=fixture(rectangle,page);r=sim.registers
  put(memory,0xF0FD+11*16+4,[flags,0]);put(memory,0x8500,bytes([0x80,0xFF])*128);put(memory,0x8600,bytes(768));put(memory,0xE399,b'\nA\n'+bytes([10])*1021)
  memory[0x99B4]=mode;memory[0x6548]=1;memory[0x9B16]=1;put(memory,0x6300,[0,0,7,11])
  put(memory,0x983F,bytes([0xF0])*4+bytes([0]));put(memory,0x9844,bytes([0xF0])*4+bytes([0]));put(memory,0x988E,[0,0]);memory[0x990A]=0x80;memory[0x993D]=0xFF;memory[0x99A3]=0x80;put(memory,0x6309,[0x3D,0x99])
  r[PC]=0x6DA8;wakeups=0
  for step in range(300000):
   if r[PC]==0x6D58:break
   if r[PC]==0xC089 and memory.o7ffd&7==0:
    assert memory[r[PC]]==0x76;r[PC]+=1;wakeups+=1
   else:sim.run()
  else:raise AssertionError('Рисователь рамки не достиг содержимого карты')
  assert memory[0x6D75]==memory[0x6D7B]==memory[0x6D90]==1 and wakeups==1
  caption_bitmap=bytes(memory[0x4000:0x5B00])
  if width<4:
   sim.run(stop=0x3FFF);assert not r[F]&1 and memory[0x4000:0x5B00]==list(caption_bitmap) and not trace.writes
   assert memory[0x6D75]==memory[0x6D7B]==memory[0x6D90]==1;wrapper_rejections+=1
  else:
   w,h=8*(width-2),8*(height-3);wanted_sectors=bytearray(1024)
   for base,sx,sy in ((0,7,11),(256,8,11),(512,7,12),(768,8,12)):wanted_sectors[base:base+256]=sector_reference(sx,sy)[0]
   expected=bytearray(caption_bitmap)
   for _,px,py in visible_points(wanted_sectors,0,0,w,h):
    sx,sy=8*x+8+px,8*y+16+py;expected[bitmap_address(sy,sx//8)-0x4000]^=128>>(sx&7)
   sim.run(stop=0xC14B);assert memory.o7ffd&7==1 and memory[0xC14B]==0x76;r[PC]=0xC14C;wakeups+=1;sim.run(stop=0x3FFF)
   assert memory[0x4000:0x5B00]==list(expected) and r[A]==0 and r[F]==0x44 and memory[0x6D75]==memory[0x6D90]==0 and memory[0x6D7B]==1
   assert memory[0x6306]==page and memory.o7ffd==page and [v for port,v in trace.writes if port==0x7FFD]==[page|1,page]
  assert r[SP]==0x8000 and r[10:12]==initial[10:12];wrapper_cases+=1;wrapper_wakeups+=wakeups
 refresh_cases=clear_cases=refresh_wakeups=0
 # Проверка очистки перед общим проходом и полной перерисовки через снимок банка 7.
 for rectangle,mode,page,whole in product(((0,0,4,4),(1,1,12,12),(0,0,32,24),(1,1,3,6)),(0,1),(0x10,0x18),(False,True)):
  x,y,width,height=rectangle;memory,sim,trace=fixture(rectangle,page);r=sim.registers
  r[B],r[C],r[D],r[E]=y,x,height,width;sim.run(start=0xC233,stop=0x3FFF)
  put(memory,0x6300,[0,0,7,11]);memory[0x99B4]=mode;memory[0x6D75]=memory[0x6D7B]=memory[0x6D90]=1
  put(memory,0x983F,bytes([0xF0])*4+bytes([0]));put(memory,0x9844,bytes([0xF0])*4+bytes([0]));put(memory,0x988E,[0,0]);memory[0x990A]=0x80;memory[0x993D]=0xFF;memory[0x99A3]=0x80;put(memory,0x6309,[0x3D,0x99])
  memory[0x6548]=1;memory[0x9B16]=0;put(memory,0x6307,[255,191]);put(memory,0x8600,bytes(768));put(memory,0x9A90,[0x58,0x9A]);put(memory,0x9A8D,[255,255])
  expected=bytearray(baseline)
  if width>=4:
   for row in range(8*(height-3)):
    address=bitmap_address(8*(y+2)+row,x+1)-0x4000;expected[address:address+width-2]=bytes([0 if mode else 255])*(width-2)
   expected_sectors=bytearray(1024)
   for base,sx,sy in ((0,7,11),(256,8,11),(512,7,12),(768,8,12)):expected_sectors[base:base+256]=sector_reference(sx,sy)[0]
   for _,px,py in visible_points(expected_sectors,0,0,8*(width-2),8*(height-3)):
    sx,sy=8*x+8+px,8*y+16+py;expected[bitmap_address(sy,sx//8)-0x4000]^=128>>(sx&7)
  if whole:expected=bytearray(pointer_image(list(expected),station,255,191))
  put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r[PC]=0x6D44 if whole else 0x6D4E;trace.writes.clear();wakeups=0
  for step in range(300000):
   if r[PC]==0x3FFF:break
   halt=(r[PC]==0x6D4A and memory.o7ffd&7==0) or (r[PC]==0xC14B and memory.o7ffd&7==1)
   if halt:assert memory[r[PC]]==0x76;r[PC]+=1;wakeups+=1
   else:sim.run()
  else:raise AssertionError('Очистка и перерисовка карты не завершились')
  assert memory[0x4000:0x5B00]==list(expected),(rectangle,mode,page,whole)
  assert r[SP]==0x8000 and r[10:12]==initial[10:12] and wakeups==int(width>=4)+int(whole)
  if width>=4:assert memory[0x6D75]==memory[0x6D90]==0 and memory[0x6D7B]==1
  else:assert memory[0x6D75]==memory[0x6D90]==memory[0x6D7B]==1
  pages=[v for port,v in trace.writes if port==0x7FFD]
  if whole:
   assert memory.banks[7][:6912]==list(baseline) and memory.o7ffd==0x10 and memory[0x6306]==0x10 and r[A]==0x10 and memory[0x9B16]==0
   assert pages==([0x17,0x18,0x19,0x18,0x10] if width>=4 else [0x17,0x18,0x10]);refresh_cases+=1
  else:
   assert memory.o7ffd==page and pages==([page|1,page] if width>=4 else []);clear_cases+=1
  refresh_wakeups+=wakeups
 report=dict(passed=True,normal_banked_cases=cases,invalid_rectangle_cases=rejected,sector_pixel_xors=pixels,
  all_three_request_codes=[0,1,128,255],initial_pages=[16,24],world_origins=3,rectangles=[[0,0,4,4],[1,1,12,12],[0,0,32,24]],
  screen_and_sector_builders_real=True,all_setup_written_bytes_checked=True,sector_request_preserved=True,screen_and_setup_requests_cleared=True,
  method='entire_original_6D58_builders_setup_and_C000_against_independent_screen_sector_setup_and_visible_pixel_models',
  primary_and_selected_markers_deliberately_outside=True,arc_radius_source_zero=True,stored_lists_empty=True,
  explicit_halt_wakeup_cases=cases,whole_item_wrapper_cases=wrapper_cases,item_wrapper_geometry_rejections=wrapper_rejections,item_wrapper_halt_wakeups=wrapper_wakeups,
  item_wrapper_bitmap_check="real_caption_callee_then_independent_sector_overlay",clear_then_draw_cases=clear_cases,shadow_refresh_cases=refresh_cases,refresh_halt_wakeups=refresh_wakeups,
  refresh_bitmap_oracle="independent_body_fill_sector_recurrence_visible_pixels_pointer_and_shadow_snapshot",irq_executed=False,native_execution=False,assembly_executed=False,full_game_loop_proved=False)
 (ROOT/'Tools/Disasm/Reports/MapPanelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

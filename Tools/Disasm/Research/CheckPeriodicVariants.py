"""Периодический callback, реальное переключение банков, заливка, кластер и указатель."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckInsetFrame import bitmap_address
from CheckGlyphRenderer import compare_flags
from CheckSignedMultiply import sbc16_flags
from CheckAnimatedVariants import CURSORS,RESOURCES,STARTS,reference_cluster,dec_flags


def main():
 station,map_source,banks=make_context();baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912))
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 paths=[]
 for start in STARTS:
  end=start
  while map_source[end-0xC000]!=0x80:end+=2
  paths.append((start,end))
 def fixture(q=3,rectangle=(4,4,16,12),pointer=(0,0),last=0x788C):
  memory=SliceableMemory(banks=[bank.copy() for bank in banks],out7ffd=0x10);sim=Simulator(memory);trace=PortTrace(sim);sim.set_tracer(trace)
  memory[0x6306]=0x10;memory[0x78D7]=0;memory[0x78DC]=1;memory[0x6548]=1;memory[0x9B16]=0
  put(memory,0x6307,pointer);put(memory,0x9A8D,[255,255]);put(memory,0x9A90,[0x58,0x9A]);put(memory,0x8600,bytes(768))
  put(memory,0x9CA6,[0,0xB4]);put(memory,0xB400,last.to_bytes(2,'little')+bytes([1,1]));put(memory,0x788D,[20,0]);put(memory,0xF0FD+20*16,bytes(rectangle))
  put(memory,0x9844,q.to_bytes(2,'little')+bytes(2));put(memory,0x983F,[0x5A,0x5A,0xA5,0xA5,0]);memory[0x9848]=0;memory[0x993D]=0x80
  put(memory,0x4000,baseline);put(memory,0x7FFE,[255,63]);sim.registers[:]=initial
  return memory,sim,trace
 cadence=rectangle_cases=normal=deferred=0;port_writes=0
 # Проверка всех масок такта и двух результатов сравнения последнего обработчика без подмены GetLastDraw.
 for pattern in range(256):
  for last in (0x788C,0x7000):
   memory,sim,trace=fixture(last=last);memory[0x78DC]=pattern;r=sim.registers;rot=((pattern>>1)|(pattern<<7))&255
   if not pattern&1:
    sim.run(start=0x78D6,stop=0x3FFF)
    assert (r[A],r[F],r[SP])==(rot,0x44|(rot&0x28),0x8000) and r[2:12]==initial[2:12] and r[16:24]==initial[16:24]
   elif last!=0x788C:
    sim.run(start=0x78D6,stop=0x3FFF)
    assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==((last-0x788C)&65535,0x788C,last>>8,sbc16_flags(last,0x788C,0),0x8000)
   else:sim.run(start=0x78D6,stop=0x792E);assert r[SP]==0x7FFC
   assert memory[0x78DC]==rot and not trace.writes and memory[0x4000:0x5B00]==list(baseline);cadence+=1
 # Проверка отложенного обновления при активном элементе, маска такта не должна продвигаться.
 for active in range(1,256):
  memory,sim,trace=fixture();memory[0x78D7]=active;memory[0x9E78]=active;before=bytes(memory[0x4000:0x5B00]);sim.run(start=0x78D6,stop=0x3FFF)
  assert memory[0x78D7]==active and memory[0x78DC]==1 and not trace.writes and bytes(memory[0x4000:0x5B00])==before and sim.registers[SP]==0x8000;deferred+=1
 memory,sim,trace=fixture();x,y,width,height=4,4,16,12
 # Проверка всех экранных пикселей указателя, в том числе дополнительной ячейки слева и сверху.
 for py in range(192):
  for px in range(256):
   put(memory,0x6307,[px,py]);memory[0x78D7]=0;memory[0x78DC]=1;memory[0x6548]=1;memory[0x9B16]=0;put(memory,0x7FFE,[255,63]);sim.registers[:]=initial
   sim.run(start=0x78D6,stop=0x792E);r=sim.registers;tx,ty=px//8,py//8;inside=x-1<=tx<x+width and y-1<=ty<y+height
   assert memory[0x7942]==int(inside) and memory[0x9B16]==int(inside)
   flags=(0x42 if ty==y-1 else compare_flags(ty-y,height)) if inside else 0x44
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==((ty<<8)|tx,(y<<8)|x,height,width,int(inside),flags,0x7FFC)
   assert memory[0x7FFC:0x7FFE]==[dec_flags(3,0),2] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24];rectangle_cases+=1
 # Проверка полного нормального callback с настоящей заливкой, банковым C677 и независимой композицией bitmap.
 for q in range(8):
  count=max(q-1,0)
  for x,y,width,height in ((1,1,10,10),(4,4,16,12),(10,7,20,16),(23,15,8,8)):
   for pointer in ((0,0),(8*x,8*y),(8*(x-1),8*(y-1)),(255,191)):
    for mode in (0,1):
     memory,sim,trace=fixture(q,(x,y,width,height),pointer);r=sim.registers
     # Настройка окна исходным SetupInsetTextWindow, геометрия не подставляется в его операнды вручную.
     r[B],r[C],r[D],r[E]=y,x,height,width;sim.run(start=0xC233,stop=0x3FFF);memory[0x99B4]=mode
     if count:
      # Подготовка ресурсов тем же банковым входом, который вызывает DrawItem20.
      memory.out7ffd(0x11);memory[0x6306]=0x11;put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r[A]=count;sim.run(start=0xC781,stop=0x3FFF)
      memory.out7ffd(0x10);memory[0x6306]=0x10
     bank1=memory.banks[1];assigned=[bank1[a-0xC000]|(bank1[a-0xC000+1]<<8) for a in RESOURCES];cursors=[bank1[a-0xC000]|(bank1[a-0xC000+1]<<8) for a in CURSORS]
     expected=bytearray(baseline)
     for row in range(8*(height-3)):
      address=bitmap_address(8*(y+2)+row,x+1)-0x4000;expected[address:address+width-2]=bytes([0 if mode else 255])*(width-2)
     expected,new_cursors,mask,last_resource,last_pointer,last_x,last_y,previous,remaining,_=reference_cluster(map_source,expected,count,x,y,assigned,cursors,bank1[0x777],paths)
     put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;trace.writes.clear();sim.run(start=0x78D6,stop=0x7941)
     tx,ty=pointer[0]//8,pointer[1]//8;inside=x-1<=tx<x+width and y-1<=ty<y+height
     assert memory[0x4000:0x5B00]==list(expected),(q,x,y,pointer,mode)
     assert memory[0x7942]==int(inside) and memory[0x6306]==0x10 and memory.o7ffd==0x10
     assert [value for port,value in trace.writes if port==0x7FFD]==[0x11,0x10]
     assert [bank1[a-0xC000]|(bank1[a-0xC000+1]<<8) for a in CURSORS]==new_cursors and bank1[0x777]==mask and bank1[0x7B6]==count
     sim.run(stop=0x3FFF)
     final=pointer_image(list(expected),station,*pointer) if inside else list(expected)
     assert memory[0x4000:0x5B00]==final and r[SP]==0x8000 and (r[A],r[F])==(int(inside),0 if inside else 0x44) and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
     desired_x=(last_x+8*(x+4)+3)&255
     desired_de=(0xCD00|desired_x) if remaining&128 else last_resource+6*(desired_x&7)+5
     assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C])==(last_pointer+2,desired_de,8*(y+4)+6,8*(x+4)+3)
     assert memory[0x9B16]==0 and memory[0x6548]==(0 if inside else 1)
     normal+=1;port_writes+=len(trace.writes)
 missing_panel_cases=0
 # Проверка раннего выхода обёртки, если обработчик панели отсутствует в текущем списке.
 for last in (0x7000,0x788B,0x788D,0x7900):
  memory,sim,trace=fixture(last=last);sim.run(start=0x7885,stop=0x3FFF);r=sim.registers
  assert r[H]*256+r[L]==0x1357 and r[D]*256+r[E]==0x788C and r[A]==1 and not r[F]&0x40 and r[SP]==0x8000 and not trace.writes
  assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24];missing_panel_cases+=1
 delayed_rebuilds=halt_wakeups=0
 # Проверка отложенного перестроения через реальные BeginScreenUpdate, DrawItem20 и EndScreenUpdate.
 for q in range(8):
  count=max(q-1,0)
  for rectangle in ((1,1,10,10),(23,15,8,8),(1,1,3,6)):
   for flags in (0,0xE1):
    for mode in (0,1):
     memory,sim,trace=fixture(q,rectangle,(255,191));r=sim.registers;memory[0x78D7]=1;memory[0x9E78]=0;memory[0x99B4]=mode
     put(memory,0xF0FD+20*16+4,[flags,0]);put(memory,0x8500,bytes([0x80,0xFF])*128)
     put(memory,0xE399,b'\nA\n'+bytes([10])*1021)
     r[PC]=0x78D6;wakeups=0
     for step in range(300000):
      if r[PC]==0xA496:break
      if r[PC]==0xC089 and memory.o7ffd&7==0:
       # Только явное пробуждение настоящего HALT, ISR и аппаратные прерывания не исполняются.
       assert memory[r[PC]]==0x76;r[PC]+=1;wakeups+=1
      else:sim.run()
     else:raise AssertionError('Отложенное перестроение не достигло EndScreenUpdate')
     before_end=list(memory[0x4000:0x5B00]);before_regs=list(r)
     assert wakeups==1 and memory[0x78D7]==0 and memory[0x78DC]==1 and memory[0x6306]==0x18 and memory.o7ffd==0x18
     assert memory.banks[7][:6912]==list(baseline) and memory[0xB400:0xB404]==[0x8C,0x78,1,1]
     assert memory[0x9A89:0x9A8B]==([0xD6,0x78] if rectangle[2]>=4 else [0x58,0x9A]) and memory[0xF0FD+20*16+4]==flags
     bank1=memory.banks[1]
     for index,operand in enumerate(RESOURCES):
      resource=bank1[operand-0xC000]|(bank1[operand-0xC000+1]<<8)
      assert resource==(0 if index>=count else 0xCD93 if index==0 else 0xCD03),(q,index,resource)
     sim.run(stop=0x3FFF)
     assert memory[0x4000:0x5B00]==pointer_image(before_end,station,255,191)
     assert memory.banks[7][:6912]==list(baseline) and memory[0x6306]==0x10 and memory.o7ffd==0x10 and memory[0x9B16]==0
     assert r[2:8]==before_regs[2:8] and r[A]==0x10 and r[F]==before_regs[F] and r[8:12]==before_regs[8:12] and r[10:12]==initial[10:12] and r[SP]==0x8000, (q,rectangle,flags,mode,list(r),before_regs)
     pages=[value for port,value in trace.writes if port==0x7FFD]
     assert pages==([0x17,0x18,0x19,0x18,0x10] if count else [0x17,0x18,0x10]),pages
     delayed_rebuilds+=1;halt_wakeups+=wakeups
 report=dict(passed=True,cadence_and_last_draw_cases=cadence,deferred_active_item_cases=deferred,pointer_pixel_cases=rectangle_cases,
  whole_normal_callback_cases=normal,panel_absence_cases=missing_panel_cases,port_writes=port_writes,real_bank_1_cluster_calls=True,all_variant_count_codes=True,
  method='original_periodic_callback_real_callees_paging_and_independent_fill_cluster_pointer_bitmap_composition',
  delayed_rebuild_branch_executed=True,delayed_rebuild_cases=delayed_rebuilds,explicit_halt_wakeups=halt_wakeups,delayed_rebuild_pixel_check="callee_integration_and_independent_final_pointer_and_shadow_snapshot",pointer_owner_code=0,irq_executed=False,native_execution=False,assembly_executed=False,full_game_loop_proved=False)
 (ROOT/'Tools/Disasm/Reports/PeriodicVariantsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

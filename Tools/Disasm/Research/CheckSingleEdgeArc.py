"""Однокраевые проходы с переходом в двухкраевую рекурсию по байтовому пределу C'."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address
from CheckSymmetricArc import reference as both_reference


def reference(raw,radius,offset,cy,left_edge,down,mode,upper=16,lower=192,initial_state=None,limit_value=None):
 screen=bytearray(raw);cx=128+(offset if left_edge else -offset);left=cx-radius if left_edge else 8;right=247 if left_edge else cx+radius
 y=cy;sx=(-radius)&255;sy=error=0;phase='vertical';limit=(offset-118)&255
 if initial_state is not None:left,right,y,sx,sy,error,phase=initial_state
 if limit_value is not None:limit=limit_value
 if y==(lower if down else upper):return screen,'entry'
 def address(x):return bitmap_address(y,x//8)-0x4000
 def move_y():
  nonlocal y
  if not down and y==upper:return False
  y+=1 if down else -1
  return not down or y!=lower
 def step_y():
  nonlocal sy,error
  old=sy;sy=(sy+1)&255;error=(error+old+sy)&65535
 for _ in range(1024):
  # Инверсия только незажатого края и независимый расчёт координаты следующего пикселя.
  x=left if left_edge else right;screen[address(x)]^=128>>(x&7)
  if phase=='vertical':
   if not move_y():return screen,'row_boundary'
   step_y()
   if error&32768:continue
  if left_edge:
   old=left;left+=1
   if old//8!=left//8 and left//8>right//8:return screen,'crossed_clip_column'
  else:
   old=right;right-=1
   if old//8!=right//8 and right//8<left//8:return screen,'crossed_clip_column'
  # Приращение x разделено проверкой предела между двумя слагаемыми ошибки.
  old=sx-256;sx=(sx+1)&255;error=(error+old)&65535
  if phase=='horizontal' and sx==0:return screen,'zero_x'
  join=sx==limit;error=(error+sx-256)&65535
  if join:
   if phase=='vertical':next_phase='vertical' if error&32768 else 'horizontal'
   else:
    next_phase='horizontal'
    if error&32768:
     step_y()
     if not move_y():return screen,'join_row_boundary'
   result,reason=both_reference(screen,0,0,0,down,mode,upper,lower,(left,right,y,sx,sy,error,next_phase))
   return result,'join_'+phase+'_'+reason
  if phase=='vertical':
   if error&32768:continue
   phase='horizontal'
  elif error&32768:
   step_y()
   if not move_y():return screen,'row_boundary'
 raise AssertionError('single_edge_reference_limit')


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 sim.registers[:]=initial;sim.registers[H],sim.registers[L]=175,239;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xD0C3,stop=0x3FFF)
 cases=0;reasons={}
 for mode in (0x38,0x30):
  memory[0xDFC4]=mode==0x38;sim.registers[:]=initial;sim.run(start=0xDFC3,stop=0xDFD8)
  # Проверка обеих незажатых сторон, направлений, радиусов, смещений и прежнего bitmap.
  for radius in range(9,81):
   for offset in (0,16,32,48,64,80,96,100):
    for cy in (17,95,190):
     for left_edge in (False,True):
      for down in (False,True):
       for pattern in (0,0xA7):
        raw=bytes([pattern])*0x1B00;expected,reason=reference(raw,radius,offset,cy,left_edge,down,mode)
        memory[0x4000:0x5B00]=raw;memory[0xDFAD:0xDFB4]=bytes([1 if left_edge else 0,radius,0,offset,cy-16,0,0])
        sim.registers[:]=initial;sim.run(start=0xE248 if left_edge else 0xE260,stop=0x3FFF);r=sim.registers
        r[16],r[17]=(offset-118)&255,0x7B;r[SP]=0x7FFE;r[A]=0x5A;r[F]=(radius*37+offset)&255;saved_f=r[F]
        entry=(0xE681 if down else 0xE688) if left_edge else (0xE68F if down else 0xE696)
        sim.run(start=entry,stop=0x3FFF)
        assert memory[0x4000:0x5B00]==expected,(mode,radius,offset,cy,left_edge,down,pattern,reason,[(hex(i+0x4000),a,b) for i,(a,b) in enumerate(zip(memory[0x4000:0x5B00],expected)) if a!=b][:12])
        assert (r[A],r[F],r[SP])==(0x5A,saved_f,0x8000) and r[8:12]==initial[8:12]
        assert r[16]==(offset-118)&255
        if reason=='zero_x':
         # Проверка фактического возврата с активным набором рекурсии после незамкнутого EXX.
         assert r[B]*256+r[C]==0xFF00 and r[D]==0
         assert r[18] and r[18]&(r[18]-1)==0 and r[19] and r[19]&(r[19]-1)==0
        cases+=1;reasons[reason]=reasons.get(reason,0)+1
 report=dict(passed=True,cases=cases,exit_reasons=reasons,method='actual_setup_preparation_four_wrappers_single_edge_kernel_and_shared_tails_against_coordinate_recurrence',
  radius_range=[9,80],offset_values=[0,16,32,48,64,80,96,100],limit_formula='(OffsetX-118) AND 255',
  zero_counter_exit_leaves_EXX_swapped=True,alternate_A_limit_preserved=True,whole_E228_proved=False,whole_DFC3_dispatch_proved=False,arbitrary_clipped_inputs_proved=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SingleEdgeArcVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

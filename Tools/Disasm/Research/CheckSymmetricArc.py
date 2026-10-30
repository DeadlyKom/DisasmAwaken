"""Двухкраевой проход окружности, независимая координатная рекурсия и фактическое закрытие байтов."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address
from CheckArcClosing import fill_low,fill_high


def reference(raw,cx,cy,radius,down,mode,upper=16,lower=192,initial_state=None,force_entry_check=False):
 screen=bytearray(raw);left,right=cx-radius,cx+radius;y=cy;sx=(-radius)&255;sy=error=0;phase='vertical';reason='entry'
 if initial_state is not None:left,right,y,sx,sy,error,phase=initial_state
 def address(x):return bitmap_address(y,x//8)-0x4000
 if (initial_state is None or force_entry_check) and (left//8>=right//8 or y==(lower if down else upper)):return screen,reason
 def move_y():
  nonlocal y
  if not down and y==upper:return False
  y+=1 if down else -1
  return not down or y!=lower
 def step_y():
  nonlocal sy,error
  old=sy;sy=(sy+1)&255;error=(error+old+sy)&65535
 def step_x():
  nonlocal sx,error
  old=sx-256;sx=(sx+1)&255;error=(error+old+sx-256)&65535
 for _ in range(1024):
  # Рисование двух координатных граничных пикселей, адрес и фаза выводятся из целого X.
  screen[address(left)]^=128>>(left&7);screen[address(right)]^=128>>(right&7)
  if phase=='vertical':
   if not move_y():return screen,'row_boundary'
   step_y()
   if error&32768:continue
  # Сближение X по одному пикселю, только переход байта сравнивает адреса краёв.
  old_left=left;left+=1
  if old_left//8!=left//8 and left//8==right//8:
   if phase=='horizontal':screen[address(left)]=fill_low(screen[address(left)],mode)
   return screen,'left_byte_collision_'+phase
  old_right=right;right-=1
  if old_right//8!=right//8 and left//8==right//8:
   if phase=='horizontal':screen[address(right)]=fill_high(screen[address(right)],mode)
   return screen,'right_byte_collision_'+phase
  step_x()
  if phase=='vertical':
   if error&32768:continue
   phase='horizontal'
  else:
   if sx==0:
    screen[address(right)]=fill_low(screen[address(right)],mode);screen[address(left)]=fill_high(screen[address(left)],mode)
    return screen,'zero_x'
   if error&32768:
    step_y()
    if not move_y():return screen,'row_boundary'
 raise AssertionError('reference_iteration_limit')


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 sim.registers[:]=initial;sim.registers[H],sim.registers[L]=175,239;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xD0C3,stop=0x3FFF)
 cases=0;reasons={}
 for mode in (0x38,0x30):
  memory[0xDFC4]=mode==0x38;sim.registers[:]=initial;sim.run(start=0xDFC3,stop=0xDFD8)
  # Проверка всех радиусов 0..80, всех фаз X, восьми граничных строк, обоих направлений и двух старых рисунков.
  for radius in range(81):
   for phase in range(8):
    cx=128+phase
    for cy in (16,17,23,24,95,175,190,191):
     for down in (False,True):
      for pattern in (0,0xA7):
       raw=bytes([pattern])*0x1B00;expected,reason=reference(raw,cx,cy,radius,down,mode)
       memory[0x4000:0x5B00]=raw;memory[0xDFAD:0xDFB4]=bytes([0,radius,0,0,cy-16,cx-8,0])
       sim.registers[:]=initial;sim.run(start=0xE208,stop=0x3FFF);r=sim.registers;r[SP]=0x7FFE;r[A]=0x5A;r[F]=(radius*37+phase)&255;saved_f=r[F]
       sim.run(start=0xE69D if down else 0xE6A4,stop=0x3FFF)
       assert memory[0x4000:0x5B00]==expected,(mode,radius,phase,cy,down,pattern,reason,[(hex(i+0x4000),a,b) for i,(a,b) in enumerate(zip(memory[0x4000:0x5B00],expected)) if a!=b][:12])
       assert (r[A],r[F],r[SP])==(0x5A,saved_f,0x8000) and r[8:12]==initial[8:12]
       assert r[16:18]==initial[16:18]
       cases+=1;reasons[reason]=reasons.get(reason,0)+1
 report=dict(passed=True,cases=cases,exit_reasons=reasons,
  method='actual_setup_PrepareArcFullSpan_both_direction_wrappers_and_symmetric_kernel_against_coordinate_error_recurrence_full_bitmap',
  radius_range=[0,80],physical_center_x_range=[128,135],upper_row=16,lower_row_excluded=192,
  actual_mode_writer_executed=True,all_pixel_phases=True,byte_closing_modes=[0x38,0x30],
  single_edge_entries_proved=False,whole_DFC3_dispatch_proved=False,arbitrary_clipped_inputs_proved=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SymmetricArcVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

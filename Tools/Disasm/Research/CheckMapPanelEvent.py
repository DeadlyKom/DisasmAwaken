"""Диспетчер карты, реальные перенос и удаления списка, остановка перед отдельно проверенными ветвями."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context

CONTROLS=((0x7B52,21),(0x7BA9,12),(0x7C1F,13),(0x7C7F,14),(0x7CB7,15),(0x7D25,17),(0x7D54,16),(0x7CF9,18),(0x7690,19),(0x788D,20))


def main():
 _,_,banks=make_context();base=bytearray(65536);base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0])
 base[0x6DA9:0x6DAB]=bytes([11,0]);base[0x9E78]=0;base[0xCA20]=6;base[0x8600:0x8900]=bytes(768);base[0xAECB]=base[0xAEC7]=0;base[0xAEC7]=11;base[0x5F00:0x5F03]=bytes([0x21,63,0])
 for address,index in CONTROLS:base[address:address+2]=index.to_bytes(2,'little')
 initial=get_registers({'SP':0x7FFE,'HL':0x6DA8,'DE':11,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 early=closed=pan=select=0
 def execute(selector,flags,event=0,y=12,full=True):
  nonlocal early,closed,pan,select
  m=bytearray(base);s=Simulator(m);r=s.registers;r[:]=initial;r[A]=selector;r[F]=flags;r[PC]=0x6C0D;m[0x9839]=event;m[0x6307]=48;m[0x6308]=y;m[0x9A82]=0xA7;m[0x9A89:0x9A8B]=bytes([0xD6,0x78]);m[0x9CA6:0x9CA8]=bytes([0,0xB4]);m[0x7FFE:0x8000]=bytes([255,63])
  entries=[0x5F00]+([a-1 for a,_ in CONTROLS] if full else [])+[0x6DA8];raw=b''.join(a.to_bytes(2,'little') for a in entries)+bytes([1,1]);m[0xB400:0xB400+len(raw)]=raw
  for _ in range(15000):
   if r[PC] in (0x6C6E,0x6D0D,0x3FFF):break
   s.run()
  else:raise AssertionError(('instruction_limit',selector,event,y,hex(r[PC])))
  if selector&128:
   assert r[PC]==0x3FFF and (r[A],r[F])==(selector,(selector&0xA8)|1) and r[2:12]==initial[2:12] and r[18:24]==initial[18:24] and r[16:18]==[0xA7,initial[17]] and r[SP]==0x8000,(selector,flags,list(r),list(initial))
   assert m[0xB400:0xB400+len(raw)]==raw and m[0x9A82]==0xA7 and m[0x9A89:0x9A8B]==bytes([0xD6,0x78]);early+=1
  elif selector==1:
   assert r[PC]==0x6D0D and r[A]==0 and r[SP]==0x7FFE;select+=1
  elif event&128 or y>>3!=11>>3:
   assert r[PC]==0x6C6E and r[SP]==0x7FFE and m[0x9A82]==0xA7 and m[0xB400:0xB400+len(raw)]==raw;pan+=1
  else:
   assert r[PC]==0x3FFF and r[SP]==0x8000 and r[H]*256+r[L]==0x9A58 and r[D]*256+r[E]==20 and m[0x9A89:0x9A8B]==bytes([0x58,0x9A]) and m[0x9A82]==0
   assert m[0xB400:0xB404]==bytes([0,0x5F,1,1]);closed+=1
  assert m[0xCC17]==0xA7 and r[8:12]==initial[8:12]
 # Проверка каждого запрещающего селектора и всех входных F без выполнения вложенных обработчиков.
 for selector in range(128,256):
  for flags in range(256):execute(selector,flags)
 # Проверка всех кодов события, двух строк и полного либо уже отсутствующего набора десяти соседних панелей.
 for selector in (0,2,127):
  for event in range(256):
   for y in (12,50):
    for full in (False,True):execute(selector,0x5D,event,y,full)
 # Проверка всех допускаемых селекторов, единственный код 1 передаётся ветви выбора.
 for selector in range(128):execute(selector,0xA5,0x80,50,True)
 report=dict(passed=True,early_bit7_cases=early,close_panel_cases=closed,pan_dispatch_cases=pan,select_dispatch_cases=select,all_input_flag_bytes_on_bit7=True,all_event_code_bytes=True,real_list_move_and_removals=True,ten_control_indices_checked=True,full_repaint_in_this_model=False,selection_and_repaint_integration='MapSelectionPanelVerification.json',pan_integration='MapPanVerification.json',method='original_dispatcher_and_helpers_until_separately_proved_pan_or_selection_entry',irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapPanelEventVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

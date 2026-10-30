"""Полный C38C с настоящим фильтром, SumSquares8 и чтением варианта, пробуждение HALT явно задано."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckVisibleMapPoints import reference
from CheckMapDistanceMinimum import distance
from CheckGlyphRenderer import compare_flags
from CheckStationSpans import subtract_flags


def main():
 _,source,_=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1010,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);rng=random.Random(0xC38C);cases=early=stale=hits=0
 def check(ox,oy,width,height,pixel_origin,pointer_xy,tables,matched,old_choice=0xF60A):
  nonlocal cases,early,stale,hits
  raw=bytes([0xA7])*512;output,cursor,count,_=reference(tables,ox,oy,width,height,raw)
  px,py=pointer_xy&255,pointer_xy>>8;origin_x,origin_y=pixel_origin&255,pixel_origin>>8
  bx=(px-origin_x)&255;by=(py-origin_y)&255
  outside=py<origin_y or by>((height-1)&255) or px<origin_x or bx>((width-1)&255)
  best=65535;choice=old_choice
  if not outside:
   # Независимый поиск только до нулевого старшего байта параллельной ссылки, включая пустой список.
   for offset in range(0,256,2):
    if output[257+offset]==0:break
    q,_,_=distance((output[offset]-bx)&255,(output[offset+1]-by)&255)
    if q<best:best=q;choice=0xF600+offset
  def get(address):return output[address-0xF600] if 0xF600<=address<0xF800 else memory[address]
  memory[0x6300:0x6306]=bytes([ox,oy,4,3,width,height]);memory[0x6307:0x6309]=pointer_xy.to_bytes(2,'little')
  memory[0xF200:0xF600]=tables;memory[0xF600:0xF800]=raw;memory[0xC3E8:0xC3EA]=old_choice.to_bytes(2,'little')
  memory[0x9844:0x9849]=bytes([0x5A,0x5B,0x5C,0x5D,0xA7])
  if not outside:
   # Чтение выбранной ссылки точно по страницам, даже если она осталась от прежнего вызова.
   link=(choice+256)&65535;source_pointer=get(link)|(get((link&0xFF00)|((link+1)&255))<<8)
   second=get(source_pointer)|(get((source_pointer&0xFF00)|((source_pointer+1)&255))<<8)
   high=source_pointer>>8;first=(3+int(high not in (0xF2,0xF3)))*256+((4+int(high not in (0xF2,0xF4)))&255)
   memory[0x990A:0x9910]=first.to_bytes(2,'little')+second.to_bytes(2,'little')+bytes([0x5B,0x80]) if matched else bytes([0x80])*6
  # Выполнение оригинального вызова фильтра до HALT и явное пробуждение без ISR.
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=pixel_origin>>8,pixel_origin&255
  sim.run(start=0xC38C,stop=0xC4E5);r[PC]=0xC4E6;sim.run(stop=0x3FFF)
  assert memory[0xF600:0xF800]==output and memory[0xF200:0xF600]==tables
  assert memory[0xC3D0:0xC3D2]==best.to_bytes(2,'little') and memory[0xC3E8:0xC3EA]==choice.to_bytes(2,'little')
  assert r[SP]==0x8000 and r[10:12]==initial[10:12] and r[14]==initial[14]
  if outside:
   if py<origin_y:expected=(by,subtract_flags(py,origin_y),by,px)
   elif by>((height-1)&255):expected=((height-1)&255,compare_flags((height-1)&255,by),by,px)
   elif px<origin_x:expected=(bx,subtract_flags(px,origin_x),by,bx)
   else:expected=((width-1)&255,compare_flags((width-1)&255,bx),by,bx)
   assert (r[A],r[F],r[B],r[C])==expected and r[H]*256+r[L]==pixel_origin
   assert memory[0x9844:0x9849]==bytes([0x5A,0x5B,0x5C,0x5D,0xA7]);early+=1
  else:
   assert memory[0x9844:0x9848]==first.to_bytes(2,'little')+second.to_bytes(2,'little')
   variant=0x5B if matched else 0;expected_hl=0 if matched else (source_pointer&0xFF00)|((source_pointer+1)&255)
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[8]*256+r[9])==(expected_hl,first if matched else second,5,variant,0x42 if matched else 0x44,0x990A)
   assert memory[0x9848]==variant;stale+=best==65535;hits+=matched
  cases+=1
 accepted_points=((201,201),(1,201),(201,1),(1,1))
 # Проверка каждого принятого количества, в том числе кратных 128, с найденным и отсутствующим сохранённым вариантом.
 for n in range(513):
  tables=bytes(v for i in range(512) for v in (accepted_points[i//128] if i<n else (100,100)))
  for matched in (False,True):check(200,200,208,112,0x1010,0x2020,tables,matched)
 # Проверка каждой позиции лучшего кандидата в непереполненном списке из 127 записей.
 for best_index in range(127):
  points=[(216,216) if i==best_index else (201,201) if i<127 else (100,100) for i in range(512)]
  check(200,200,208,112,0x1010,0x2020,bytes(v for point in points for v in point),bool(best_index&1))
 # Проверка всех размеров и четырёх ветвей раннего отказа, а также обычной внутренней позиции.
 for size in range(256):
  for pointer in (0x0F20,0xFF20,0x200F,0x20FF,0x2020):
   check(200,200,size,(size*37)&255,0x1010,pointer,bytes(rng.randrange(256) for _ in range(1024)),False)
 report=dict(passed=True,cases=cases,early_outside_cases=early,stale_selection_cases=stale,stored_variant_hits=hits,
  method='original_C38C_visible_filter_SumSquares8_and_ReadStoredMapVariant_independent_list_search_and_key_reconstruction',
  accepted_counts_zero_through_512=True,all_dimension_bytes=True,empty_list_uses_old_choice=True,
  halt_wakeup_fixture=True,tables_and_stored_record_fixture=True,ROM_fixture_is_zero_filled=True,
  all_alternate_AF_values_proved=False,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/NearestVisiblePointVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

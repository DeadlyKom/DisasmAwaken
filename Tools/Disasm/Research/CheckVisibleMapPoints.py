"""Четыре страницы по 128 слов, фильтр видимости и циклические выходные страницы F6/F7."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context


def visible_points(tables,origin_x,origin_y,width,height):
 for index in range(512):
  quadrant=index//128;x,y=tables[2*index:2*index+2]
  reverse_x=bool(quadrant&1);reverse_y=bool(quadrant&2)
  dx=(origin_x-x) if reverse_x else (x-origin_x);dy=(origin_y-y) if reverse_y else (y-origin_y)
  valid_x=dx>=0 and (dx>=((1-width)&255) if reverse_x else dx<width)
  valid_y=dy>=0 and (dy>=((1-height)&255) if reverse_y else dy<height)
  if valid_x and valid_y:yield index,(-dx if reverse_x else dx)&255,(-dy if reverse_y else dy)&255


def reference(tables,origin_x,origin_y,width,height,output):
 result=bytearray(output);cursor=accepted=0;last=None
 for index,x,y in visible_points(tables,origin_x,origin_y,width,height):
  result[cursor]=x;result[(cursor+1)&255]=y
  pointer=0xF200+2*index;result[256+cursor]=pointer&255;result[256+((cursor+1)&255)]=pointer>>8
  cursor=(cursor+2)&255;accepted+=1;last=pointer
 result[256+((cursor+1)&255)]=0
 return result,cursor,accepted,last


def main():
 _,source,_=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);rng=random.Random(0xC4E5);cases=overflow=empty=0
 def check(ox,oy,width,height,tables):
  nonlocal cases,overflow,empty
  raw=bytes(rng.randrange(256) for _ in range(512));expected,cursor,count,last=reference(tables,ox,oy,width,height,raw)
  # Подготовка четырёх таблиц и отличимого прежнего содержимого двух выходных страниц.
  memory[0x6300:0x6302]=bytes([ox,oy]);memory[0x6304:0x6306]=bytes([width,height]);memory[0xF200:0xF600]=tables
  memory[0xF600:0xF800]=raw;memory[0xF800]=0xA7;sim.registers[:]=initial;r=sim.registers
  # HALT обходится только как явно заданное пробуждение, ISR и аппаратные прерывания не моделируются.
  assert memory[0xC4E5]==0x76;sim.run(start=0xC4E6,stop=0x3FFF)
  assert memory[0xF600:0xF800]==expected and memory[0xF200:0xF600]==tables and memory[0xF800]==0xA7,(ox,oy,width,height,count)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[F],r[SP])==(0xF700+cursor+1,last if last is not None else 0x247A,0x36C9,((cursor+1)&0xA8)|1,0x8000)
  assert r[18:24]==[0,(1-height)&255,oy,ox,tables[-1],tables[-2]]
  assert r[8:12]==initial[8:12] and r[14]==initial[14]
  writes={0xC511:height,0xC52B:width,0xC55C:(1-width)&255,0xC579:(1-height)&255,0xC590:width,0xC5CA:(1-width)&255}
  assert all(memory[a]==v for a,v in writes.items()) and memory[0xC5B6:0xC5B8]==bytes([254,127])
  cases+=1;overflow+=count>=128;empty+=count%128==0
 # Проверка каждого числа принятых точек, включая оборачивание и стирание высокого байта первой ссылки.
 accepted_points=((201,201),(1,201),(201,1),(1,1))
 for n in range(513):
  points=[accepted_points[i//128] if i<n else (100,100) for i in range(512)]
  check(200,200,208,112,bytes(v for point in points for v in point))
 # Проверка всех размеров, крайних начал окна и независимого фильтра случайных исходных координат.
 for size in range(256):
  for ox,oy in ((0,0),(1,255),(127,128),(200,200),(255,255)):
   check(ox,oy,size,(size*37)&255,bytes(rng.randrange(256) for _ in range(1024)))
 report=dict(passed=True,cases=cases,output_wrapped_cases=overflow,zero_sentinel_at_first_record_cases=empty,
  method='original_C4E6_after_explicit_HALT_wakeup_four_128_word_tables_independent_filter_full_output_and_exact_pointer_registers',
  accepted_counts_zero_through_512_checked=True,all_width_and_height_bytes=True,output_cursor_wrap_not_fixed=True,
  halt_wakeup_fixture=True,interrupt_handler_executed=False,all_AF_values_proved=False,
  tables_synthetic=True,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/VisibleMapPointsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

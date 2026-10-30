"""Классификатор после настоящего D0C3, все байтовые пороги и заголовки, включая оборачивание."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckMapPointOutcodes import reference
from CheckWorldSignature import logical_flags
from CheckGlyphRenderer import compare_flags


def main():
 _,source,banks=make_context();memory=bytearray(65536)
 memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0xB000,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial
 sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 rng=random.Random(0xD0C3D430);cases=zero=0

 def check(header,raw,stop_x,stop_y):
  nonlocal cases,zero
  count=header&15;expected,aggregate,last=reference(raw,count,stop_x,stop_y)
  memory[0xF7FF:0xF901]=bytes([0x5A])*258;memory[0xF800:0xF900]=raw;memory[0xB000]=header
  sim.registers[:]=initial;r=sim.registers;sim.run(start=0xD430,stop=0x3FFF)
  assert memory[0xF800:0xF900]==expected and memory[0xF7FF]==memory[0xF900]==0x5A and memory[0xB000]==header
  size=5*count
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0xF800+((size+1)&255),0x247A,size,last,aggregate,logical_flags(aggregate),0x8000)
  assert r[16:18]==[size,compare_flags(size,size)] and r[18:24]==initial[18:24] and r[8:12]==initial[8:12]
  cases+=1;zero+=count==0

 for stop_x in range(256):
  stop_y=255-stop_x
  # Настройка обеих границ оригинальным кодом, минимумы специально ненулевые и не упорядоченные.
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=(stop_y-1)&255,(stop_x-1)&255;r[D],r[E]=(stop_x*37)&255,(stop_x*53)&255
  sim.run(start=0xD0C3,stop=0x3FFF)
  assert (memory[0xD44D],memory[0xD468])==(stop_x,stop_y)
  # Проверка каждого младшего байта при каждом пороге и обеих знаковых ветвей старшего байта.
  for value in (*range(256),256,511,32767,32768,32769,65280,65534,65535):
   for x,y in ((value,(stop_y-1)&255),((stop_x-1)&255,value)):
    check(1,x.to_bytes(2,'little')+y.to_bytes(2,'little')+bytes([0xA7])+bytes(251),stop_x,stop_y)
  # Проверка каждого заголовка, включая циклическое чтение изменённых данных при нулевом количестве.
  for header in range(256):check(header,bytes(rng.randrange(256) for _ in range(256)),stop_x,stop_y)
  if stop_x==240:
   # Проверка каждого 16-битного слова обеих осей в одном реально настроенном профиле.
   for value in range(65536):
    for x,y in ((value,0),(0,value)):
     check(1,x.to_bytes(2,'little')+y.to_bytes(2,'little')+bytes([0xA7])+bytes(251),stop_x,stop_y)
 report=dict(passed=True,cases=cases,setup_profiles=256,all_byte_thresholds_each_axis=True,all_coordinate_words_each_axis_in_profile=[240,15],
  all_headers_per_profile=True,zero_count_cases=zero,nonzero_minima_do_not_move_lower_classifier_boundary=True,
  maximum_255_wraps_excluded_threshold_to_zero=True,method='original_D0C3_then_original_D430_exact_memory_registers_flags',
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ConfiguredMapOutcodesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

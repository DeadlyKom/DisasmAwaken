"""Исходные четыре признака выхода точки за прямоугольник 0..254 и их дополнения."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckWorldSignature import logical_flags
from CheckGlyphRenderer import compare_flags


def code(x,y,stop_x=255,stop_y=255):
 def axis(value,stop):return 2 if value&32768 else 1 if value>=stop else 0
 return axis(x,stop_x)|(axis(y,stop_y)<<2)


def reference(raw,count,stop_x=255,stop_y=255):
 work=bytearray(raw);aggregate=last=0
 for index in range(count if count else 256):
  offset=(5*index)&255
  x=work[offset]|(work[(offset+1)&255]<<8);y=work[(offset+2)&255]|(work[(offset+3)&255]<<8)
  last=code(x,y,stop_x,stop_y);packed=last|((last^15)<<4);work[(offset+4)&255]=packed;aggregate|=packed
 return work,aggregate,last


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0xB000,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 rng=random.Random(0xD430);cases=zero=0;bounds=(0,254,255,256,32768,65535)
 fixtures=[]
 # Проверка всех слов каждой координаты при граничных значениях другой оси.
 for value in range(65536):
  other=bounds[value%len(bounds)]
  fixtures.extend(((1,value,other,None),(1,other,value,None)))
 # Проверка всех заголовков, количества 0..15 и влияния нулевого количества на тот же рабочий массив.
 for header in range(256):fixtures.append((header,0,0,bytes(rng.randrange(256) for _ in range(256))))
 for header,x,y,raw in fixtures:
  if raw is None:raw=x.to_bytes(2,'little')+y.to_bytes(2,'little')+bytes([0xA7])+bytes(251)
  count=header&15;expected,aggregate,last=reference(raw,count)
  memory[0xF7FF:0xF901]=bytes([0x5A])*258;memory[0xF800:0xF900]=raw;memory[0xB000]=header;memory[0x7FFE:0x8000]=bytes([255,63])
  sim.registers[:]=initial;r=sim.registers;sim.run(start=0xD430,stop=0x3FFF)
  assert memory[0xF800:0xF900]==expected and memory[0xF7FF]==memory[0xF900]==0x5A and memory[0xB000]==header
  size=5*count
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0xF800+((size+1)&255),0x247A,size,last,aggregate,logical_flags(aggregate),0x8000)
  assert r[16:18]==[size,compare_flags(size,size)] and r[18:24]==initial[18:24] and r[8:12]==initial[8:12]
  cases+=1;zero+=count==0
 report=dict(passed=True,cases=cases,zero_count_cases=zero,
  method='original_map_point_outcodes_all_coordinate_words_and_all_header_bytes',
  accepted_coordinate_range='0..254',negative_axis_bit_left_or_top=True,
  upper_nibble_is_complement_of_lower=True,zero_count_processes_256_wrapped_records=True,
  zero_count_reads_its_previous_output=True,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapPointOutcodesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

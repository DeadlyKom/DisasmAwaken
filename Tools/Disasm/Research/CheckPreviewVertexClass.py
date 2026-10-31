"""Все координатные слова, ранние маркеры, пороги и модульный обход исходного DF46."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckWorldSignature import logical_flags
from PreviewVertexClassOracle import classify


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;outcomes=collections.Counter();codes=set();wrap_cases=0
 def check(buffer,next_offset,limit_first,limit_second):
  nonlocal cases,wrap_cases
  expected=classify(buffer,next_offset,limit_first,limit_second);m.recording=False;m[0xC600:0xC700]=buffer;m[0xD90D]=next_offset;m[0xDF7F]=limit_first;m[0xDF64]=limit_second;s.registers[:]=initial;m.recording=True;m.writes=[];s.run(start=0xDF46,stop=0x3FFF);r=s.registers
  assert bytes(m[0xC600:0xC700])==expected['buffer'],(next_offset,limit_first,limit_second,expected)
  answer=expected['accumulator'];flags=logical_flags(answer)
  assert (r[A],r[F],r[H]*256+r[L],r[B],r[C],r[D],r[E],r[SP])==(answer,flags,0x1357,expected['length'],expected['mask'],0x24,0x7A,0x8000)
  assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
  alt=(expected['length'],0x42|(expected['length']&0x28)) if expected['accepted'] else (expected['previous_accumulator'],logical_flags(expected['previous_accumulator']))
  assert tuple(r[16:18])==alt,(next_offset,r[16:18],expected)
  assert set(m.writes[:2])=={(0x7FFD,0x13),(0x7FFC,0x57)} and m.writes[2:]==[(0xC600+offset,value) for offset,value in expected['written']],m.writes[:8]
  cases+=1;outcomes['completed' if expected['accepted'] else 'marker_80']+=1;codes.update(value for offset,value in expected['written']);wrap_cases+=next_offset==4
 # Проверка каждого 16-битного слова на каждой оси при исходно заданных порогах, включая точное 80 в старшем байте.
 for axis in (0,2):
  for value in range(65536):
   buffer=bytearray(256);buffer[axis]=value&255;buffer[axis+1]=value>>8;check(buffer,9,123,87)
 # Проверка каждого порога на всех байтовых координатах при нулевых старших байтах.
 for limit in range(256):
  for value in range(256):
   buffer=bytearray(256);buffer[:4]=bytes((value,0,value,0));check(buffer,9,limit,limit)
 # Проверка раннего отказа в каждой допустимой позиции без переписывания оставшейся части буфера.
 for count in (1,2,11,32,50):
  for failed in range(count):
   buffer=bytearray((i*37+failed)&255 for i in range(256))
   for index in range(count):buffer[5*index:5*index+4]=bytes((0,0,0,0))
   buffer[5*failed+1]=128;check(buffer,4+5*count,100,80)
 rng=random.Random(0xDF46)
 for _ in range(2048):check(bytes(rng.randrange(256) for i in range(256)),4+5*rng.randrange(1,51),rng.randrange(256),rng.randrange(256))
 # Проверка всех нештатных счётчиков и пустого входа, чтение и запись остаются в странице C6 с оборачиванием L.
 for next_offset in range(256):check(bytes(256),next_offset,123,87)
 report=dict(passed=True,cases=cases,outcomes=dict(outcomes),codes=sorted(codes),all_coordinate_words_on_both_axes=True,all_byte_thresholds_and_coordinates=True,all_modular_counters_checked=True,empty_offset_04_cases=wrap_cases,exact_main_alternate_and_index_registers=True,exact_partial_writes_and_cpu_stack=True,independent_coordinate_and_modular_buffer_model=True,irq_executed=False,native_execution=False,assembly_executed=False,face_dispatch_not_executed=True)
 (ROOT/'Tools/Disasm/Reports/PreviewVertexClassVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Исходное накопление кодов одной грани DDFD с точными Carry, счётчиком и индексами."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckWorldSignature import logical_flags


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x6000,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;outcomes=collections.Counter()
 def check(indices,codes,count):
  nonlocal cases
  total=0;visited=0;failed=False
  # Независимое накопление кодов по индексам, нуль завершает чтение до добавления в общий OR.
  for index in indices[:count or 256]:
   visited+=1;code=codes[(index+4)&255]
   if code==0:failed=True;break
   total|=code
  m.recording=False;m[0x6001:0x6101]=indices;m[0xC600:0xC700]=codes;s.registers[:]=initial;r=s.registers;r[B]=count;m.recording=True;m.writes=[];s.run(start=0xDDFD,stop=0x3FFF)
  answer=0 if failed else total;flags=0x45 if failed else logical_flags(total)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[8]*256+r[9],r[SP])==(0x6000,0x6001+visited,count,total,answer,flags,0x2400+count,0x8000)
  assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
  assert set(m.writes)=={(0x7FFC,0),(0x7FFD,0x60)} and len(m.writes)==2
  cases+=1;outcomes['zero_code' if failed else 'completed']+=1
 # Проверка всех индексных и кодовых байтов, включая оборачивание +4 в той же странице C6.
 for index in range(256):
  for code in range(256):
   codes=bytearray([0xF0]*256);codes[(index+4)&255]=code;check(bytes([index]*256),codes,1)
 # Проверка каждого счётчика и раннего нуля в каждой возможной позиции, B=0 означает 256.
 indices=bytes(range(256))
 for count in range(256):
  check(indices,bytes([0xF0]*256),count)
  for failed in range(count or 256):
   codes=bytearray([0xF0]*256);codes[(failed+4)&255]=0;check(indices,codes,count)
 rng=random.Random(0xDDFD)
 for _ in range(1024):check(bytes(rng.randrange(256) for i in range(256)),bytes(rng.randrange(256) for i in range(256)),rng.randrange(256))
 report=dict(passed=True,cases=cases,outcomes=dict(outcomes),all_index_and_code_bytes=True,all_counts_and_first_zero_positions=True,zero_count_reads_256=True,exact_registers_flags_and_two_stack_bytes=True,no_projection_buffer_writes=True,irq_executed=False,native_execution=False,assembly_executed=False,full_face_pass_not_executed=True)
 (ROOT/'Tools/Disasm/Reports/PreviewFaceCodesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Исходный определитель DFA6, реальные умножители и независимая модель с цепочкой Carry."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,D,E,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckWorldSignature import logical_flags
from PreviewFaceOrientationOracle import orientation


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x6000,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=extremes=0;strides=collections.Counter();signs=collections.Counter()
 def check(points,indices=(0,5,10),count=3,alt_carry=1):
  nonlocal cases,extremes
  buffer=bytearray((i*37+cases*11)&255 for i in range(256))
  # Подготовка записей с реальным оборачиванием младшего адреса, наложенные индексы не нормализуются.
  for offset,(first,second) in zip(indices,points):
   for index,value in enumerate((second&255,second>>8,first&255,first>>8)):buffer[(offset+index)&255]=value
  expected=orientation(buffer,indices,count,alt_carry);m.recording=False;m[0xC600:0xC700]=buffer;m[0x6000:0x6008]=[0xA5]*8
  stride=1 if count<5 else 2
  for index,value in enumerate(indices):m[0x6001+stride*index]=value
  s.registers[:]=initial;r=s.registers;r[A]=count;r[17]=(r[17]&254)|alt_carry;m.recording=True;m.writes=[];s.run(start=0xDFA6,stop=0x3FFF)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[8]*256+r[9],r[10]*256+r[11],r[SP])==(0x6000,expected['low'],0x36C9,*expected['af'],expected['ix'],0x5C3A,0x8000),(points,indices,count,alt_carry,r[:12],expected)
  first=expected['first_product'];assert tuple(r[16:24])==(*expected['alt_af'],first['bc']>>8,first['bc']&255,first['de']>>8,first['de']&255,first['hl']>>8,first['hl']&255),(points,indices,count,r[16:24],expected)
  second=expected['second_product'];saved_af=second['af'][0]*256+logical_flags(second['af'][0])
  # Проверка всех шести слов, остающихся под CPU-SP после вложенных вызовов и восстановления указателей.
  stack_words=[m[p]+256*m[p+1] for p in range(0x7FF2,0x7FFE,2)]
  assert stack_words==[saved_af,0xE006,first['de'],first['hl'],0x6000,0x36C9]
  assert {p for p,v in m.writes}==set(range(0x7FF2,0x7FFE)) and m[0x7FFE:0x8000]==[255,63]
  cases+=1;strides[stride]+=1;signs['negative' if r[F]&128 else 'nonnegative']+=1;extremes+=first['extreme_multiplier_lost']+second['extreme_multiplier_lost']
 # Проверка каждого слова в первой координате третьей вершины для обоих способов выбора индексов.
 for value in range(65536):
  for count in (3,5):check(((0,0),(256,256),(value,32768)),count=count)
 # Проверка крайних геометрий и обоих входных Carry альтернативного AF.
 values=(0,1,255,256,32767,32768,65535)
 for x in values:
  for y in values:
   for count in (0,3,4,5,15,255):
    for carry in (0,1):check(((32768,65535),(x,256),(y,32767)),count=count,alt_carry=carry)
 # Проверка каждого индексного байта и каждого входного A с наложениями и переходом через конец C6.
 for value in range(256):check(((1,2),(32768,65535),(255,256)),(value,(value+1)&255,(value+253)&255),value,value&1)
 rng=random.Random(0xDFA6)
 for _ in range(8192):check(tuple((rng.randrange(65536),rng.randrange(65536)) for i in range(3)),tuple(rng.randrange(256) for i in range(3)),rng.randrange(256),rng.randrange(2))
 report=dict(passed=True,cases=cases,index_strides=dict(strides),orientation_signs=dict(signs),extreme_multiplier_cases=extremes,all_coordinate_words_in_selected_geometries=True,all_index_bytes_and_input_a=True,original_chained_borrows_and_product_carry_preserved=True,independent_full_register_and_signed_product_model=True,real_two_word_multipliers=True,exact_twelve_stack_bytes_and_cpu_return=True,irq_executed=False,native_execution=False,assembly_executed=False,face_walk_not_executed=True)
 (ROOT/'Tools/Disasm/Reports/PreviewFaceOrientationVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

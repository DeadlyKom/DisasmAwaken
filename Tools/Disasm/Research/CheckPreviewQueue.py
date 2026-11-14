"""Двухключевая вставка EE24, физическая упаковка четырнадцатибайтовой записи и предел очереди."""
from pathlib import Path
import json,sys,random,collections,struct
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,PC,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from ReferenceControlsPointRespawn import refresh


def add_flags(a,b):
 total=a+b;value=total&255
 return (value&0xA8)|(0x40 if value==0 else 0)|(0x10 if (a&15)+(b&15)>15 else 0)|(4 if (~(a^b)&(a^value)&128) else 0)|int(total>255)


def queue_m1(records,newflags,position):
 n=len(records)
 # Расчёт стоимости независимого поиска по уже выбранной позиции, только первая ветвь ключа имеет лишний JP.
 if not n:search=7
 elif position==0:search=22
 else:search=22+int(not ((newflags|records[0][0])&128))+2+22*(position-1)+(4 if position==n else 17)
 if n==18:return search+3
 return search+(10 if position==0 else 9 if position==n else 11)+18


def main():
 m=Memory([0]*65536);raw=payload(6);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 outcomes=collections.Counter();cases=wrapped=0;m1_bounds={}
 def check(records,newflags,newkey1,newkey2,params=(0x53,0x64,0x75,0x86,0x9753,0xA864)):
  nonlocal cases,wrapped
  m.recording=False;n=len(records);free=14*n;original=bytearray((j*37+19)&255 for j in range(256))
  # Создание допустимой бесцикловой цепочки с физическими индексами, нулевой индекс является обычной записью.
  for i,(flags,key1,key2) in enumerate(records):
   offset=14*i;original[offset:offset+14]=struct.pack('<6B4H',14*(i+1) if i+1<n else 1,flags,7,8,9,10,11,12,key1,key2)
  m[0xC700:0xC800]=list(original);m[0xCF02]=0 if n else 1;m[0xCF03]=free
  def word(ptr,value):m[ptr]=value&255;m[ptr+1]=value>>8
  model,angle1,angle2,angle3,result1,result2=params
  word(0xDA16,newkey1);word(0xEB8D,newkey2);word(0xDAF6,result1);word(0xDA38,result2)
  m[0xCEFA]=newflags;m[0xCEFB]=model;m[0xC21E]=angle1;m[0xC21F]=angle2;m[0xC220]=angle3
  # Поиск позиции по паре ключей и знаку шестнадцатибитной разности, равенство пропускает существующую запись.
  position=n
  for index,(flags,key1,key2) in enumerate(records):
   second=bool((newflags|flags)&128);old=key2 if second else key1;new=newkey2 if second else newkey1
   difference=(old-new)&65535
   if bool(difference&32768)!=(old-new<0):wrapped+=1
   if difference&32768:position=index;break
  expected=bytearray(original);head=0 if n else 1
  if n<18:
   next_index=position*14 if position<n else 1
   if position==0:head=free
   else:expected[(position-1)*14]=free
   expected[free:free+14]=struct.pack('<6B4H',next_index,newflags,model,angle1,angle2,angle3,result1,result2,newkey1,newkey2)
  initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*73)&255,0,cases%3
  s.registers[:]=initial;r=s.registers;r[PC]=0xEE24;m.writes=[];m.recording=True;measured_m1=0
  for _ in range(1200):
   if r[PC] in (0xECAE,0xEEEE):break
   old_r=r[15];s.run();increment=(r[15]-old_r)&127
   assert increment in (1,2)
   measured_m1+=increment
  else:raise AssertionError('Не завершена вставка в очередь')
  assert bytes(m[0xC700:0xC800])==bytes(expected) and m[0xCF02]==head and r[D]*256+r[E]==newkey2 and r[2]*256+r[3]==newkey1
  assert r[16:24]==initial[16:24]
  cost=queue_m1(records,newflags,position)
  assert measured_m1==cost and r[15]==refresh(initial[15],cost),(n,position,newflags,measured_m1,cost)
  assert all(r[i]==initial[i] for i in (14,26,27))
  if n==18:
   assert r[PC]==0xEEEE and m[0xCF03]==252 and r[SP]==initial[SP] and (r[A],r[F])==(252,0x6A) and m.writes==[]
   assert r[H]*256+r[L]==difference,(records,position,'last_comparison_HL')
   outcomes['full_stop']+=1
  else:
   assert r[PC]==0xECAE and m[0xCF03]==free+14 and r[SP]==0xC700+free+1
   assert (r[A],r[F],r[H]*256+r[L])==(angle3,add_flags(free,14),model*256+newflags)
   allowed=set(range(0xC700+free,0xC700+free+14))|{0xCF03}
   if position==0:allowed.add(0xCF02)
   else:allowed.add(0xC700+(position-1)*14)
   assert all(ptr in allowed for ptr,value in m.writes)
   # PUSH AF временно пишет флаги в поле AngleSecond, последующий PUSH HL обязан их заменить.
   assert (0xC700+free+4,add_flags(free,14)) in m.writes and m[0xC700+free+4]==angle2
   # Проверка каждой записи нового узла, служебной ссылки и временного F, включая повтор поля AngleSecond.
   wanted_writes=[(0xC700+free+i,expected[free+i]) for i in range(14)]
   wanted_writes += [(0xC700+free+4,add_flags(free,14)),(0xCF03,free+14)]
   wanted_writes += [(0xCF02,free)] if position==0 else [(0xC700+(position-1)*14,free)]
   assert len(m.writes)==17 and collections.Counter(m.writes)==collections.Counter(wanted_writes)
   outcomes['head' if position==0 else 'tail' if position==n else 'middle']+=1
  if n==0:expected_ix=0x2468;expected_iy=0x5C3A
  elif position==0:expected_ix=0xC700;expected_iy=0x5C3A
  else:
   expected_ix=0xC700+14*(position-1)
   expected_iy=0xC700+(14*position if position<n else 14*(n-1) if n>1 else 0x3A)
  assert r[8]*256+r[9]==expected_ix and r[10]*256+r[11]==expected_iy,(records,position,r[8:12],hex(expected_ix),hex(expected_iy))
  kind='full_stop' if n==18 else 'head' if position==0 else 'tail' if position==n else 'middle'
  lo,hi=m1_bounds.get(kind,(cost,cost));m1_bounds[kind]=(min(lo,cost),max(hi,cost))
  cases+=1
 # Проверка всех пар флаговых байтов для несовпадающих, равных и переполненных разностей ключей.
 key_sets=((10,20,30,5),(20,10,5,30),(32768,1,32767,32768),(1,1,0,0))
 for newflags in range(256):
  for oldflags in range(256):
   for old1,new1,old2,new2 in key_sets:check([(oldflags,old1,old2)],newflags,new1,new2)
 # Проверка всех допустимых размеров цепочки, включая пустую и полную, на воспроизводимой выборке.
 rng=random.Random(0xEE24)
 for count in range(19):
  for _ in range(256):
   records=[(rng.randrange(256),rng.randrange(65536),rng.randrange(65536)) for j in range(count)]
   check(records,rng.randrange(256),rng.randrange(65536),rng.randrange(65536),tuple(rng.randrange(256) for j in range(4))+tuple(rng.randrange(65536) for j in range(2)))
 # Проверка каждой позиции каждой длины при двух селекторах ключа, включая предельный хвост полного пула.
 for count in range(19):
  for position in range(count+1):
   for flags in (0,128):
    records=[(flags,100 if index<position else 0,100 if index<position else 0) for index in range(count)]
    check(records,flags,50,50)
 report=dict(passed=True,cases=cases,outcomes=dict(outcomes),all_flag_byte_pairs=True,all_valid_queue_sizes=True,all_positions_for_each_size_and_key_selector_checked=True,targeted_position_cases=380,wrapped_sign_comparisons=wrapped,independent_list_insertion_and_binary_record_pack=True,full_queue_does_not_write=True,transient_flags_push_checked=True,sp_at_node_plus_one=True,register_and_write_boundaries_checked=True,child_rendering_not_executed=True,direct_full_M1_and_R_checked=True,I_IM_IFF_preserved_checked=True,exact_write_values_and_multiplicity_checked=True,successful_insert_byte_writes=17,full_queue_last_comparison_HL_checked=True,observed_M1_bounds=m1_bounds,complete_joint_input_product_exhausted=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewQueueVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

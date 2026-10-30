"""Оригинальная сумма с выбранной строкой, двумя таблицами весов и необязательным полем."""
from pathlib import Path
import sys,json,random
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckMatrixKey import add_flags


def reference(mem,index):
 total=0;target=(0x9852+2*index)&65535
 for i in range(30):
  address=0x9852+2*i;q=(mem[address]&127)+int(address==target);unit=mem[0x94FA+i]
  if (unit-1)&128:value=q
  elif unit==1:value=q>>4
  else:value=0
  total=(total+value)&255
 for table,values,count in ((0x95F1,0x988E,30),(0x9633,0x98F6,14)):
  for i in range(count):
   raw=mem[values+i];weight=raw if raw<128 else raw^255
   total=(total+weight*mem[table+2*i])&255
 option=mem[0x984A]
 if option==255:extra=0;hl=0x964F;de=0x9904
 else:
  shift=((option<<2)|(option>>6))&255;offset=(shift+option)&255
  hl=0x9829+offset;de=offset;extra=mem[hl]
 return (total+extra)&255,add_flags(extra,total),total,hl,de


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 memory=original.copy();simulator=Simulator(memory);rng=random.Random(0xC86F)
 initial=get_registers({'SP':0x7FFE,'DE':0x247A,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0
 # Проверка всех байтов категорий и необязательного индекса, включая старшие биты вращения.
 for case in range(512):
  memory[:]=original
  for address in list(range(0x94FA,0x9518))+list(range(0x95F1,0x9650))+list(range(0x9829,0x9904)):
   memory[address]=rng.randrange(256)
  for i in range(30):memory[0x94FA+i]=case&255
  # Создание ограниченных множителей для быстрого охвата всех категорий и знаковых весов.
  for base,count in ((0x95F1,30),(0x9633,14)):
   for i in range(count):memory[base+2*i]=(case+i)%4
  if case%32==0:
   for base,count in ((0x95F1,30),(0x9633,14)):
    for i in range(count):memory[base+2*i]=255
  memory[0x984A]=case&255;index=(case%33) if case<256 else (case*193)&65535
  expected=reference(memory,index);simulator.registers[:]=initial;r=simulator.registers;r[H],r[L]=index>>8,index&255
  memory[0x7FFE:0x8000]=bytes([255,63]);simulator.run(start=0xC86F,stop=0x3FFF)
  value,flags,total,hl,de=expected
  assert (r[A],r[F],r[C],r[H]*256+r[L],r[D]*256+r[E])==(value,flags,total,hl,de),(case,expected,list(r))
  assert r[B]==0 and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
  assert memory[0xC884]+256*memory[0xC885]==(0x9852+2*index)&65535
  for operand,source in ((0xC8BF,0x98AB),(0xC8E1,0x9903)):
   byte=memory[source];assert memory[operand]==(byte if byte<128 else byte^255)
  cases+=1
 report=dict(passed=True,method='original_three_table_weighted_sum_with_selected_row_and_rotated_option',cases=cases,
  all_category_bytes=True,all_option_bytes=True,weights_use_complement_not_absolute_value=True,
  native_execution=False,irq_executed=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/WeightedLoadVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

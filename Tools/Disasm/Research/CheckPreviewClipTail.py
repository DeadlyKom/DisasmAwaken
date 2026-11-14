"""Запись точки, два слова разности и четыре угла D3D с точными флагами и оборачиванием C8.

Документация: ../../../Docs/PreviewClipTail.md#r-и-неперекрытие-рамки-возврата
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckSignedMultiply import sbc16_flags
from PreviewEdgeRasterOracle import column_context,logical
from collections import Counter


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts=dict(differences=0,append=0,second=0,corners=0,configured_corners=0)
 entries=Counter();refresh_seeds={}
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 codes=[i for region in flow if region['name']=='D3D' for i in region['instructions']
        if 0xE7B4<=i['address']<0xE7E0 or 0xE830<=i['address']<0xE85D]
 for row in codes:
  code=bytes.fromhex(row['hex']);address=row['address']
  assert bytes(m[address:address+len(code)])==code==raw[address-0xC000:address-0xC000+len(code)]
 def run(entry,point=None,carry=0,accumulator=0x5A):
  s.registers[:]=initial;r=s.registers;r[0]=accumulator;r[1]=(r[1]&254)|carry
  if point is not None:r[4]=point>>8;r[5]=point&255
  serial=entries[entry];entries[entry]+=1
  r[14]=serial&255;r[15]=(serial*73)&255;r[26]=serial&1;r[27]=serial%3
  refresh_seeds.setdefault(entry,set()).add(r[15]);initial_r=r[15];system=(r[14],r[26],r[27])
  # Расчёт полного M1 короткого входа, отказ угла не вызывает общий писатель.
  if entry in (0xE830,0xE83B):m1=7
  elif entry==0xE84E:m1=10
  elif entry==0xE846:m1=14
  else:
   assert entry in (0xE7B4,0xE7BF,0xE7CA,0xE7D5)
   m1=3 if m[0xC250] else 15
  m.recording=True;m.writes=[];s.run(start=entry,stop=0x3FFF)
  assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[12]==0x8000 and r[16:24]==initial[16:24]
  assert r[15]==(initial_r&128)|((initial_r+m1)&127)
  assert (r[14],r[26],r[27])==system
  return r
 def appended(r,point,size,carry):
  end=(size+2)&255
  assert (r[0],r[1],r[4]*256+r[5],r[6]*256+r[7])==(end,column_context(end,1,carry),point,0xC800+end)
  assert m.writes==[(0xC800+size,point&255),(0xC800+((size+1)&255),point>>8),(0xC22B,end)]
 # Проверка всех значений первого слова на пяти крайних значениях второго, для каждой оси.
 for first in range(65536):
  for second in (0,1,32767,32768,65535):
   for entry,offset in ((0xE830,0),(0xE83B,2)):
    m.recording=False;m[0xC22C+offset:0xC22E+offset]=[first&255,first>>8];m[0xC23C+offset:0xC23E+offset]=[second&255,second>>8]
    r=run(entry,carry=first&1,accumulator=first&255);result=(second-first)&65535
    assert (r[0],r[1],r[4]*256+r[5],r[6]*256+r[7])==(first&255,sbc16_flags(second,first,0),first,result) and not m.writes
    counts['differences']+=1
 # Проверка каждой упакованной точки на границах оборачивания и обоих входных Carry.
 for point in range(65536):
  for size in (0,1,254,255):
   for carry in (0,1):
    m.recording=False;m[0xC22B]=size;r=run(0xE84E,point,carry);appended(r,point,size,carry);counts['append']+=1
    first=point;second=(point*73+19)&65535;m.recording=False;m[0xC23C:0xC240]=[first&255,first>>8,second&255,second>>8];m[0xC22B]=size
    r=run(0xE846,carry=carry);appended(r,((second&255)<<8)|(first&255),size,carry);counts['second']+=1
 # Проверка всех значений курсора, включая нечётные, на обоих Carry.
 for size in range(256):
  for point in (0,1,0x7FFF,0x8000,0xFFFF):
   for carry in (0,1):
    m.recording=False;m[0xC22B]=size;r=run(0xE84E,point,carry);appended(r,point,size,carry);counts['append']+=1
 corners=((0xE7B4,0xE7BA),(0xE7BF,0xE7C5),(0xE7CA,0xE7D0),(0xE7D5,0xE7DB))
 # Проверка целого BlockCode и байтового размера на всех четырёх исходных углах.
 for entry,operand in corners:
  point=m[operand]+256*m[operand+1]
  for block in range(256):
   for size in range(256):
    m.recording=False;m[0xC250]=block;m[0xC22B]=size;r=run(entry,carry=1)
    if block:
     assert tuple(r[:8])==(block,logical(block)|16,*initial[2:8]) and not m.writes
    else:appended(r,point,size,0)
    counts['corners']+=1
 # Настройка всех байтов четырёх пределов настоящим E011, порядок границ специально не нормализуется.
 for index in range(256):
  m.recording=False;s.registers[:]=initial;r=s.registers;r[6]=index;r[7]=(index*73+19)&255;r[4]=index^255;r[5]=(index*37+11)&255;s.run(start=0xE011,stop=0x3FFF)
  expected=((r[4]<<8)|r[7],(r[4]<<8)|r[5],(r[6]<<8)|r[7],(r[6]<<8)|r[5])
  # E011 меняет младшие L и E местами, поэтому ожидаемые углы берутся из его доказанного выхода.
  for (entry,operand),point in zip(corners,expected):
   for size in (0,1,254,255):
    m.recording=False;m[0xC250]=0;m[0xC22B]=size;r=run(entry,carry=1);appended(r,point,size,0);counts['configured_corners']+=1
 alias_probes=[]
 # Проверка изменения внешнего возврата выходной точкой либо самим ByteCount.
 for stack,size,target in ((0xC8FE,254,0x1234),(0xC8FF,254,0x3F12),(0xC22B,255,0x3F01)):
  probe=Memory(list(m));probe.recording=False;probe[0xC22B]=size;probe[stack:stack+2]=[255,63]
  cpu=Simulator(probe);cpu.registers[:]=initial;r=cpu.registers;r[4:6]=[0x12,0x34];r[12]=stack;r[24]=0xE84E;r[15]=0xFE
  probe.recording=True;probe.writes=[]
  for _ in range(10):cpu.run()
  assert r[24]==target and r[12]==(stack+2)&65535 and r[15]==0x88
  assert probe.writes==[(0xC800+size,0x34),(0xC800+((size+1)&255),0x12),(0xC22B,(size+2)&255)]
  alias_probes.append(dict(input_SP=stack,input_cursor=size,initial_return=0x3FFF,
   actual_return=target,final_SP=r[12],point=0x1234,bounded_instructions=10,target_executed=False))
 report=dict(passed=True,counts=counts,exact_main_alternate_and_index_context=True,append_wraps_only_inside_c8=True,ordered_point_and_counter_writes_checked=True,input_carry_preserved_by_append=True,corner_and_clears_input_carry=True,all_block_bytes_checked=True,real_configurer_all_256_component_values=True,original_immediates_not_replaced_in_source=True,irq_executed=False,native_execution=False,assembly_executed=False)
 assert all(seeds==set(range(256)) for seeds in refresh_seeds.values())
 report.update(R_m1_costs={'difference':7,'point':10,'second_then_point':14,'corner_rejected':3,'corner_appended':15},
  all_256_R_values_per_entry=True,R_bit7_and_I_IM_IFF_preserved=True,
  checked_original_code_bytes=sum(len(bytes.fromhex(row['hex'])) for row in codes),
  R_full_joint_input_product=False,configurer_R_cost_proved=False,return_frame_alias_probes=alias_probes)
 (ROOT/'Tools/Disasm/Reports/PreviewClipTailVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

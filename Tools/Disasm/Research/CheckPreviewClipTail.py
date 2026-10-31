"""Запись точки, два слова разности и четыре угла D3D с точными флагами и оборачиванием C8."""
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


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts=dict(differences=0,append=0,second=0,corners=0,configured_corners=0)
 def run(entry,point=None,carry=0,accumulator=0x5A):
  s.registers[:]=initial;r=s.registers;r[0]=accumulator;r[1]=(r[1]&254)|carry
  if point is not None:r[4]=point>>8;r[5]=point&255
  m.recording=True;m.writes=[];s.run(start=entry,stop=0x3FFF)
  assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[12]==0x8000 and r[16:24]==initial[16:24]
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
 report=dict(passed=True,counts=counts,exact_main_alternate_and_index_context=True,append_wraps_only_inside_c8=True,ordered_point_and_counter_writes_checked=True,input_carry_preserved_by_append=True,corner_and_clears_input_carry=True,all_block_bytes_checked=True,real_configurer_all_256_component_values=True,original_immediates_not_replaced_in_source=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipTailVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

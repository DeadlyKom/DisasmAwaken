"""Исходные адреса двух растровых краёв, маски и ограниченный поиск строки."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address
from CheckWorldSignature import logical_flags


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x96C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 points=reset=seek=0
 def run(entry):
  memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=entry,stop=0x3FFF)
  assert sim.registers[8:12]==initial[8:12] and sim.registers[16:24]==initial[16:24] and sim.registers[SP]==0x8000
 # Проверка всех байтовых координат обоих краёв, адреса сравниваются с независимым чтением таблиц.
 for y in range(256):
  for x in range(256):
   high=memory[0xEE00+y];low=(memory[0xEF00+y]+memory[0xF000+x])&255;address=high*256+low;mask=128>>(x&7)
   for entry in (0xE514,0xE52E):
    sim.registers[:]=initial;r=sim.registers;r[A]=x;r[C]=y;run(entry)
    if entry==0xE514:
     assert (r[H]*256+r[L],r[D],r[E],r[B],r[C],r[A],r[F])==(address,0x24,low,mask,x,0,0x43 if x&7==0 else 0x42)
    else:
     assert (r[H]*256+r[L],r[D],r[E],r[B],r[C],r[A],r[F])==(address,0x24,0x7A,0x96,mask,0x96,0x43 if x&7==7 else 0x42)
     assert memory[0xDFB8]==0x96
    points+=1
 # Проверка масок полного внутреннего пролёта для всех младших байтов левого адреса.
 for low in range(256):
  sim.registers[:]=initial;r=sim.registers;r[L]=low;run(0xE5D8);value=(low&224)|1
  assert (r[H],r[L],r[D],r[E],r[B],r[C],r[A],r[F])==(0x13,low,0x24,value,128,1,value,logical_flags(value));reset+=1
 upper=bitmap_address(16,0);lower=bitmap_address(144,0)
 memory[0xDFBA:0xDFBE]=upper.to_bytes(2,'little')+lower.to_bytes(2,'little')
 # Проверка всех счётчиков поиска и всех внутренних строк при обоих направлениях.
 fixtures=[(0,y,count) for y in range(128) for count in range(256)]
 fixtures += [(column,y,count) for column in (1,31) for y in (0,1,7,8,63,120,127) for count in range(256)]
 for column,y,count in fixtures:
  for entry,down,operand in ((0xE5E3,False,0xE5EE),(0xE621,True,0xE62C)):
   memory[operand]=column;sim.registers[:]=initial;r=sim.registers;r[A]=y;r[B]=count;run(entry)
   expected_y=min(128,y+count) if down else max(0,y-count)
   crossed=count>=8-(y&7) if down else count>(y&7)
   de=(lower if down else upper) if crossed else 0x247A
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F])==(bitmap_address(16+expected_y,column),de,count,y,y,0x5C),(entry,column,y,count)
   seek+=1
 report=dict(passed=True,edge_coordinate_cases=points,reset_mask_cases=reset,seek_cases=seek,
  method='original_raster_edge_addresses_masks_and_bounded_row_seek_all_counts_rows_and_coordinate_bytes',
  seek_restores_AF=True,seek_returns_C_equal_input_A=True,upper_inclusive_lower_exclusive=True,
  original_zero_OR_seek_cases=65536,synthetic_nonzero_OR_seek_cases=7168,
  game_writer_of_OR_operands_established=False,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/RasterPreparationVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

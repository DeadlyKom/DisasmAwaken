"""Поиск строк после D0C3 в окнах с целыми восьмистрочными блоками и допустимой колонкой."""
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
 _,source,banks=make_context();memory=bytearray(65536)
 memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x96C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0
 sim.run(start=0xC49B,stop=0x3FFF);reset_cases=seek_cases=0
 for max_x in range(248):
  height=128 if max_x==239 else (max_x%22+1)*8;upper=bitmap_address(16,0);lower=bitmap_address(16+height,0)
  # Настройка реальных колонок и границ без ручной записи в OR или MapState.UpperRow/LowerRow.
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=height-1,max_x;r[D]=r[E]=0
  sim.run(start=0xD0C3,stop=0x3FFF)
  column=(max_x+8)//8;left_column=1
  assert memory[0xDFBA:0xDFBE]==upper.to_bytes(2,'little')+lower.to_bytes(2,'little')
  # Проверка сброса пролёта при каждом младшем адресном байте после установки окна.
  for low in range(256):
   sim.registers[:]=initial;r=sim.registers;r[L]=low;sim.run(start=0xE5D8,stop=0x3FFF)
   value=(low&224)|left_column
   assert (r[H],r[L],r[D],r[E],r[B],r[C],r[A],r[F],r[SP])==(0x13,low,0x24,value,128,1,value,logical_flags(value),0x8000)
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];reset_cases+=1
  # Проверка каждого внутреннего Y, граничных счётчиков и полного диапазона B в одном окне.
  for y in range(height):
   for count in range(256) if max_x==239 else (0,1,7,8,127,128,255):
    for entry,down in ((0xE5E3,False),(0xE621,True)):
     sim.registers[:]=initial;r=sim.registers;r[A]=y;r[B]=count;sim.run(start=entry,stop=0x3FFF)
     expected_y=min(height,y+count) if down else max(0,y-count)
     crossed=count>=8-(y&7) if down else count>(y&7)
     de=(lower if down else upper) if crossed else 0x247A
     assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(bitmap_address(16+expected_y,column),de,count,y,y,0x5C,0x8000),(max_x,height,y,count,entry)
     assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];seek_cases+=1
 report=dict(passed=True,setup_profiles=248,reset_mask_cases=reset_cases,seek_cases=seek_cases,
  method='original_table_builder_DE_zero_then_D0C3_then_reset_and_both_seek_entries',
  height_range='8..176, multiple of 8',max_x_range='0..247',seek_column_range='1..31',
  all_counts_and_rows_in_profile=dict(max_x=239,height=128),all_internal_rows_each_profile=True,
  max_x_248_to_255_and_unaligned_boundaries_verified=False,game_writer_of_OR_operands_executed=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ConfiguredRasterSeekVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

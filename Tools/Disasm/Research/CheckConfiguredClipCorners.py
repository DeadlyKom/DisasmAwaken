"""Четыре угла после настоящей настройки D0C3, запрет записи и байтовый курсор."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckClipIntersections import inc_flags
from CheckWorldSignature import logical_flags


def main():
 _,source,banks=make_context();memory=bytearray(65536)
 memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0
 sim.run(start=0xC49B,stop=0x3FFF);cases=0
 for profile in range(256):
  min_x,min_y,max_x,max_y=profile,(profile*37)&255,255-profile,(profile*53)&255
  # Настройка четырёх углов настоящим кодом, без ручного исправления пары DE в процедурах.
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=max_y,max_x;r[D],r[E]=min_y,min_x
  sim.run(start=0xD0C3,stop=0x3FFF)
  for entry,pair in ((0xDAB0,(min_x,min_y)),(0xDABB,(max_x,min_y)),(0xDAC6,(min_x,max_y)),(0xDAD1,(max_x,max_y))):
   # Проверка всех запрещающих байтов, при разрешённой записи всех 256 положений курсора.
   for block in range(256):
    for cursor in range(256) if block==0 else (block,):
     memory[0xDE3A]=block;memory[0xDE3B]=cursor;memory[0xF8FF:0xFA01]=bytes([0xA7])*258
     sim.registers[:]=initial;r=sim.registers;sim.run(start=entry,stop=0x3FFF)
     expected=bytearray([0xA7]*256)
     if block:values=(block,logical_flags(block)|0x10,0x1357,0x247A)
     else:
      expected[cursor],expected[(cursor+1)&255]=pair;after=(cursor+2)&255
      values=(after,inc_flags((cursor+1)&255,0),0xF900+after,pair[1]*256+pair[0])
     assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E])==values
     assert memory[0xF900:0xFA00]==expected and memory[0xF8FF]==memory[0xFA00]==0xA7
     assert memory[0xDE3B]==(cursor if block else (cursor+2)&255) and r[SP]==0x8000
     for index in (*range(14),*range(16,24)):
      if index not in (A,F,H,L,D,E,SP):assert r[index]==initial[index]
     cases+=1
 report=dict(passed=True,cases=cases,setup_profiles=256,each_boundary_all_byte_values=True,all_corner_block_bytes=True,
  all_output_cursors_when_allowed=True,unordered_bounds_preserved=True,
  method='original_D0C3_then_four_original_corner_entries_actual_common_writer_exact_output_registers_flags',
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ConfiguredClipCornersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

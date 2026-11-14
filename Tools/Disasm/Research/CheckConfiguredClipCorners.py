"""Четыре угла после настоящей настройки D0C3, запрет записи и байтовый курсор."""
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckClipIntersections import inc_flags
from CheckWorldSignature import logical_flags
from CheckPreviewCoordinateMultiply import Memory
from ReferenceControlsPointRespawn import refresh


def main():
 _,source,banks=make_context();memory=Memory([0]*65536)
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
     initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*73)&255,0,cases%3
     initial[F]=(cases*37)&255
     sim.registers[:]=initial;r=sim.registers;r[24]=entry;memory.writes=[];memory.recording=True;measured=0
     # Проверка полного короткого пути, включая общий писатель и RET.
     for _ in range(20):
      if r[24]==0x3FFF:break
      previous_r=r[15];sim.run();increment=(r[15]-previous_r)&127
      assert increment==1
      measured+=increment
     else:raise AssertionError('угол карты не вернулся')
     memory.recording=False
     cost=3 if block else 15
     assert measured==cost and r[15]==refresh(initial[15],cost)
     expected=bytearray([0xA7]*256)
     if block:values=(block,logical_flags(block)|0x10,0x1357,0x247A)
     else:
      expected[cursor],expected[(cursor+1)&255]=pair;after=(cursor+2)&255
      values=(after,inc_flags((cursor+1)&255,0),0xF900+after,pair[1]*256+pair[0])
     assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E])==values
     assert bytes(memory[0xF900:0xFA00])==expected and memory[0xF8FF]==memory[0xFA00]==0xA7
     assert memory[0xDE3B]==(cursor if block else (cursor+2)&255) and r[SP]==0x8000
     # Проверка значений и кратности каждой записи, запрещённый угол не пишет даже размер.
     writes=[] if block else [(0xF900+cursor,pair[0]),(0xF900+((cursor+1)&255),pair[1]),(0xDE3B,(cursor+2)&255)]
     assert collections.Counter(memory.writes)==collections.Counter(writes)
     for index in (*range(15),*range(16,24),26,27):
      if index not in (A,F,H,L,D,E,SP):assert r[index]==initial[index]
     cases+=1
 report=dict(passed=True,cases=cases,setup_profiles=256,each_boundary_all_byte_values=True,all_corner_block_bytes=True,
  all_output_cursors_when_allowed=True,direct_full_M1_and_R_checked=True,
  exact_write_values_and_multiplicity=True,I_IM_IFF_preservation_checked=True,
  complete_joint_boundary_product_exhausted=False,unordered_bounds_preserved=True,
  method='original_D0C3_then_four_original_corner_entries_actual_common_writer_exact_output_registers_flags',
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ConfiguredClipCornersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Два исходных поиска пятибайтовых записей карты с FF-пустотами и отрицательным концом."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckMapViewCenter import reference as center_reference


def main():
 _,map_source,banks=make_context();memory=bytearray(65536)
 memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(map_source)]=map_source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;hits=ends=0
 # Проверка всех первых байтов записи, позиций, значений и несовпадения второго слова.
 for marker in range(256):
  for position in range(9):
   for value in (0,1,127,255):
    for different_second in (False,True):
     table=bytearray([255]*50+[128]);offset=position*5
     table[offset:offset+5]=bytes([marker,0x4B,0xF2 if different_second else 0xF3,0x4A,value])
     table[45:50]=bytes([0x38,0x4B,0xF3,0x4A,0x6B])
     # Независимый поиск по физическому формату, отрицательный не-FF байт завершает таблицу.
     chosen=None;end_marker=None
     for index in range(10):
      record=table[index*5:index*5+5]
      if record[0]==255:continue
      if record[0]&128:end_marker=record[0];break
      if record[:4]==bytes([0x38,0x4B,0xF3,0x4A]):chosen=index;break
     for entry in (0xC40F,0xC894,0xC325,0xC88F):
      memory[0x990A:0x993D]=table;memory[0x993D:0x9970]=table;memory[0x9844:0x9848]=bytes([0x38,0x4B,0xF3,0x4A]);memory[0x9848]=0xA5
      memory[0x7FFE:0x8000]=bytes([255,63]);memory[0x6304:0x6306]=bytes([32,24]);sim.registers[:]=initial;r=sim.registers;r[PC]=entry
      if entry==0xC325:r[D],r[E],r[H],r[L]=0x4B,0x38,0x4A,0xF3
      for _ in range(1000):
       if r[PC]==0x3FFF:break
       sim.opcodes[memory[r[PC]]]()
      else:raise AssertionError(('instruction_limit',entry,marker,position))
      assert r[SP]==0x8000 and r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
      if entry==0xC40F:
       expected=0 if chosen is None else table[chosen*5+4]
       assert memory[0x9848]==expected and r[A]==expected and r[B]*256+r[C]==5
       assert r[8]*256+r[9]==0x990A+(position if chosen is None else chosen)*5
       assert r[F]==(0x44 if chosen is None else 0x42)
       assert r[D]*256+r[E]==(0x4AF3 if chosen is None else 0x4B38)
       if chosen is not None:assert r[H]*256+r[L]==0
      elif entry==0xC325:
       expected=0 if chosen is None else table[chosen*5+4];cx,cy,flags=center_reference(0x38F3,0x4B4A,32,24)
       assert memory[0x9848]==expected and bytes(memory[0x9844:0x9848])==bytes([0x38,0x4B,0xF3,0x4A])
       assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F])==((cy&0xFF00)|(cx>>8),((cy&255)<<8)|(cx&255),0xFFF4,cy&255,flags)
       assert bytes(memory[0x6300:0x6304])==bytes([cx&255,cy&255,cx>>8,cy>>8])
       assert r[8]*256+r[9]==0x990A+(position if chosen is None else chosen)*5
      else:
       assert memory[0x9848]==0xA5 and r[8:10]==initial[8:10]
       if chosen is None:assert r[A]==end_marker and r[F]&0xC2==0x82 and r[D]*256+r[E]==(0x993D if entry==0xC88F else 0x990A)+position*5
       else:assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C])==(0,0x44,0,(0x993D if entry==0xC88F else 0x990A)+chosen*5+3,0x4AF3)
      cases+=1;hits+=chosen is not None;ends+=chosen is None
 report=dict(passed=True,cases=cases,found=hits,terminated=ends,
  method='original_two_stored_point_searches_and_complete_selection_centering_all_markers_positions_values',
  record_size=5,empty_byte='FF',terminator_range='80..FE',all_alternate_registers_preserved=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StoredMapPointsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

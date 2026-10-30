"""Исходное построение четырёх таблиц секторов карты, включая обмен общих наборов."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP


def reference(x,y):
 first,second,mix=x,y,0x8237;raw=bytearray()
 for _ in range(128):
  total=((first+second)&65535)^0x0A00;wide=total+mix;new=wide&65535
  raw.extend([second>>8,mix>>8]);last_a=mix>>8;last_flags=0x50|int(wide>65535)
  first,second,mix=second,mix,new
 return raw,first,mix,last_a,last_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 full=single=0
 coords=sorted({(x,y) for x in range(256) for y in (0,1,255)}|{(x,y) for y in range(256) for x in (0,1,255)})
 # Проверка всех байтов X и Y, краёв соседних секторов и точных четырёх страниц результата.
 for x,y in coords:
  memory[0x6302:0x6304]=bytes([x,y]);memory[0x7FFE:0x8000]=bytes([255,63]);memory[0xF1FF:0xF601]=bytes([0xA7])*1026
  sim.registers[:]=initial;r=sim.registers;sim.run(start=0xC44A,stop=0x3FFF)
  for base,sx,sy in ((0xF200,x,y),(0xF300,(x+1)&255,y),(0xF500,(x+1)&255,(y+1)&255),(0xF400,x,(y+1)&255)):
   expected,_,_,last_a,last_f=reference(sx,sy)
   assert bytes(memory[base:base+256])==expected
  assert (r[A],r[F])==(last_a,last_f) and r[2:12]==initial[2:12] and r[SP]==0x8000
  assert r[16:22]==initial[16:22] and r[22:24]==[0xF4,0] and memory[0xF1FF]==memory[0xF600]==0xA7
  full+=1
 # Проверка отдельного помощника, возвращающего противоположный общий набор после EXX.
 for coordinate in range(256):
  x,y=coordinate,255-coordinate;sim.registers[:]=initial;r=sim.registers
  r[H],r[L]=0xF2,0;r[20],r[21]=y,x;memory[0x7FFE:0x8000]=bytes([255,63])
  expected,first,mix,last_a,last_f=reference(x,y);sim.run(start=0xC474,stop=0x3FFF)
  assert bytes(memory[0xF200:0xF300])==expected
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[SP])==(first,y*256+x,mix,last_a,last_f,0x8000)
  assert r[18:22]==initial[2:6] and r[22:24]==[0xF2,0] and r[16:18]==initial[16:18] and r[8:12]==initial[8:12]
  single+=1
 report=dict(passed=True,full_cases=full,single_sector_cases=single,
  method='original_four_adjacent_sector_tables_against_independent_three_word_recurrence',
  quadrant_order=['F200','F300','F500','F400'],single_sector_swaps_general_register_sets=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapSectorTablesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

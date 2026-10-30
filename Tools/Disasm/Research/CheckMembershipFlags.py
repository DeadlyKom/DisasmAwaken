"""Исходные четырёхбайтовые проверки и преобразование старшего бита в код 127 либо 1."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckGlyphRenderer import compare_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 entry=next(e for e in manifest['entries'] if e['slot']==5);source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
 memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFA,'BC':0x36C9,'AF':0x5A00,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts={}
 # Проверка всех индексов, искомых байтов и пяти положений первого совпадения либо отсутствия.
 for start,base,selector in ((0xC558,0x9400,0x9849),(0xC5B2,0x9484,0x984A),(0xC55E,0xA000,None)):
  cases=0
  for index in range(256):
   for value in range(256):
    for position in range(5):
     sim.registers[:]=initial;r=sim.registers;r[A]=value;r[D],r[E]=base>>8,base&255
     memory[0x7FFA:0x7FFE]=bytes((index,0xE3,255,63));address=base+4*index
     if selector is not None:memory[selector]=value
     record=[(value+1)&255]*4
     if position<4:record[position]=value
     memory[address:address+4]=bytes(record)
     # Чтение реального селектора после записи, таблица может перекрыть сам селектор на больших индексах.
     wanted=memory[selector] if selector is not None else value
     found=record.index(wanted) if wanted in record else 4;last=min(found,3)
     expected_hl=address+(found+1 if found<3 else 3)
     sim.run(start=start,stop=0x3FFF)
     assert (r[A],r[F],r[D]*256+r[E],r[H]*256+r[L])==(wanted,compare_flags(wanted,record[last]),int(found==4),expected_hl)
     assert r[B]*256+r[C]==0x36C9 and r[SP]==0x7FFE
     assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
     cases+=1
  counts[hex(start)]=cases
 # Проверка всех байтов старшего маркера при каждом индексе, оба штатных входа и общий хвост.
 for start,base in ((0xC577,0x988E),(0xC5BB,0x98F6),(0xC57A,0xA200),(0xC57A,0xFFFF)):
  cases=0
  for index in range(256):
   for value in range(256):
    sim.registers[:]=initial;r=sim.registers;r[D],r[E]=base>>8,base&255
    memory[0x7FFA:0x7FFE]=bytes((index,0xE3,255,63));memory[(base+index)&65535]=value
    sim.run(start=start,stop=0x3FFF);expected=1 if value&128 else 127
    flags=0x10|(value&0xA8)|(0 if value&128 else 0x44)|int(base+index>65535)
    assert (r[A],r[F],r[D],r[E],r[H]*256+r[L])==(expected,flags,0,expected,(base+index)&65535)
    assert r[B]*256+r[C]==0x36C9 and r[SP]==0x7FFE
    assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    cases+=1
  counts[hex(start)+'_'+hex(base)]=cases
 report=dict(passed=True,method='original_four_byte_membership_and_high_bit_code',cases=counts,
  table_selector_alias_tested=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MembershipFlagsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Исходные пятибайтовые записи, отдельные базы и общие стековые входы."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP


def add16_flags(left,right,old):
 result=left+right
 return (old&0xC4)|((result>>8)&0x28)|(0x10 if (left&0xFFF)+(right&0xFFF)>0xFFF else 0)|(result>0xFFFF)


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 memory=bytearray(65536);memory[0x6000:]=sources[4];memory[0xC000:0xC000+len(sources[5])]=sources[5]
 simulator=Simulator(memory)
 initial=get_registers({'SP':0x7FFA,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A00,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts={};bits=0
 # Проверка всех индексов и флагов для трёх штатных входов и двух общих хвостов.
 for entry,base,word in ((0xC5E9,0x9803,True),(0xC5F9,0x9802,False),(0xC609,0x9806,False),
                         (0xC60F,0x9826,True),(0xC615,0x9829,False),
                         (0xC5EC,0xAFFF,True),(0xC5FC,0x9FFF,False)):
  count=0
  for index in range(256):
   for flags in range(256):
    simulator.registers[:]=initial;r=simulator.registers;r[F]=flags
    if entry in (0xC5EC,0xC5FC):r[D],r[E]=base>>8,base&255
    # Создание старшего байта индекса, который обработчик обязан отбросить.
    memory[0x7FFA:0x7FFE]=bytes((index,(index*73+flags)&255,255,63))
    address=(base+5*index)&0xFFFF
    memory[address]=(index*17+flags*13)&255;memory[address+1]=(index*29+flags*7)&255
    expected=memory[address]+(memory[address+1]*256 if word else 0)
    simulator.run(start=entry,stop=0x3FFF)
    assert r[SP]==0x7FFE and r[H]*256+r[L]==address+int(word)
    assert r[D]*256+r[E]==expected and r[B]*256+r[C]==index
    assert r[A]==0x5A and r[F]==add16_flags(5*index,base,flags)
    assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    count+=1
  counts[hex(entry)]=count
 report=dict(passed=True,method='original_stride5_accessors_and_shared_stack_entries',accessor_cases=counts,
             all_byte_indices=True,all_initial_flags=True,index_high_byte_discarded=True,
             irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StrideFiveVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

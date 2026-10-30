"""Сумма вторичного индекса и прямые чтения кодированных весов через исходный разбор."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckMatrixKey import add_flags
from CheckWorldSignature import logical_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 memory=original.copy();sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 sums=fields=0
 # Проверка всех пар двух исходных компонент индекса без интерпретации их игрового назначения.
 for first in range(256):
  for second in range(256):
   sim.registers[:]=initial;r=sim.registers;memory[0x73D8]=first;memory[0x737D]=second;memory[0x7FFE:0x8000]=bytes([255,63])
   sim.run(start=0xC90C,stop=0x3FFF);value=(first+second)&255
   assert (r[A],r[F],r[B],r[C],r[SP])==(value,add_flags(second,first),0,value,0x8000)
   assert r[H]*256+r[L]==0x1357 and r[D]*256+r[E]==0x247A and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
   sums+=1
 # Проверка прямого пути обоих весов, числового переполнения и обоих знаков кодированного байта.
 for entry,base,row_address,offset_address,alt_count in ((0xC1C8,0x988E,0x7217,0x71B9,2),(0xC1EC,0x98F6,0x73D8,0x737D,2)):
  for prefix in (b'',b'0',b'1',b'30',b'256',b'65535',b'99999'):
   for value in range(256):
    memory[:]=original;memory[row_address]=29;memory[offset_address]=7
    index=(int(prefix)-1)&65535 if prefix else 36;address=(base+index)&65535
    memory[address]=value;memory[0xB000:0xB000+len(prefix)+2]=prefix+b'!\r';memory[0x7FFE:0x8000]=bytes([255,63])
    sim.registers[:]=initial;r=sim.registers;sim.run(start=entry,stop=0x3FFF)
    normalized=value if value<128 else value^255
    flags=logical_flags(value) if value<128 else (logical_flags(value)&0xC5)|0x12|(normalized&0x28)
    assert (r[A],r[F],r[D],r[E],r[H]*256+r[L],r[B],r[C],r[SP])==(normalized,flags,0,normalized,address,0,36,0x8000)
    assert r[8]*256+r[9]==0xB000+len(prefix) and r[10:12]==initial[10:12]
    assert r[18]==alt_count and r[19:24]==initial[19:24] and r[16:18]==initial[16:18]
    fields+=1
 report=dict(passed=True,method='original_secondary_index_and_two_direct_weight_fields',sum_cases=sums,field_cases=fields,
  all_encoded_weight_bytes=True,all_index_component_pairs=True,suffix_handlers_executed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/WeightFieldsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Исходная запись байта десятичными цифрами с безусловным подавлением нулевых десятков."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckMatrixKey import add_flags


def digits(number):
 hundreds,remainder=divmod(number,100);tens,units=divmod(remainder,10)
 return ((str(hundreds) if hundreds else '')+(str(tens) if tens else '')+str(units)).encode()


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;nonstandard=[];memory[0x7FFE:0x8000]=bytes([255,63])
 for address in (0xB000,0xB0FF):
  for number in range(256):
   sim.registers[:]=initial;r=sim.registers;r[A]=number;r[D],r[E]=address>>8,address&255
   memory[address-1:address+5]=bytes([0xA7])*6;sim.run(start=0xE6F6,stop=0x3FFF);expected=digits(number);units=number%10
   assert bytes(memory[address:address+len(expected)])==expected and memory[address-1]==memory[address+len(expected)]==0xA7
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0x1357,address+len(expected),(number%100)//10,units,48+units,add_flags(units,48),0x8000)
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];cases+=1
   if address==0xB000 and expected!=str(number).encode():nonstandard.append(number)
 report=dict(passed=True,cases=cases,method='original_compact_decimal_all_bytes_and_buffer_page_crossing',
  omitted_zero_tens_values=nonstandard,terminator_written=False,calls_stubbed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/CompactDecimalVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

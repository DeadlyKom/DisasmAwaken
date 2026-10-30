"""Числовой литерал, два индексированных байтовых поля и чтение трёхкомпонентного ресурса."""
from pathlib import Path
from itertools import product
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckMarketAccess import add16_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();original=bytearray(65536);original[0xC000:0xC000+len(source)]=source
 memory=original.copy();sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,'^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 numeric=resources=0
 # Проверка композиции с фактическим выходом исходного ReadDecimal5, без замены парсера.
 for number in list(range(256))+[256,65535,65536,99999]:
  text=str(number).encode()+b'!';memory[:]=original;memory[0xB000:0xB000+len(text)]=text
  sim.registers[:]=initial;memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=0xC6EA,stop=0x3FFF);parsed=sim.registers.copy();value=number&65535
  for entry,base in ((0xC323,None),(0xC342,0x9A42),(0xC34D,0x9A33)):
   memory[:]=original;memory[0xB000:0xB000+len(text)]=text;memory[0x7FFE:0x8000]=bytes([255,63])
   if base is not None:address=(base+value)&65535;memory[address]=(number*37)&255;expected=memory[address]
   else:expected=value
   sim.registers[:]=initial;r=sim.registers
   if base is None:r[8],r[9]=0xB0,1
   sim.run(start=entry,stop=0x3FFF)
   assert memory[0xB800:0xB802]==expected.to_bytes(2,'little') and r[22]*256+r[23]==0xB802
   assert r[B:C+1]==parsed[B:C+1] and r[8:12]==parsed[8:12] and r[16:20]==initial[16:20] and r[SP]==0x8000
   if base is None:
    assert (r[D]*256+r[E],r[H]*256+r[L],r[A],r[F])==(value,parsed[D]*256+parsed[E],parsed[A],parsed[F])
    assert r[20]*256+r[21]==value
   else:
    assert (r[D]*256+r[E],r[H]*256+r[L],r[A],r[F])==(base,address,expected,add16_flags(value,base,parsed[F]))
    assert r[20:22]==initial[20:22]
   numeric+=1
 # Проверка двух путей к исходному поиску FF/FE, включая нулевые внешние счётчики как 256.
 for groups,records,offset in product((0,1,2,255),(0,1,255),(0,1,5,255,65535)):
  n=groups or 256;k=records or 256;payload=bytes([0x31,255])*n+bytes([0x32,254])*k
  marker=0x9A49+len(payload)-1;target=(marker+offset)&65535
  for entry in (0xC355,0xC362):
   memory[:]=original;memory[0x9A49:0x9A49+len(payload)]=payload
   if offset!=0:memory[target]=123
   if entry==0xC355:text=str(offset).encode()+b'!';memory[0x9A1C]=groups;memory[0x9A1D]=records;expected_c=groups
   else:text=(str(groups)+'X'+str(records)+'?'+str(offset)+'!').encode();expected_c=records
   memory[0xB000:0xB000+len(text)]=text;memory[0x7FFE:0x8000]=bytes([255,63]);expected=memory[target]
   sim.registers[:]=initial;r=sim.registers;sim.run(start=entry,stop=0x3FFF)
   assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[SP])==(expected,add16_flags(marker,offset,0x44),target,offset,0,expected_c,0x8000)
   assert memory[0xB800:0xB802]==bytes([expected,0]) and r[22]*256+r[23]==0xB802
   assert r[8]*256+r[9]==0xB000+len(text)-1 and r[10:12]==initial[10:12] and r[16:22]==initial[16:22]
   resources+=1
 report=dict(passed=True,numeric_cases=numeric,resource_cases=resources,method='original_numeric_and_delimited_byte_readers_with_expression_push',
  arbitrary_separator_bytes_tested=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/NumericFieldReadsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

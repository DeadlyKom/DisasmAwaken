"""Исходный запрос грузовой пары, первый байт без маски и суффикс c для второго байта."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,SP


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 memory=original.copy();simulator=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts={'default':0,'second_byte':0}
 # Проверка исходного прямого чтения и обработчика суффикса c без заглушек.
 for row in range(32):
  for base in (0,1,29,128,255):
   for prefix in (b'',b'0',b'1',b'30',b'31',b'65535',b'99999'):
    for tail,kind in ((b'!','default'),(b'.c','second_byte')):
     memory[:]=original
     for i in range(30):
      memory[0x9852+2*i]=(i*37+row)&255;memory[0x9853+2*i]=(i*13+base)&255
     memory[0x7068]=row;memory[0x7026]=base;memory[0x984A]=255
     text=prefix+tail+b'\r';memory[0xB000:0xB000+len(text)]=text
     index=((int(prefix)-1)&65535) if prefix else (row+base)&255
     if kind=='default':expected=memory[(0x9852+2*index)&65535]
     else:expected=memory[0x9853+2*(index&255)]
     simulator.registers[:]=initial;r=simulator.registers;memory[0x7FFE:0x8000]=bytes([255,63])
     simulator.run(start=0xC30A,stop=0x3FFF)
     assert r[D]*256+r[E]==expected,(row,base,prefix,tail,expected,list(r))
     assert r[SP]==0x8000 and r[10:12]==initial[10:12]
     assert r[8]*256+r[9]==0xB000+len(prefix)+(0 if kind=='default' else 2)
     counts[kind]+=1
 report=dict(passed=True,method='original_cargo_field_and_second_byte_suffix',cases=counts,
  calls_stubbed=False,selected_row_and_base_wrap=True,explicit_zero_index_tested=True,
  native_execution=False,irq_executed=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/CargoFieldVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Полный исходный путь запроса рынка, включая разбор, поиск токена и расчёт взвешенной суммы."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,SP
from CheckWeightedLoad import reference
from CheckGlyphRenderer import and_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 memory=original.copy();simulator=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts={'default':0,'price':0,'mark':0,'weighted':0}
 # Проверка исходных получателей без заглушек, включая полный суффикс m.
 for row in range(32):
  for base in (0,1,29,128,255):
   for prefix in (b'',b'0',b'1',b'30',b'31',b'65535',b'99999'):
    for tail,kind in ((b'!','default'),(b'.c','price'),(b'.s','mark'),(b'.m','weighted')):
     memory[:]=original
     for i in range(30):
      memory[0x9555+2*i]=(i*37+row)&255;memory[0x9556+2*i]=(i*13+base)&255
     memory[0x7068]=row;memory[0x7026]=base;memory[0x984A]=255
     text=prefix+tail+b'\r';memory[0xB000:0xB000+len(text)]=text
     index=((int(prefix)-1)&65535) if prefix else (row+base)&255
     if kind=='default':expected=memory[(0x9555+2*index)&65535]&127
     elif kind=='price':expected=memory[0x9556+2*(index&255)]
     elif kind=='mark':expected=int(not memory[0x9555+2*(index&255)]&128)
     else:expected=reference(memory,index&255)[0]
     simulator.registers[:]=initial;r=simulator.registers;memory[0x7FFE:0x8000]=bytes([255,63])
     simulator.run(start=0xC26D,stop=0x3FFF)
     assert r[D]*256+r[E]==expected,(row,base,prefix,tail,expected,list(r))
     assert r[SP]==0x8000 and r[10:12]==initial[10:12]
     assert r[8]*256+r[9]==0xB000+len(prefix)+(0 if kind=='default' else 2)
     if kind=='default':assert r[A]==expected and r[F]==and_flags(expected)
     counts[kind]+=1
 report=dict(passed=True,method='original_market_field_entry_suffix_dispatch_and_all_three_handlers',cases=counts,
  calls_stubbed=False,selected_row_and_base_wrap=True,explicit_zero_index_tested=True,
  native_execution=False,irq_executed=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MarketFieldVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Полный исходный путь запроса рынка, включая разбор, поиск токена и расчёт взвешенной суммы."""
from pathlib import Path
import sys,json
from hashlib import sha256
from CheckGeometryReturnEntries import Memory
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,SP
from CheckWeightedLoad import reference,own_writes
from CheckGlyphRenderer import and_flags


def main(with_expression_wrapper=False):
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 # Проверка исходных секторных областей и наблюдателя CPU.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 for slot,data in sources.items():
  item=next(e for e in manifest['entries'] if e['slot']==slot)
  assert data==disk[item['offset']:item['offset']+item['allocated_length']]
  assert sha256(data).hexdigest()==item['sectors_sha256']
 probe=Memory(65536);probe[0x4000:0x4003]=bytes.fromhex('320070')
 cpu=Simulator(probe);cpu.registers[24]=0x4000;probe.recording=True;cpu.run()
 assert probe.writes==[(0x7000,0)]
 memory=Memory(65536);memory[:]=original;simulator=Simulator(memory)
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
     if with_expression_wrapper:r[22],r[23]=0xB8,0
     persistent=[(0xC804,49789&255),(0xC805,49789>>8)]
     if kind=='weighted':
      persistent.extend((a,v) for a,v in own_writes(memory,index&255,0x7FF8) if not 0x7FF4<=a<0x7FFE)
     if with_expression_wrapper:persistent.extend(((0xB800,expected&255),(0xB801,expected>>8)))
     memory.writes.clear();memory.recording=True
     simulator.run(start=49773-6 if with_expression_wrapper else 49773,stop=0x3FFF);memory.recording=False
     # Проверка всех нестековых записей, возврата и результата полного писателя.
     assert [(a,v) for a,v in memory.writes if not (0x7FF4 if with_expression_wrapper else 0x7FF6)<=a<0x7FFE]==persistent
     assert bytes(memory[0x7FFE:0x8000])==bytes([255,63])
     if with_expression_wrapper:
      assert (r[20]*256+r[21],r[22]*256+r[23])==(expected,0xB802)
      assert bytes(memory[0x7FFC:0x7FFE])==expected.to_bytes(2,'little')
     assert r[D]*256+r[E]==expected,(row,base,prefix,tail,expected,list(r))
     assert r[SP]==0x8000 and r[10:12]==initial[10:12]
     assert r[8]*256+r[9]==0xB000+len(prefix)+(0 if kind=='default' else 2)
     if kind=='default':assert r[A]==expected and r[F]==and_flags(expected)
     counts[kind]+=1
 report=dict(passed=True,method='original_market_field_entry_suffix_dispatch_and_all_three_handlers',cases=counts,
  calls_stubbed=False,selected_row_and_base_wrap=True,explicit_zero_index_tested=True,
  expression_wrapper_executed=with_expression_wrapper,physical_disk_and_sector_hashes_checked=True,
  CPU_write_watch_positive_control=True,exact_non_stack_write_sequence_checked=True,
  original_return_word_preserved=True,full_R_proved=False,
  temporary_stack_interval=[0x7FF4 if with_expression_wrapper else 0x7FF6,0x7FFE],
  all_registers_addresses_and_error_suffixes_checked=False,stack_bus_cycle_order_verified=False,
  native_execution=False,irq_executed=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports'/('MarketFieldExpressionWrapperVerification.json' if with_expression_wrapper else 'MarketFieldVerification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main('--expression-wrapper' in sys.argv)

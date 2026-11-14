"""Четыре настоящих входа пятибайтовых записей, включая выбранный байт и индекс банка 4."""
from pathlib import Path
import json,sys
from hashlib import sha256
from CheckBank4Index import WriteMemory
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckGlyphRenderer import compare_flags
from CheckMarketAccess import add16_flags


def main(with_expression_wrappers=False):
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 lang=(ROOT/(e['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=lang
 # Проверка физических секторов LANG, STATION и KARTA.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 for slot in (4,5,7):
  item=next(row for row in manifest['entries'] if row['slot']==slot)
  sectors=(ROOT/(item['path']+'.sectors.bin')).read_bytes()
  assert sectors==disk[item['offset']:item['offset']+item['allocated_length']]
  assert sha256(sectors).hexdigest()==item['sectors_sha256']
 # Проверка наблюдателя самостоятельной записью CPU.
 probe=WriteMemory(banks=[bytearray(0x4000) for _ in range(8)],out7ffd=0x16)
 put(probe,0x4000,bytes.fromhex('320070'));cpu=Simulator(probe)
 cpu.registers[24]=0x4000;probe.recording=True;cpu.run()
 assert probe.cpu_writes==[(0x7000,0)]
 memory=WriteMemory(banks=[b.copy() for b in banks],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 first={'c':(0x9803,True,0xE9),'t':(0x9802,False,0xF9),'s':(0x9806,False,0x09)}
 second={'c':(0x9826,True,0x0F),'v':(0x9829,False,0x15)}
 count=0
 for entry,selector,banked,n,fields in ((0xC207,0x9849,False,3,first),(0xC227,0x984A,False,2,second),
                                     (0xC2D6,0x9849,True,3,first),(0xC2F0,0x984A,True,2,second)):
  for selected in range(256):
   for prefix in (b'',b'0',b'1',b'2',b'15',b'256',b'65535',b'99999'):
    for suffix in ['']+list(fields):
     memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x16)
     memory[0x6306]=0x16;put(memory,0x7FFE,[255,63]);memory.banks[4][0x2146]=selected;memory.banks[4][0x2148]=73
     default=(selected+73)&255 if banked else selected;index=((int(prefix)-1)&65535) if prefix else default
     if suffix:
      base,word,low=fields[suffix];address=base+5*(index&255);memory[address]=(selected*13)&255;memory[address+1]=(selected*71)&255
     memory[selector]=selected;text=prefix+(b'.'+suffix.encode() if suffix else b'!')+b'\r';put(memory,0xB000,list(text))
     if suffix:value=memory[address]+(memory[address+1]*256 if word else 0)
     sim.registers[:]=initial;r=sim.registers;trace=PortTrace(sim);sim.set_tracer(trace)
     if with_expression_wrappers:r[22],r[23]=0xB8,0
     memory.cpu_writes.clear();memory.recording=True
     sim.run(start=entry-6 if with_expression_wrappers else entry,stop=0x3FFF);memory.recording=False
     # Расчёт банковой тени и сохранённого продолжения без суффикса.
     target={0xC207:0xC21A,0xC227:0xC23A,0xC2D6:0xC2E6,0xC2F0:0xC300}[entry]
     persistent=([(0x6306,0x14),(0x6306,0x16)] if banked else [])+[(0xC804,target&255),(0xC805,target>>8)]
     if with_expression_wrappers:
      result=value if suffix else 127 if banked else selected
      persistent.extend(((0xB800,result&255),(0xB801,result>>8)))
      assert (r[20]*256+r[21],r[22]*256+r[23])==(result,0xB802)
      assert bytes(memory[0x7FFC:0x7FFE])==result.to_bytes(2,'little')
     assert [(a,v) for a,v in memory.cpu_writes if not (0x7FF4 if with_expression_wrappers else 0x7FF6)<=a<0x7FFE]==persistent
     assert bytes(memory[0x7FFE:0x8000])==bytes([255,63])
     if not with_expression_wrappers and not banked and not prefix and not suffix:assert memory.cpu_writes==persistent
     if suffix:
      assert (r[D]*256+r[E],r[H]*256+r[L],r[B]*256+r[C],r[A],r[F])==(value,address+int(word),index&255,low,add16_flags(5*(index&255),base,0x40))
     else:
      assert (r[D]*256+r[E],r[H]*256+r[L],r[B],r[C],r[A],r[F])==(127 if banked else selected,index,0,default,33,compare_flags(33,46 if prefix else 48))
     assert r[8]*256+r[9]==0xB000+len(prefix)+(2 if suffix else 0) and r[SP]==0x8000
     assert r[10:12]==initial[10:12] and r[16:18]==initial[16:18] and r[18]==n and r[19]==initial[19]
     if not with_expression_wrappers:assert r[20:24]==initial[20:24]
     assert trace.writes==([(0x7FFD,0x14),(0x7FFD,0x16)] if banked else [])
     count+=1
 report=dict(passed=True,cases=count,method='original_record_field_expression_wrappers' if with_expression_wrappers else 'original_selected_record_fields_and_bank4_record_fields',
  expression_wrappers_executed=with_expression_wrappers,
  all_selected_bytes=True,actual_suffix_letters_verified=True,bank4_sum_stubbed=False,
  physical_disk_and_sector_hashes_checked=True,CPU_write_watch_positive_control=True,
  exact_non_stack_write_sequence_checked=True,original_return_word_preserved=True,
  temporary_stack_interval=[0x7FF4 if with_expression_wrappers else 0x7FF6,0x7FFE],
  selected_no_number_no_suffix_has_no_stack_writes=not with_expression_wrappers,
  full_R_proved=False,all_stack_addresses_pages_and_error_suffixes_checked=False,
  stack_bus_cycle_order_verified=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports'/('RecordFieldExpressionWrappersVerification.json' if with_expression_wrappers else 'RecordFieldSelectorsVerification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main('--expression-wrappers' in sys.argv)

"""Три байтовых суммы индексов и прямые чтения кодированных количеств через исходный разбор."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckMatrixKey import add_flags
from CheckWorldSignature import logical_flags
from CheckGeometryReturnEntries import Memory


def main(with_expression_wrappers=False):
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 # Проверка обеих исходных секторных областей относительно полного TRD.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert hashlib.sha256(disk).hexdigest()==manifest['sha256']
 for slot,data in sources.items():
  e=next(e for e in manifest['entries'] if e['slot']==slot)
  assert data==disk[e['offset']:e['offset']+e['allocated_length']]
  assert hashlib.sha256(data).hexdigest()==e['sectors_sha256']
 # Проверка наблюдателя настоящей записью CPU в отдельную память.
 probe=Memory(65536);probe[0x4000:0x4003]=bytes.fromhex('320070')
 cpu=Simulator(probe);cpu.registers[24]=0x4000;probe.recording=True;cpu.run()
 assert probe.writes==[(0x7000,0)]
 memory=Memory(65536);memory[:]=original;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 sums=fields=0
 # Проверка всех пар компонент трёх сумматоров, включая FF и перенос.
 index_counts={}
 for entry,row_address,offset_address in ((0xC900,0x7217,0x71B9),(0xC90C,0x73D8,0x737D),(0xC918,0x7068,0x7026)):
  # Проверка полной последовательности с различием только двух абсолютных адресов.
  expected=bytes([0x3A])+row_address.to_bytes(2,'little')+bytes([0x4F,0x3A])+offset_address.to_bytes(2,'little')+bytes.fromhex('814f0600c9')
  assert sources[5][entry-0xC000:entry-0xC000+12]==expected
  index_counts[entry]=0
  for first in range(256):
   for second in range(256):
    sim.registers[:]=initial;r=sim.registers;memory[row_address]=first;memory[offset_address]=second;memory[0x7FFE:0x8000]=bytes([255,63])
    refresh=first^second;r[15]=refresh
    memory.writes.clear();memory.recording=True;sim.run(start=entry,stop=0x3FFF);memory.recording=False
    value=(first+second)&255
    assert (r[A],r[F],r[B],r[C],r[SP])==(value,add_flags(second,first),0,value,0x8000)
    assert r[H]*256+r[L]==0x1357 and r[D]*256+r[E]==0x247A and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    assert r[15]==((refresh&128)|((refresh+7)&127)) and not memory.writes
    assert memory[0x7FFE:0x8000]==bytes([255,63])
    sums+=1;index_counts[entry]+=1
 # Проверка прямого пути обоих весов, числового переполнения и обоих знаков кодированного байта.
 for entry,base,row_address,offset_address,alt_count in ((0xC1C8,0x988E,0x7217,0x71B9,2),(0xC1EC,0x98F6,0x73D8,0x737D,2)):
  for prefix in (b'',b'0',b'1',b'30',b'256',b'65535',b'99999'):
   for value in range(256):
    memory[:]=original;memory[row_address]=29;memory[offset_address]=7
    index=(int(prefix)-1)&65535 if prefix else 36;address=(base+index)&65535
    memory[address]=value;memory[0xB000:0xB000+len(prefix)+2]=prefix+b'!\r';memory[0x7FFE:0x8000]=bytes([255,63])
    sim.registers[:]=initial;r=sim.registers;refresh=(value^len(prefix))&255;r[15]=refresh
    # Расчёт временного возврата индекса и записей необязательного десятичного аргумента.
    second=entry==0xC1EC
    ret=0xC1F6 if second else 0xC1D2
    direct=0xC1FC if second else 0xC1D8
    expected_writes=[(0x7FFC,ret&255),(0x7FFD,ret>>8),(0xC804,direct&255),(0xC805,direct>>8)]
    if prefix:
     expected_writes.extend(((0x7FFC,36),(0x7FFD,0),(0x7FFA,0xF2 if second else 0xEC),
                             (0x7FFB,0xC9),(0x7FF8,0x0B),(0x7FF9,0xC8)))
     if len(prefix)>1:
      expected_writes.extend(((0x7FF6,2*(prefix[-2]-48)),(0x7FF7,0)))
      for position in range(len(prefix)-3,-1,-1):
       expected_writes.extend(((0x7FF6,prefix[position]-48),(0x7FF7,0)))
    if with_expression_wrappers:
     r[22],r[23]=0xB8,0
     expected_writes=[(a-2 if a<0x8000 else a,v) for a,v in expected_writes]
     wrapper_return=entry-3
     normalized=value if value<128 else value^255
     expected_writes=[(0x7FFC,wrapper_return&255),(0x7FFD,wrapper_return>>8)]+expected_writes+[
      (0x7FFC,normalized),(0x7FFD,0),(0xB800,normalized),(0xB801,0)]
    memory.writes.clear();memory.recording=True
    sim.run(start=entry-6 if with_expression_wrappers else entry,stop=0x3FFF);memory.recording=False
    assert memory.writes==expected_writes
    assert memory[0x7FFE:0x8000]==bytes([255,63])
    # Проверка M1 прямого поля, включая ветвь инверсии текущего кода.
    decimal_cost=(14,39,68,103,134)[len(prefix)-1] if prefix else 0
    cost=(44+decimal_cost if prefix else 32)+int(second)+int(value>=128)+(11 if with_expression_wrappers else 0)
    assert r[15]==((refresh&128)|((refresh+cost)&127)),(entry,prefix,value,r[15],cost)
    normalized=value if value<128 else value^255
    flags=logical_flags(value) if value<128 else (logical_flags(value)&0xC5)|0x12|(normalized&0x28)
    assert (r[A],r[F],r[D],r[E],r[H]*256+r[L],r[B],r[C],r[SP])==(normalized,flags,0,normalized,address,0,36,0x8000)
    assert r[8]*256+r[9]==0xB000+len(prefix) and r[10:12]==initial[10:12]
    assert r[18]==alt_count and r[19]==initial[19] and r[16:18]==initial[16:18]
    if with_expression_wrappers:
     assert (r[20]*256+r[21],r[22]*256+r[23])==(normalized,0xB802)
     assert bytes(memory[0x7FFC:0x7FFE])==bytes([normalized,0])
    else:assert r[20:24]==initial[20:24]
    fields+=1
 report=dict(passed=True,method='original_direct_quantity_expression_wrappers' if with_expression_wrappers else 'original_three_byte_index_adders_and_two_direct_weight_fields',
  expression_wrappers_executed=with_expression_wrappers,sum_cases=sums,field_cases=fields,
  all_encoded_weight_bytes=True,all_index_component_pairs=True,suffix_handlers_executed=False,
  direct_quantity_exact_R_and_CPU_writes_checked=True,direct_quantity_return_word_preserved=True,
  direct_quantity_suffix_paths_checked=False,
  index_cases_by_entry=index_counts,index_M1=7,index_no_CPU_RAM_writes=True,
  index_exact_R_and_return_word_checked=True,CPU_write_watch_positive_control=True,
  physical_disk_and_sector_hashes_checked=True,
  full_index_component_AF_R_cartesian_product_checked=False,arbitrary_stack_addresses_checked=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports'/('QuantityExpressionWrappersVerification.json' if with_expression_wrappers else 'WeightFieldsVerification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main('--expression-wrappers' in sys.argv)

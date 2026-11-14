"""Оригинальный разбор необязательного индекса и точки, остановка до выбранного обработчика."""
from pathlib import Path
import hashlib,sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckGlyphRenderer import compare_flags
from CheckGeometryReturnEntries import Memory


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 entry=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
 # Проверка физических байтов перед исполнением модели.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert hashlib.sha256(disk).hexdigest()==manifest['sha256']
 assert source==disk[entry['offset']:entry['offset']+entry['allocated_length']]
 assert hashlib.sha256(source).hexdigest()==entry['sectors_sha256']
 # Проверка наблюдателя положительным примером записи настоящего CPU.
 probe=Memory(65536);probe[0x4000:0x4003]=bytes.fromhex('320070')
 cpu=Simulator(probe);cpu.registers[24]=0x4000;probe.recording=True;cpu.run()
 assert probe.writes==[(0x7000,0)]
 memory=Memory(65536);memory[0xC000:0xC000+len(source)]=source
 simulator=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x9F00,'DE':0xB100,'BC':0xA75D,
  'IX':0xB000,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x03BE,'^AF':0x69CF},None,False)
 counts={'first_byte':0,'decimal':0,'suffix':0,'short_boundaries':0}
 def run(text,digits,number,kind):
  memory.recording=False
  simulator.registers[:]=initial;r=simulator.registers
  seed=sum(counts.values())
  r[14],r[15],r[26],r[27]=(seed>>8)&255,seed&255,seed&1,seed%3
  saved=list(r)
  memory[0xB000:0xB010]=bytes(16);memory[0xB000:0xB000+len(text)]=text
  memory[0x7FFE:0x8000]=bytes([255,63])
  index=(number-1)&65535 if digits else 0x5D
  cursor=digits
  suffix=text[cursor]==46
  # Проверка исходного потока до банка диспетчера либо до самомодифицированного перехода.
  r[24]=0xC7EE
  memory.writes.clear();memory.recording=True
  steps=0
  while r[24] not in (0xC7DA,0x9F00):
   simulator.opcodes[memory[r[24]]]()
   steps+=1
   assert steps<300
  memory.recording=False
  # Расчёт всех собственных записей до входа диспетчера либо продолжения.
  expected=[(0xC804,0),(0xC805,159)]
  if digits:
   expected.extend(((0x7FFC,0x5D),(0x7FFD,0xA7),(0x7FFA,0),(0x7FFB,0xB1),
                    (0x7FF8,0x0B),(0x7FF9,0xC8)))
   if digits>1:
    expected.extend(((0x7FF6,2*(text[digits-2]-48)),(0x7FF7,0)))
    for position in range(digits-3,-1,-1):
     expected.extend(((0x7FF6,text[position]-48),(0x7FF7,0)))
  if suffix:expected.extend(((0x7FFC,index&255),(0x7FFD,index>>8)))
  assert memory.writes==expected,(text,memory.writes,expected)
  assert memory[0x7FFE:0x8000]==bytes([255,63])
  assert all(r[i]==saved[i] for i in (14,26,27)) and r[15]&128==saved[15]&128
  assert memory[0xC804:0xC806]==bytes([0,159])
  assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
  if suffix:
   assert (r[24],r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0xC7DA,0xB100,index,3,0x5D,text[cursor+1],compare_flags(46,46),0x7FFC), (text, list(r))
   assert memory[0x7FFC]+256*memory[0x7FFD]==index
   cursor+=2;counts['suffix']+=1
  else:
   assert r[24]==0x9F00 and r[H]*256+r[L]==index and r[D]*256+r[E]==0xB100
   assert r[B]*256+r[C]==0xA75D and r[SP]==0x7FFE
   limit=46 if digits else (48 if text[0]<48 else 58)
   assert r[A]==text[cursor] and r[F]==compare_flags(text[cursor],limit)
  assert r[10]*256+r[11]==0x5C3A and r[8]*256+r[9]==0xB000+cursor
  counts[kind]+=1
 # Проверка всех начальных байтов, включая точку, цифры и недопустимые символы.
 for first in range(256):
  digit=48<=first<58
  run(bytes([first,33,13]),int(digit),first-48 if digit else 0,'first_byte')
 # Проверка 00000..99999 с точкой и без, переполнение слова и декремент нуля сохраняются.
 for number in range(100000):
  digits=str(number).zfill(5).encode()
  for tail in (b'.c',b'!'):
   run(digits+tail+b'\r',5,number&65535,'decimal')
 # Проверка коротких чисел на границах десятичного порядка с точкой и без неё.
 for width in (2,3,4):
  for number in (0,1,10**width-1):
   digits=str(number).zfill(width).encode()
   for tail in (b'.c',b'!'):run(digits+tail+bytes([13]),width,number,'short_boundaries')
 report=dict(passed=True,method='original_suffix_parser_and_decimal_reader_until_tail_target',cases=counts,
  physical_disk_and_sector_hashes_checked=True,exact_CPU_write_sequence_checked=True,
  CPU_write_watch_positive_control=True,stack_bus_cycle_order_verified=False,
  preserved_return_word=True,I_IFF_IM_and_R_bit7_checked=True,
  arbitrary_pointer_or_stack_addresses_checked=False,full_joint_register_product_checked=False,
  dispatch_or_field_handler_executed=False,decimal_reader_stubbed=False,irq_executed=False,
  native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/FieldSuffixVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

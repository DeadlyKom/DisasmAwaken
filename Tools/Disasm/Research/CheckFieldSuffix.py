"""Оригинальный разбор необязательного индекса и точки, остановка до выбранного обработчика."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckGlyphRenderer import compare_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 entry=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
 memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source
 simulator=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x9F00,'DE':0xB100,'BC':0xA75D,
  'IX':0xB000,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x03BE,'^AF':0x69CF},None,False)
 counts={'first_byte':0,'decimal':0,'suffix':0}
 def run(text,digits,number,kind):
  simulator.registers[:]=initial;r=simulator.registers
  memory[0xB000:0xB010]=bytes(16);memory[0xB000:0xB000+len(text)]=text
  memory[0x7FFE:0x8000]=bytes([255,63])
  index=(number-1)&65535 if digits else 0x5D
  cursor=digits
  suffix=text[cursor]==46
  # Проверка исходного потока до банка диспетчера либо до самомодифицированного перехода.
  r[24]=0xC7EE
  steps=0
  while r[24] not in (0xC7DA,0x9F00):
   simulator.opcodes[memory[r[24]]]()
   steps+=1
   assert steps<300
  assert memory[0xC804:0xC806]==[0,159] or memory[0xC804:0xC806]==bytearray([0,159])
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
 report=dict(passed=True,method='original_suffix_parser_and_decimal_reader_until_tail_target',cases=counts,
  dispatch_or_field_handler_executed=False,decimal_reader_stubbed=False,irq_executed=False,
  native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/FieldSuffixVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

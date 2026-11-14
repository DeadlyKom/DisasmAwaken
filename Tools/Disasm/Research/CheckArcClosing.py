"""Завершающие битовые маски исходного ядра, в том числе совпадение двух адресов."""
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC,R
from ReferenceControlsPointRespawn import refresh
from hashlib import sha256
from CheckRowHighlight import make_context


def fill_low(value,mode):
 return value|((value-1)&255) if mode==0x38 else 255 if value==0 else value&((value+1)&255)


def fill_high(value,mode):
 if value==0:return 255
 return value|((255<<value.bit_length())&255) if mode==0x38 else value&(255>>(8-(value^255).bit_length()))


def high_loop_b(value,mode):return 0 if value==0 else 255>>(8-(value if mode==0x38 else value^255).bit_length())


def low_loop_b(value,mode):
 if value==0:return 0
 vector=value if mode==0x38 else value^255
 shift=(vector&-vector).bit_length() if vector else 9
 return value>>shift


def skipped_low(value,mode):
 vector=value if mode==0x38 else value^255
 return 8 if vector==0 else (vector&-vector).bit_length()-1


def skipped_high(value,mode):
 vector=value if mode==0x38 else value^255
 return 8 if vector==0 else 8-vector.bit_length()


def closing_M1(entry,value,mode,left_input=None):
 if entry==0xE41A:return 14 if value==0 else 19+5*skipped_low(value,mode)
 if entry==0xE430:return 13 if value==0 else 16+5*skipped_high(value,mode)
 assert entry==0xE445 and left_input is not None
 return 22+(0 if value==0 else 5+5*skipped_low(value,mode))+(0 if left_input==0 else 3+5*skipped_high(left_input,mode))


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 for slot in (4,7):
  row=next(x for x in manifest['entries'] if x['slot']==slot)
  assert (ROOT/(row['path']+'.sectors.bin')).read_bytes()==disk[row['offset']:row['offset']+row['allocated_length']]
 _,source,banks=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FF0,'HL':0x4785,'DE':0xAA83,'BC':0x36C9,'AF':0x1357,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts=collections.Counter()
 refresh_cases=0;initial_R_codes=set();costs=collections.Counter();witnesses=[]
 def run_with_refresh(entry,cost,witness=False):
  nonlocal refresh_cases
  initial_r=refresh_cases&255;initial_R_codes.add(initial_r);sim.registers[R]=initial_r
  if witness:
   sim.registers[PC]=entry;m1=0
   # Проверка абсолютной стоимости на пошаговых свидетелях с учётом префикса LD SP,(nn).
   for _ in range(256):
    pc=sim.registers[PC]
    if pc==0x3FFF:break
    opcode=memory[pc]
    assert opcode not in (0xDD,0xFD)
    assert memory[pc:pc+2] not in (b'\xed\x4f',b'\xed\x5f')
    m1+=2 if opcode in (0xCB,0xED) else 1
    sim.opcodes[opcode]()
    assert sim.registers[R]==refresh(initial_r,m1)
   else:raise AssertionError(('closing_instruction_limit',entry))
   assert m1==cost,(entry,m1,cost)
   witnesses.append(dict(entry=entry,initial_R=initial_r,final_R=sim.registers[R],observed_M1=m1))
  else:sim.run(start=entry,stop=0x3FFF)
  assert sim.registers[R]==refresh(initial_r,cost)
  costs[entry,cost]+=1;refresh_cases+=1
 # Проверка фактического писателя четырёх кодов JR для всех 256 значений исходного операнда DFC4.
 for value in range(256):
  memory[0xDFC4]=value;sim.registers[:]=initial;sim.registers[F]=value^0x5A;sim.run(start=0xDFC3,stop=0xDFD8)
  assert all(memory[address]==(0x38 if value&1 else 0x30) for address in (0xE426,0xE438,0xE44F,0xE460))
 for mode in (0x38,0x30):
  memory[0xDFC4]=1 if mode==0x38 else 0;sim.registers[:]=initial;sim.run(start=0xDFC3,stop=0xDFD8)
  # Проверка двух одиночных масок для каждого байта и каждого старого AF, снимаемого с сохранённого кадра.
  for entry in (0xE41A,0xE430):
   for value in range(256):
    for flags in range(256):
     memory[0xDFB4:0xDFB6]=(0x7FFA).to_bytes(2,'little');memory[0x7FFA:0x7FFE]=bytes([flags,0x5A,255,63]);memory[0x4782:0x4787]=bytes([0xA7,value,0xA7,value,0xA7])
     sim.registers[:]=initial;r=sim.registers;run_with_refresh(entry,closing_M1(entry,value,mode),flags==0 and value in (0,1,0x80,0xFF))
     address=0x4783 if entry==0xE41A else 0x4785;result=fill_low(value,mode) if entry==0xE41A else fill_high(value,mode)
     b=low_loop_b(value,mode) if entry==0xE41A else high_loop_b(value,mode)
     expected=bytearray([0xA7,value,0xA7,value,0xA7]);expected[address-0x4782]=result
     assert memory[0x4782:0x4787]==expected
     assert (r[H]*256+r[L],r[B],r[C],r[A],r[F],r[SP])==(address,b,0xC9,0x5A,flags,0x7FFE)
     assert r[D]*256+r[E]==0xAA83 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
     counts[format(mode,'02X')+':'+format(entry,'04X')]+=1
  # Проверка всех пар левого и правого байтов, а также последовательных преобразований одного общего байта.
  for same in (False,True):
   for left in range(256):
    for right in range(256) if not same else (left,):
     left_address=0x4785 if same else 0x4783;memory[0x4782:0x4787]=bytes([0xA7,left,0xA7,right,0xA7])
     memory[0xDFB4:0xDFB6]=(0x7FFA).to_bytes(2,'little');memory[0x7FFA:0x7FFE]=bytes([0x5D,0x5A,255,63]);sim.registers[:]=initial;r=sim.registers
     # E445 сначала EXX, поэтому растровые адреса и маски передаются альтернативным набором.
     r[22],r[23]=0x47,0x85;r[20],r[21]=0xAA,left_address&255;r[18],r[19]=0x36,0xC9;core=list(r[B:L+1])
     after_right=fill_low(right,mode);left_input=after_right if same else left;after_left=fill_high(left_input,mode)
     run_with_refresh(0xE445,closing_M1(0xE445,right,mode,left_input),left in (0,0xFF) and right in (0,0xFF))
     expected=bytearray([0xA7,left,0xA7,right,0xA7]);expected[3]=after_right;expected[left_address-0x4782]=after_left
     assert memory[0x4782:0x4787]==expected
     assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(left_address,0xAA00+(left_address&255),high_loop_b(left_input,mode),0xC9,0x5A,0x5D,0x7FFE)
     assert r[18:24]==core and r[8:12]==initial[8:12] and r[16:18]==initial[16:18]
     counts[format(mode,'02X')+(' E445_same_byte' if same else ' E445_two_bytes')]+=1
 assert refresh_cases==sum(counts.values()) and initial_R_codes==set(range(256))
 report=dict(passed=True,cases=sum(counts.values()),cases_by_entry=dict(counts),method='both_actual_self_modified_arc_closing_modes_against_integer_bit_operations_all_bytes_pairs_and_saved_AF',
  mode_writer_cases=256,mode_opcodes=[0x38,0x30],zero_byte_always_becomes_FF=True,
  JR_C_low_formula='v OR ((v-1) AND 255)',JR_NC_low_formula='255 if v=0 else v AND ((v+1) AND 255)',
  same_address_uses_updated_byte=True,saved_stack_pointer_and_AF_checked=True,full_arc_kernel_proved=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False,
  refresh_verification=dict(cases=refresh_cases,initial_R_codes=sorted(initial_R_codes),
   final_R_from_independent_bit_run_length_formulas=True,original_disk_sha256=manifest['sha256'],
   witnesses=witnesses,witness_count=len(witnesses),cost_profiles=[dict(entry=e,M1=m1,cases=n) for (e,m1),n in sorted(costs.items())],
   every_instruction_R_checked_only_in_witnesses=True,independent_R_input_product_proved=False))
 old=json.loads((ROOT/'Tools/Disasm/Reports/ArcClosingVerification.json').read_bytes())
 assert all(report[k]==v for k,v in old.items())
 (ROOT/'Tools/Disasm/Reports/ArcClosingVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(dict(passed=True,cases=refresh_cases,witnesses=len(witnesses),maximum_M1=max(m1 for _,m1 in costs)),ensure_ascii=False))


if __name__=='__main__':main()

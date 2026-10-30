"""Исходная подпись варианта ключа, рабочий ключ, глифы и десятичный хвост."""
from pathlib import Path
import json,sys
from itertools import product
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckWorldSignature import step_key


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;single=0
 # Проверка всех порядковых байтов при каждой из восьми XOR-свёрток исходного ключа.
 for fold in range(8):
  first=0x4B38;second=0x4A00|((first>>8)^(first&255)^0x4A^fold)
  for variant,entry in product(range(256),(0xC8C9,0xC8C2)):
   sim.registers[:]=initial;r=sim.registers;r[A]=variant;r[H],r[L]=first>>8,first&255;r[D],r[E]=second>>8,second&255
   for address,value in ((0x6320,0),(0x6321,0),(0xAEAB,192),(0xAEB3,255),(0xAEBB,0),(0xAEBF,0),(0xAEC7,0),(0xAECB,0),(0xBD26,0)):memory[address]=value
   memory[0x7FFE:0x8000]=bytes([255,63]);memory[0x9844:0x9848]=first.to_bytes(2,'little')+second.to_bytes(2,'little');r[PC]=entry;glyphs=[];steps=0
   if entry==0xC8C2:r[H],r[L],r[D],r[E]=0x13,0x57,0x24,0x7A
   current_first,current_second=first,second;previous_second=None
   if fold<2:expected=b'-';expected_calls=0
   else:
    for _ in range(variant+1):previous_second=current_second;current_first,current_second,checksum=step_key(current_first,current_second)
    number=((checksum>>4)+1+variant)&255
    expected=bytes([0x80+(checksum&15),45])+str(number).encode();expected_calls=variant+1
   for _ in range(50000):
    if r[PC]==0x3FFF:break
    if r[PC]==0xAE8D:glyphs.append(r[A])
    if r[PC]==0xA9F3:steps+=1
    sim.opcodes[memory[r[PC]]]()
   else:raise AssertionError(('instruction_limit',fold,variant,hex(r[PC])))
   assert bytes(glyphs)==expected and steps==expected_calls,(fold,variant,glyphs,expected)
   assert bytes(memory[0x631C:0x6320])==current_first.to_bytes(2,'little')+current_second.to_bytes(2,'little')
   assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
   assert (r[A],r[F])==(0,0x45)
   if fold<2:
    assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C])==(first,second,(variant+1)&255,variant);single+=1
   else:assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C])==(previous_second,current_second,10)
   cases+=1
 report=dict(passed=True,cases=cases,hyphen_only_cases=single,
  method='original_variant_label_all_variant_bytes_all_fold_classes_actual_key_steps_glyphs_and_decimal',
  all_variant_bytes=True,all_fold_classes=True,number_wrap_preserved=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/VariantLabelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

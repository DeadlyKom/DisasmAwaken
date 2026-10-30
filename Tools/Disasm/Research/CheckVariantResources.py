"""Исходный выбор четырёх ресурсов варианта и подготовка шести изменяемых указателей."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context


def main():
 _,source,banks=make_context();original=bytearray(65536);original[0x4000:0x8000]=bytes(banks[5]);original[0x8000:0xC000]=bytes(banks[2]);original[0xC000:0xC000+len(source)]=source
 memory=original.copy();sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 targets=(0xC6C1,0xC6DE,0xC6FB,0xC718,0xC735,0xC752);direct=prepared=0
 modes=('current','selected','stored','empty_before_match','end','wrong_value')
 def prepare(mode,wanted):
  memory[:]=original;memory[0x7FFE:0x8000]=bytes([255,63])
  memory[0x9844:0x9848]=bytes([0x38,0x4B,0xF3,0x4A]);memory[0x983F:0x9843]=bytes([0x38 if mode=='current' else 0x39,0x4B,0xF3,0x4A]);memory[0x9843]=wanted
  memory[0x9848]=wanted if mode=='selected' else (wanted+1)&255
  table=bytearray([128]+[255]*50)
  if mode in ('stored','wrong_value'):
   table[:5]=bytes([0x38,0x4B,0xF3,0x4A,wanted if mode=='stored' else (wanted+1)&255]);table[5]=128
  if mode=='empty_before_match':table[:11]=bytes([255]*5+[0x38,0x4B,0xF3,0x4A,wanted,128])
  memory[0x993D:0x9970]=table
  return table
 # Проверка всех порядковых байтов, четырёх счётчиков и приоритета трёх совпадающих категорий.
 for count in (0,1,6,255):
  for wanted in range(256):
   for mode in modes:
    prepare(mode,wanted);sim.registers[:]=initial;r=sim.registers;r[B]=(count-wanted)&255;memory[0xC7B6]=count
    sim.run(start=0xC7B4,stop=0x3FFF);expected={'current':0xCD33,'selected':0xCD93,'stored':0xCD63}.get(mode,0xCD03)
    assert r[H]*256+r[L]==expected and (r[B],r[C])==((count-wanted)&255,0xC9)
    assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
    if mode in ('current','selected'):assert r[8:10]==initial[8:10] and r[A]==wanted
    else:assert memory[0xC817]==wanted
    direct+=1
 # Проверка всех входных количеств и ограничения подготовки шестью физическими операндами.
 for count in range(256):
  for mode in ('current','selected','stored','empty_before_match'):
   prepare(mode,0);sim.registers[:]=initial;r=sim.registers;r[A]=count
   for address in targets:memory[address:address+2]=bytes([0xA5,0x5A])
   sim.run(start=0xC781,stop=0x3FFF);number=count if 1<=count<=5 else 6
   for index,address in enumerate(targets):
    pointer=int.from_bytes(memory[address:address+2],'little')
    expected=0x5AA5 if index>=number else {'current':0xCD33,'selected':0xCD93,'stored':0xCD63}.get(mode,0xCD03) if index==0 else 0xCD93 if index==1 and mode!='selected' else 0xCD03
    assert pointer==expected,(count,mode,index,hex(pointer),hex(expected))
   assert memory[0xC7B6]==count and r[C]==0xC9 and r[B]==(0 if 1<=count<=5 else (count-5)&255)
   assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24] and r[SP]==0x8000;prepared+=1
 report=dict(passed=True,direct_cases=direct,prepare_cases=prepared,
  method='original_variant_resource_priority_all_variant_bytes_and_all_prepare_counts',
  negative_empty_byte_terminates_secondary_scan=True,count_zero_prepares_six=True,
  max_pointers_written=6,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/VariantResourcesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

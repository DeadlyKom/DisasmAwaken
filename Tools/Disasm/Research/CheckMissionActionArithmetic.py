"""Локальные арифметические участки миссии, без подмены полного игрового запуска."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,H,L,PC,SP
from CheckRowHighlight import make_context


def main():
 _,_,banks=make_context();memory=bytearray(65536)
 memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2])
 sim=Simulator(memory);initial=get_registers({'SP':0x5FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
  'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,'^AF':0x69CF,'^BC':0x58BE,'^DE':0x47AD,'^HL':0x369C},None,False)
 def execute(start,stops):
  r=sim.registers;r[PC]=start
  for _ in range(100):
   if r[PC] in stops:return r[PC]
   sim.opcodes[memory[r[PC]]]()
  raise AssertionError(('instruction_limit',hex(r[PC])))
 accepted=rejected=wrapped=cancel=penalty=0;examples=[]
 # Проверка всех пар используемого и требуемого тоннажа на границах вместимости.
 for used in range(256):
  for required in range(256):
   total=(used+required)&255
   for capacity in sorted({0,255,total,max(0,total-1),min(255,total+1)}):
    sim.registers[:]=initial;memory[0x99A3]=0xA5;memory[0x99A4]=0x5A
    memory[0x9850:0x9854]=bytes([used,capacity,255-used,0xC7]);memory[0x98BE:0x98C0]=bytes([required,0xB3])
    stop=execute(0x6ED6,{0x6F14,0x6F34,0x6F5D});ok=capacity>=total
    assert stop==(0x6F14 if ok else 0x6F34)
    assert memory[0x9850]==(total if ok else used)
    assert memory[0x9852]==((255-used+required)&255 if ok else 255-used)
    assert (memory[0x99A3],memory[0x99A4],memory[0x9853])==((1,0,10) if ok else (0xA5,0x5A,0xC7))
    assert sim.registers[SP]==initial[SP] and sim.registers[8:12]==initial[8:12] and sim.registers[16:24]==initial[16:24]
    accepted+=ok;rejected+=not ok;wrapped+=ok and used+required>255
 # Проверка всех сочетаний сохранённых H и D на четырёх границах младших байтов.
 for high_left in range(256):
  for high_right in range(256):
   for quantity,required in ((0,1),(1,1),(255,1),(0,255)):
    sim.registers[:]=initial;r=sim.registers;r[H]=high_left;r[D]=high_right
    memory[0x9852]=quantity;memory[0x98BE]=required;memory[0x99A3]=1
    execute(0x6F5D,{0x6F73});borrow=(high_left*256+quantity)<(high_right*256+required)
    expected=0 if borrow else (quantity-required)&255
    assert memory[0x9852]==expected and memory[0x99A3]==0
    assert r[SP]==initial[SP] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    if len(examples)<4 and expected!=max(0,quantity-required):
     examples.append(dict(H=high_left,D=high_right,quantity=quantity,required=required,result=expected))
    cancel+=1
 # Проверка всех денежных слов до вывода сообщения, без исполнения LANG и рисователей.
 for credits in range(65536):
  sim.registers[:]=initial;memory[0x984E:0x9850]=credits.to_bytes(2,'little')
  execute(0x6F85,{0x6F94})
  assert int.from_bytes(memory[0x984E:0x9850],'little')==max(0,credits-1000)
  penalty+=1
 report=dict(passed=True,accept_cases=accepted+rejected,accepted=accepted,rejected=rejected,
  accepted_wrapped_sums=wrapped,cancel_cases=cancel,penalty_cases=penalty,
  cancellation_differs_from_byte_saturation_examples=examples,
  method='original_instruction_slices_with_independent_wrapped_byte_and_full_word_oracles',
  script_executed=False,drawers_executed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionActionArithmeticVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

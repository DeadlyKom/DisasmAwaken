"""Интеграция A806, два настоящих рисования и защита указателя, без подмены вызовов."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,PC,SP
from CheckRowHighlight import make_context


def main():
 station,_,banks=make_context();base=bytearray(65536);base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0]);cases=equal=0
 initial=get_registers({'SP':0x7FFE,'HL':0,'DE':1,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 # Проверка всех исходных флаговых байтов, разных индексов и совпадающих старой и новой записей.
 for old_index,new_index in ((0,1),(1,0),(0,45),(45,0),(20,20)):
  for old_flags in range(256):
   memory=bytearray(base);memory[0x4000:0x6000]=bytes([0x96])*8192
   memory[0x8500:0x8600]=bytes([0x80,0xFF])*128;memory[0x8600:0x8900]=bytes(768)
   memory[0x6307:0x6309]=bytes([240,184]);memory[0x6548]=1;memory[0x9B16]=0
   memory[0x9A90:0x9A92]=bytes([0x58,0x9A]);memory[0x9A8D:0x9A8F]=bytes([0xFF,0xFF])
   memory[0xE4AA:0xE4AA+1024]=b'\nA\rB\n'+bytes([10])*1018
   memory[0xBD4F]=0xC3;memory[0xAED5:0xAED8]=station[0x4ED5:0x4ED8]
   old_address=0xF0FD+16*old_index;new_address=0xF0FD+16*new_index;new_flags=(old_flags*73+11)&255
   memory[new_address:new_address+6]=bytes([14,10,10,5,new_flags,0]);memory[old_address:old_address+6]=bytes([1,1,8,4,old_flags,0])
   sim=Simulator(memory);sim.registers[:]=initial;r=sim.registers;r[H],r[L]=old_index>>8,old_index&255;r[D],r[E]=new_index>>8,new_index&255
   memory[0x7FFE:0x8000]=bytes([255,63]);original=bytes(memory[0xF0FD:0xF0FD+46*16])
   sim.run(start=0xA806,stop=0xC2DF)
   assert (r[H]*256+r[L],r[D]*256+r[E],memory[old_address+4],memory[0x9B16])==(old_index,old_index,old_flags&254,1)
   assert r[SP]==0x7FFA and memory[0x7FFC:0x7FFE]==new_index.to_bytes(2,'little')
   sim.run(stop=0xA816);assert r[H]*256+r[L]==old_index and r[D]*256+r[E]==old_index and r[A]==0xC3
   sim.run(stop=0xC2DF);wanted_new=((old_flags&254) if old_index==new_index else new_flags)|1
   assert (r[H]*256+r[L],r[D]*256+r[E],memory[new_address+4],memory[0x9B16])==(new_index,new_index,wanted_new,1)
   assert r[SP]==0x7FFC
   sim.run(stop=0xA829);last_af=(r[A],r[F]);assert r[H]*256+r[L]==new_index and r[D]*256+r[E]==new_index and r[A]==0xC3
   sim.run(stop=0x3FFF)
   assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==(new_index,new_index,*last_af,0x8000)
   assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[18:23]==initial[18:23] and memory[0x9B16]==0
   wanted=bytearray(original);wanted[old_index*16+4]&=254;wanted[new_index*16+4]|=1
   assert memory[0xF0FD:0xF0FD+46*16]==wanted
   equal+=old_index==new_index;cases+=1
 report=dict(passed=True,cases=cases,equal_index_cases=equal,all_old_flag_bytes=True,other_item_fields_preserved=True,
  draw_calls_per_case=2,real_centered_renderer_and_pointer_guards=True,pointer_initially_restored=True,pointer_outside_items=True,
  method='original_A806_call_argument_and_frame_trace_full_real_callees_flag_updates_and_return_registers',
  independent_compound_bitmap_oracle=False,callee_bitmap_models='CenteredItemVerification.json and PointerVerification.json',
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ItemContourSwitchVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Исходный сумматор двух байтов из банка 4 с возвратом банка LANG 6."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import logical_flags
from ProbeShipPreviewCallbacks import payload


class WriteMemory(SliceableMemory):
 recording=False
 def __init__(self,**kwargs):
  super().__init__(**kwargs);self.cpu_writes=[]
 def __setitem__(self,address,value):
  if self.recording:
   assert isinstance(address,int)
   self.cpu_writes.append((address,value))
  super().__setitem__(address,value)


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 d3d=payload(6);banks[4][:len(d3d)]=d3d
 assert bytes(banks[4][0x2145:0x2149])==bytes.fromhex('3E 00 C6 00')
 # Проверка наблюдателя фактической записью CPU в отдельный банковый контекст.
 probe=WriteMemory(banks=[bytearray(0x4000) for _ in range(8)],out7ffd=0x16)
 put(probe,0x4000,bytes.fromhex('320070'));probe_cpu=Simulator(probe)
 probe_cpu.registers[24]=0x4000;probe.recording=True;probe_cpu.run()
 assert probe.cpu_writes==[(0x7000,0)]
 memory=WriteMemory(banks=banks,out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 count=0
 inputs=((a,b,0x16) for a in range(256) for b in range(256))
 from itertools import chain
 for first,second,old in chain(inputs,((0xFF,1,old) for old in range(32))):
  memory.out7ffd(old);memory[0x6306]=old;memory.banks[4][0x2146]=first;memory.banks[4][0x2147]=0xE3;memory.banks[4][0x2148]=second
  put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;trace=PortTrace(sim);sim.set_tracer(trace)
  refresh=first^second;r[15]=refresh
  memory.cpu_writes.clear();memory.recording=True
  sim.run(start=0xAA1D,stop=0x3FFF)
  memory.recording=False;final=(old&0xF8)|0x16
  # Расчёт двух рамок CALL и двух PUSH BC на каждом выборе банка.
  index=(first+second)&255
  expected=[(0x7FFC,0x22),(0x7FFD,0xAA),(0x7FFA,0xC9),(0x7FFB,0x36),
            (0x7FFA,0xC9),(0x7FFB,0x36),(0x6306,(old&0xF8)|0x14),
            (0x7FFC,0x32),(0x7FFD,0xAA),(0x7FFA,index),(0x7FFB,0),
            (0x7FFA,index),(0x7FFB,0),(0x6306,final)]
  assert memory.cpu_writes==expected,(first,second,old,memory.cpu_writes)
  assert r[15]==((refresh&128)|((refresh+37)&127))
  assert memory[0x7FFE:0x8000]==[255,63] or bytes(memory[0x7FFE:0x8000])==bytes([255,63])
  assert (r[A],r[F],r[B],r[C],r[SP])==(final,logical_flags(final),0,(first+second)&255,0x8000)
  assert r[H]*256+r[L]==0x1357 and r[D]*256+r[E]==0x247A and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
  assert trace.writes==[(0x7FFD,(old&0xF8)|0x14),(0x7FFD,final)] and memory[0x6306]==final and memory.o7ffd==final
  count+=1
 report=dict(passed=True,cases=count,method='original_bank4_sum_and_bank6_return',all_byte_pairs=True,all_unlocked_pages=True,
  row_operand_address=0xE146,base_operand_address=0xE148,original_d3d_opcodes=['LD A, n','ADD A, n'],
  high_byte_E147_ignored=True,exact_R_M1=37,exact_CPU_write_sequence_checked=True,
  CPU_write_watch_positive_control=True,original_return_word_preserved=True,
  full_index_components_page_and_R_cartesian_product_checked=False,
  physical_paging_lock_emulation_proved=False,arbitrary_stack_addresses_checked=False,
  stack_bus_cycle_order_verified=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/Bank4IndexVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Полное исходное формирование имени системы, включая обмен наборов регистров."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put
from CheckCompactDecimal import digits


def main():
 _,source,banks=make_context();banks=[bytearray(b) for b in banks]
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x11);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0,'^AF':0x69CF},None,False)
 starts=[];prefixes=[];cursor=0x2722
 for _ in range(16):
  end=source.index(10,cursor);starts.append(cursor+0xC000);prefixes.append(source[cursor:end]);cursor=end+1
 assert cursor==0x2779
 cases=maximum=0
 for prefix in range(16):
  for value in range(256):
   first=(value<<8)|((value*193)&255);second=((value^0xA5)<<8)|((value&0xF0)|prefix);bc=((value*257)^0xA65C)&65535
   memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x11)
   put(memory,0x7FFE,[255,63]);put(memory,0x630A,bytes([0xA7])*23)
   sim.registers[:]=initial;r=sim.registers;r[H],r[L]=first>>8,first&255;r[D],r[E]=second>>8,second&255;r[B],r[C]=bc>>8,bc&255
   n1=(second&0xF0)|((first>>8)&15);n2=((first>>8)&0xF0)|((second>>8)&15);letter=0x80+(second>>12)
   expected=prefixes[prefix]+b'-'+digits(n1)+b'/'+digits(n2)+b'-'+bytes([letter,10])
   sim.run(start=0xE6AB,stop=0x3FFF)
   assert bytes(memory[0x630B:0x630B+len(expected)])==expected and memory[0x630A]==memory[0x630B+len(expected)]==0xA7
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(starts[prefix]+len(prefixes[prefix]),0x630B+len(expected)-1,(n2%100)//10,n2%10,10,0x80|((second>>12)&8),0x8000),(first,second,list(r),expected)
   assert (r[22]*256+r[23],r[20]*256+r[21],r[18]*256+r[19])==(first&0xF0FF,second&0xFFF0,bc)
   assert r[8:12]==initial[8:12] and r[16:18]==initial[16:18];cases+=1;maximum=max(maximum,len(expected))
 report=dict(passed=True,cases=cases,method='original_system_name_prefix_copy_two_compact_numbers_letter_and_LF',
  all_sixteen_prefixes=True,all_byte_values_for_both_numbers=True,zero_alternative_BC_tested=True,
  output_register_set_swapped=True,maximum_output_bytes=maximum,calls_stubbed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SystemNameVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Полный рисователь цели миссии с настоящей рамкой, именем и печатью, HALT пробуждается фикстурой."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckCompactDecimal import digits


def main():
 _,map_source,banks=make_context();banks=[bytearray(b) for b in banks]
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 prefixes=[];cursor=0x2722
 for _ in range(16):end=map_source.index(10,cursor);prefixes.append(map_source[cursor:end]);cursor=end+1
 cases=wakeups=disabled=0
 def prepare(page):
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(page);memory[0x6306]=page
  put(memory,0x8500,bytes([0x80,255])*128);put(memory,0x8600,bytes([0x33])*768);put(memory,0x7FFE,[255,63]);sim.registers[:]=initial
  trace=PortTrace(sim);sim.set_tracer(trace);return sim.registers,trace
 for page in (0x10,0x18):
  for flags in (0,1):
   for value in range(256):
    r,trace=prepare(page);first=(value<<8)|0x38;second=((value^0xA5)<<8)|((value&0xF0)|(value&15))
    put(memory,0xF2ED,[6,10,11,4,flags,4]);put(memory,0x6FC6,[31,0]);put(memory,0x98B0,first.to_bytes(2,'little')+second.to_bytes(2,'little'));memory[0x6F54]=value
    n1=(second&0xF0)|((first>>8)&15);n2=((first>>8)&0xF0)|((second>>8)&15)
    name=prefixes[second&15]+b'-'+digits(n1)+b'/'+digits(n2)+b'-'+bytes([0x80+(second>>12),10])
    r[PC]=0x6FC5;caption_alt=None;wakes=0
    for _ in range(100000):
     if r[PC]==0x3FFF:break
     if r[PC]==0xC089:
      assert memory[r[PC]]==0x76;r[PC]+=1;wakes+=1;continue
     if r[PC]==0x6FCB:caption_alt=tuple(r[16:18])
     sim.opcodes[memory[r[PC]]]()
    else:raise AssertionError(('instruction_limit',page,flags,value,hex(r[PC])))
    assert wakes==1 and bytes(memory[0x630B:0x630B+len(name)])==name and memory[0x6F54]==255
    assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0x630B+len(name),0x630B+len(name)-1,(n2%100)//10,n2%10,10,0x4A,0x8000)
    assert (r[22]*256+r[23],r[20]*256+r[21],r[18]*256+r[19])==(first&0xF0FF,second&0xFFF0,0x36C9)
    assert tuple(r[16:18])==caption_alt and r[8:12]==initial[8:12] and memory[0xBD26]==0
    assert trace.writes==[(0x7FFD,page&0xF8|0x11),(0x7FFD,page)] and memory.o7ffd==page
    assert bytes(memory[0x8500:0x8502])==bytes([31,0]);cases+=1;wakeups+=wakes
 for value in range(256):
  r,trace=prepare(0x10);memory[0x6FC5]=0xC9;memory[0x6F54]=value;sim.run(start=0x6FC5,stop=0x3FFF)
  assert memory[0x6F54]==value and r[:12]==initial[:12] and r[16:24]==initial[16:24] and r[SP]==0x8000 and not trace.writes;disabled+=1
 report=dict(passed=True,cases=cases,disabled_cases=disabled,halt_fixture_wakeups=wakeups,
  method='original_mission_name_draw_caption_system_name_and_print_without_stubs',
  original_caption_executed=True,real_bank_switches=True,alternate_register_result_checked=True,
  actual_irq_wakeup=False,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionNameDrawVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

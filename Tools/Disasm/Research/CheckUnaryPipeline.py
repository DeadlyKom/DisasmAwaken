"""Исходные плюс/минус, диспетчер и все семь унарных обработчиков до NextCommand."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put


def main():
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();banks[6][:len(source)]=source
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FF0,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69A5},None,False)
 cases=0
 def prepare(text):
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x16)
  memory[0x6306]=0x16;put(memory,0xB000,list(text));put(memory,0x7FF0,[255,63]);sim.registers[:]=initial
  trace=PortTrace(sim);sim.set_tracer(trace);return trace
 for entry,mode in ((0xC090,1),(0xC09C,0)):
  for code,base in (('p',0x9A1D),('v',0x9A1E),('m',0x9A32),('e',0x9A41)):
   for number in (0,1,15,255,256,65535):
    text=(code+str(number)).encode()+b'\x00';trace=prepare(text);target=(base+number)&65535;memory[target]=0xA7
    sim.run(start=entry,stop=0xC00C);r=sim.registers
    assert memory[target]==mode and r[A]==mode and r[8]*256+r[9]==0xB000+len(text)-1
    assert r[SP]==0x7FF0 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24] and not trace.writes
    cases+=1
  for code,field in (('K',0x9849),('R',0x984A)):
   for selected in range(256):
    trace=prepare(code.encode()+b'\x00');memory.banks[4][0x2146]=selected;memory.banks[4][0x2148]=73
    sim.run(start=entry,stop=0xC00C);r=sim.registers;expected=(selected+73)&255 if mode else 255
    assert memory[field]==expected and r[A]==expected and r[8]*256+r[9]==0xB001
    assert trace.writes==[(0x7FFD,0x14),(0x7FFD,0x16)] and r[SP]==0x7FF0 and r[18:24]==initial[18:24]
    cases+=1
  trace=prepare(b't1\x00');memory[0x9A1C]=1;memory[0x9A1D]=1;put(memory,0x9A49,[0x31,255,0x32,254,0xA7]);put(memory,0xCF18,list(b'_X1?1!1 payload\r'))
  sim.run(start=entry,stop=0xC00C);r=sim.registers
  assert memory[0x9A4D]==(1 if mode else 0xA7) and r[8]*256+r[9]==(0xB002 if mode else 0xB001)
  assert not trace.writes and r[SP]==0x7FF0 and r[18:24]==initial[18:24]
  cases+=1
 report=dict(passed=True,cases=cases,method='original_two_unary_modes_and_all_seven_handlers_until_next_command',
  zero_resource_mode_leaves_numeric_argument_unconsumed=True,calls_stubbed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/UnaryPipelineVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

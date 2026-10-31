"""Исходная перенесённая копия финального загрузчика до TR-DOS с настоящим MUZ1 и моделью клавиатурного байта."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC,I,IFF,IM
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckGlyphRenderer import compare_flags


class KeyboardTrace(PortTrace):
 def __init__(self,sim,values):super().__init__(sim);self.values=list(values);self.reads=[]
 def read_port(self,registers,port):
  self.reads.append(port);assert port==0x7FFE
  if not self.values:raise AssertionError('Клавиатурная последовательность исчерпана')
  return self.values.pop(0)


def main():
 _,_,banks=make_context();manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==10);music=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();banks[3][0x1B00:0x1B00+len(music)]=list(music)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x2468,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=waiting_reads=0
 for first_byte in range(256):
  for old_page in (0x10,0x18):
   m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=old_page);m[0x6306]=old_page;s=Simulator(m);sequence=[first_byte] if first_byte==0xBE else [first_byte,0xBE];trace=KeyboardTrace(s,sequence);s.set_tracer(trace);copy=bytes(m[0x6E11:0x7011]);put(m,0x4000,copy);s.registers[:]=initial;r=s.registers;r[PC]=0x4000;r[IFF]=1;r[IM]=2
   observed_wait=False
   for _ in range(15000):
    if r[PC]==0x3D13:break
    if r[PC]==0x4024:
     assert m[0xD800:0xDB00]==[1]*768 and m.o7ffd==0x1F and m[0x6306]==((old_page&0xF8)|0x13);observed_wait=True
    s.run()
   else:raise AssertionError(('instruction_limit',first_byte,old_page,hex(r[PC])))
   assert observed_wait and m[0xD800:0xDB00]==[0]*768 and m[0x5CDD:0x5CE6]==list(b'FINALF  C') and m[0x5CF9]==0
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0x4065,0x6000,0,14,0,0x44,0x5FFD)
   assert m[0x5FFD:0x5FFF]==[0,0x60] and r[10]*256+r[11]==0x5C3A and r[I]==0x3F and r[IM]==1 and r[IFF]==0
   assert r[8:10]==initial[8:10] and r[16:24]==initial[16:24] and trace.reads==[0x7FFE]*len(sequence) and not trace.values
   expected=[(0x7FFD,(old_page&0xF8)|0x13)]+[p for reg in range(13,-1,-1) for p in ((0xFFFD,reg),(0xBFFD,0))]+[(0x7FFD,0x1F),(0x01FE,1)]
   assert trace.writes==expected,(first_byte,old_page,trace.writes,expected)
   assert bytes(m[0x4000:0x4200])==copy;cases+=1;waiting_reads+=len(trace.reads)
 report=dict(passed=True,cases=cases,keyboard_reads=waiting_reads,accepted_keyboard_byte=190,all_other_bytes_wait=True,real_music_initializer=True,real_paging_and_attribute_fills=True,relocated_copy_512_bytes_preserved=True,filename=b'FINALF  C'.decode(),stacked_entry=24576,stops_before_trdos=True,disk_load_substituted=False,trdos_executed=False,final_entry_executed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/FinalExitVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

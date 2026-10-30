"""Два исходных CPIR-поиска по FF и FE с нулевым счётчиком как 256 повторений."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP


def main():
 m=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 e=next(e for e in m['entries'] if e['slot']==5);source=(ROOT/(e['path']+'.sectors.bin')).read_bytes()
 memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'IX':0xB000,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0
 for first in range(256):
  for second in (0,1,2,17,127,255):
   for offset in (0,1,5,255,65535):
    n=first or 256;k=second or 256;payload=bytes([0x31,255])*n+bytes([0x32,254])*k
    memory[0x9A49:0x9A49+len(payload)]=payload
    sim.registers[:]=initial;r=sim.registers;r[A]=first;r[B]=second;r[C]=0x75;r[D],r[E]=offset>>8,offset&255
    memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=0xC849,stop=0x3FFF)
    target=(0x9A49+len(payload)-1+offset)&65535
    assert r[H]*256+r[L]==target and r[A]==254 and r[B]==0 and r[C]==0x75 and r[D]*256+r[E]==offset
    assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    assert memory[0xC856]==first and memory[0xC862]==second
    assert r[F]&0xC4==0x44
    cases+=1
 report=dict(passed=True,cases=cases,method='original_two_marker_scan_with_actual_cpir',zero_counts_mean_256=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/DelimitedRecordVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

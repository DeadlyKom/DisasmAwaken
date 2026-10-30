"""Исходный поиск активных соседей с байтовым удвоением индекса таблицы границ."""
from pathlib import Path
import json,sys,random
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckWorldSignature import logical_flags


def reference(memory,index,bounds,values):
 selected=values+index;pair=bounds+((2*index)&255);left=(-memory[pair])&255;right=memory[pair+1]
 for distance in range(1,left+1):
  raw=memory[selected-distance];value=raw if raw<128 else raw^255
  if value:return value,logical_flags(value),selected,(memory[pair]+distance-1)&255,1
 for distance in range(1,right+1):
  raw=memory[selected+distance];value=raw if raw<128 else raw^255
  if value:return value,logical_flags(value),selected+distance,right-distance+1,1
 return 0,0x42,selected+right,0,0


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFA,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 rng=random.Random(0xC520);cases=0
 for entry,bounds,values in ((0xC51A,0x964E,0x988E),(0xC5A9,0x9690,0x98F6),(0xC520,0xA000,0xA500)):
  for case in range(4096):
   index=case&255;leftcode=(case//16)&255;right=(case*73+case//256)&255
   for address in range(values-255,values+511):memory[address]=rng.choice((0,255,0,255,1,128,127,254)) if case%4 else rng.choice((0,255))
   pair=bounds+((2*index)&255);memory[pair]=leftcode;memory[pair+1]=right
   expected=reference(memory,index,bounds,values);sim.registers[:]=initial;r=sim.registers
   if entry==0xC520:r[B],r[C]=bounds>>8,bounds&255;r[D],r[E]=values>>8,values&255
   memory[0x7FFA:0x7FFE]=bytes((index,(case*19)&255,255,63));sim.run(start=entry,stop=0x3FFF)
   value,flags,hl,c,result=expected
   assert (r[A],r[F],r[H]*256+r[L],r[C],r[D],r[E])==(value,flags,hl,c,0,result),(entry,case,expected,list(r))
   assert r[B]==bounds>>8 and r[SP]==0x7FFE and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
   cases+=1
 # Проверка переноса общего входа, при двух нулевых границах OR A не снимает Carry.
 for index in (0,1,255):
  sim.registers[:]=initial;r=sim.registers;r[B]=255;r[C]=255;r[D]=0xA5;r[E]=0
  pair=(0xFFFF+((2*index)&255))&65535;memory[pair]=0;memory[(pair+1)&65535]=0
  memory[0x7FFA:0x7FFE]=bytes((index,0,255,63));sim.run(start=0xC520,stop=0x3FFF)
  assert (r[A],r[F],r[D],r[E],r[H]*256+r[L],r[C],r[SP])==(0,0x42|int(index!=0),0,0,0xA500+index,0,0x7FFE)
  cases+=1
 report=dict(passed=True,cases=cases,method='original_backward_and_forward_active_neighbor_scans',
  all_index_bytes=True,all_left_bound_bytes=True,all_right_bound_bytes=True,double_index_wrap_tested=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ActiveNeighborsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Ограниченное наблюдение заливки, не независимое доказательство алгоритма."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,PC,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckRowHighlight import make_context
from PreviewEdgeRasterOracle import address


def context():
 _,_,banks=make_context();raw=payload(6);m=Memory([0]*65536)
 m[0x4000:0x8000]=banks[5];m[0x8000:0xC000]=banks[2];m[0xC000:0xC000+len(raw)]=raw
 m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0xF0F8,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 s.registers[:]=initial;s.run(start=0x6322,stop=0x3FFF)
 return m,s,initial


def execute(m,s,initial,vertices,mode=0):
 m.recording=False;m[0xC800:0xC800+2*len(vertices)]=[b for row,col in vertices for b in (col,row)]
 m[0xC22B]=2*len(vertices);m[0xC23B]=mode;m[0x7FFE:0x8000]=[255,63]
 s.registers[:]=initial;s.registers[PC]=0xD41B;m.recording=True;m.writes=[];m.rom_write_attempts=[]
 for step in range(100000):
  if s.registers[PC]==0x3FFF:break
  # Поиск попыток LD (BC),A в ROM, симулятор подавляет их до обращения к объекту памяти.
  if m[s.registers[PC]]==0x02:
   pointer=s.registers[2]*256+s.registers[3]
   if pointer<0x4000:m.rom_write_attempts.append((pointer,s.registers[0]))
  s.run()
 else:raise AssertionError(('instruction_limit',vertices,mode,s.registers[PC]))
 assert s.registers[SP]==0x8000
 return step


def main():
 m,s,initial=context();cases=[]
 for vertices in (((2,3),(2,18),(5,18),(5,3)),((2,3),(5,18),(5,3)),((2,3),(3,3),(3,3)),((2,18),(5,18),(5,3))):
  m.recording=False;m[0x4000:0x5800]=[0]*6144;steps=execute(m,s,initial,vertices)
  rows={str(y):[x for x in range(32) if m[address(y,8*x)]] for y in range(8)}
  cases.append(dict(vertices=vertices,steps=steps,bitmap_rows={y:[(x,m[address(int(y),8*x)]) for x in xs] for y,xs in rows.items() if xs},registers=s.registers[:24],writers=sorted(set(p for p,v in m.writes if p>=0xC000))))
 report=dict(observation_only=True,cases=cases,assembly_executed=False,native_execution=False,irq_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewPolygonProbe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

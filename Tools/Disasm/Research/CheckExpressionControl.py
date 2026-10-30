"""Полный числовой путь выражения и скобок на исходных инструкциях языка."""
from pathlib import Path
from itertools import product
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,SP,PC
from CheckMultiplyBranches import reference as multiply
from CheckGlyphRenderer import compare_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FF0,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 ops={'=':lambda x,y:int(x==y),'*':lambda x,y:multiply(x,y)[0],'+':lambda x,y:min(x+y,65535),
  '-':lambda x,y:max(x-y,0),'<':lambda x,y:int(x<y),'>':lambda x,y:int(x>y),
  '[':lambda x,y:int(x<=y),']':lambda x,y:int(x>=y),'&':lambda x,y:x&y,'!':lambda x,y:x|y,':':lambda x,y:y}
 count=nested=0
 def check(body,value,kind):
  sim.registers[:]=initial;r=sim.registers;end=')' if kind=='parenthesis' else ':' if kind=='condition' else '@'
  text=(body+end).encode();memory[0xB000:0xB000+len(text)]=text;memory[0x7FF0:0x7FF2]=bytes([255,63])
  entry,stop,base=(0xC32C,0x3FFF,0xB800) if kind=='parenthesis' else (0xC039,0xC00C,0xCA67)
  r[PC]=entry
  for _ in range(10000):
   if r[PC]==stop:break
   sim.opcodes[memory[r[PC]]]()
  else:raise AssertionError(('limit',body,kind,hex(r[PC])))
  assert memory[base:base+2]==value.to_bytes(2,'little'),(body,kind,value,memory[base:base+2])
  assert r[22]*256+r[23]==base+2 and r[20]*256+r[21]==value and r[D]*256+r[E]==value
  assert r[8]*256+r[9]==0xB000+len(body)+(kind=='parenthesis')
  assert (r[A],r[F])==(ord(end),compare_flags(ord(end),ord(end)))
  assert r[SP]==0x7FF0+(2 if kind=='parenthesis' else 0) and r[10:12]==initial[10:12] and r[16:20]==initial[16:20]
 # Проверка всех операторов для предельных чисел во всех трёх видах завершения.
 for left,right,(symbol,formula),kind in product((0,1,127,255,256,32767,65535),(0,1,127,255,256,32767,65535),ops.items(),('parenthesis','condition','inverse')):
  check(str(left)+symbol+str(right),formula(left,right),kind);count+=1
 # Проверка последовательности вычисления и влияния только явных скобок.
 cases=[('1+2*3',9),('1+(2*3)',7),('(1+2)*3',9),('(1+(2*3))+4',11),
  ('(65535+1)-1',65534),('1:2',2),('258*255+1',255),('(1=1)&(2>1)',1)]
 for body,result in cases:
  for kind in ('parenthesis','condition','inverse'):check(body,result,kind);nested+=1
 check('1:2:3',3,'parenthesis');nested+=1
 report=dict(passed=True,operator_cases=count,nested_and_chain_cases=nested,
  method='original_numeric_readers_dispatch_operators_expression_call_and_control',all_eleven_operators=True,
  evaluation_left_to_right=True,explicit_nested_parentheses=True,calls_stubbed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ExpressionControlVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

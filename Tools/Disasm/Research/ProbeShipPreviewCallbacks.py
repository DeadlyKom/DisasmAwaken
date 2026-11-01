"""Исходные станционные callbacks с настоящими банками и контролируемым IRQ в точках HALT."""
import collections,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from Analyze import payload
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckStationInterrupt import InterruptPorts
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,PC,SP,I,IFF,IM


class Trace(PortTrace):
 def __init__(self,simulator):
  super().__init__(simulator);m=simulator.memory
  self.inputs=InterruptPorts([tuple(m[a:a+2]) for a in range(0x99B6,0x99C2,2)],0,0x5A)
 def read_port(self,registers,port,offset=0):return self.inputs.read_port(registers,port,offset)
 def write_port(self,registers,port,value,offset):
  super().write_port(registers,port,value,offset)
  if port in (0x7FFD,0xFFFD,0xBFFD):self.inputs.write_port(registers,port,value,offset)


class Fixture:
 boot_code=None
 def __init__(self,base,selector=0,model=0,rectangle=(1,1,16,12),page=0x10,flags=0):
  self.memory=m=SliceableMemory(banks=[b.copy() for b in base],out7ffd=page);self.sim=s=Simulator(m);self.trace=Trace(s);s.set_tracer(self.trace)
  # Подготовка настоящей таблицы IM2 и JP 8181 исходными инструкциями загрузчика.
  if Fixture.boot_code is None:
   source=payload(4);flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));code_rows=[]
   for group in flow:
    if group['name']=='StationBoot':
     for instruction in group['instructions']:
      if 0x4196<=instruction['address']<0x41B1:
       code=bytes.fromhex(instruction['hex']);assert code==source[instruction['offset']:instruction['offset']+len(code)];code_rows.append((instruction['address'],code))
   Fixture.boot_code=tuple(code_rows)
  for address,code in Fixture.boot_code:put(m,address,code)
  s.run(start=0x4196,stop=0x41B1);assert m[0x80FF]==m[0x8100]==0x81 and m[0x8181:0x8184]==[0xC3,0xEA,0x9A]
  put(m,0x4000,bytes(6912))
  self.initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
   '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF,'I':0x80},{'iff':1,'im':2},False)
  m[0x6306]=page;put(m,0x6307,(250,190));m[0x6548]=1;m[0x9B16]=1;m[0x9B62]=m[0x99B2]=0;m[0x9B7E]=50;m[0x9B72]=0x5A
  put(m,0x983B,bytes(4));m[0x9A99]=0;put(m,0x9A8D,(255,255));put(m,0x9A90,(0x58,0x9A));put(m,0x9A89,(0x58,0x9A))
  put(m,0x8500,bytes((0x80,255))*128);put(m,0x8600,bytes(768));m[0xBD4F]=0xC3
  for index,rect in ((25,(1,1,24,12)),(26,rectangle),(27,(1,1,24,12))):
   record=0xF0FD+16*index;text=m[record+5];put(m,record,(*rect,flags,text))
  put(m,0x6878,(26,0));put(m,0x67E1,(25,0));put(m,0x6946,(27,0));m[0x6906]=selector;m[0x79DD]=1;m[0x68EB]=0
  m[0x9849]=model if selector==0 else 0;m[0x984A]=model if selector==1 else 0;m.banks[4][0x2146]=model
  # Создание списка в исходной StationState.DrawList, B400 принадлежит исполняемому коду глифа.
  put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,bytes((0xE0,0x67,0x45,0x69,0x77,0x68,1,1)))
  # Проверка сохранности исходного кода глифа после создания списка.
  assert bytes(m[0xB400:0xB408])==bytes(base[2][0x3400:0x3408])
  put(m,0x7FFE,(255,63));s.registers[:]=self.initial;self.wakes=0

 def wake(self,pc):
  s=self.sim;m=self.memory;r=s.registers;assert r[IFF]==1,('halt_iff_zero',hex(pc))
  assert m[0x9B16]==1,('pointer_not_blocked_at_tested_halt',hex(pc))
  before=tuple(r[:28]);page=m.o7ffd;screens=(bytes(m.banks[5][:6912]),bytes(m.banks[7][:6912]));target=pc+1
  # Ожидание реальной временной границы модели HALT, PC изменяет сама исходная инструкция.
  for _ in range(18000):
   s.run()
   if r[PC]==target:break
  else:raise AssertionError(('halt_did_not_wake',hex(pc)))
  assert s.accept_interrupt(r,m,pc) and r[PC]==0x8181
  # Исполнение исходного IM2 без подмены ISR, музыка режимом фикстуры выключена.
  for _ in range(4000):
   if r[PC]==target:break
   assert r[PC]!=0xDB05,'unexpected_music_tick'
   s.run()
  else:raise AssertionError(('irq_did_not_return',hex(pc),hex(r[PC])))
  assert tuple(r[:12])==before[:12] and tuple(r[16:24])==before[16:24] and r[SP]==before[SP] and r[I]==before[I] and r[IM]==2 and r[IFF]==1
  assert m.o7ffd==page and m[0x6306]==page and (bytes(m.banks[5][:6912]),bytes(m.banks[7][:6912]))==screens,(hex(pc),page,m.o7ffd,m[0x6306])
  self.wakes+=1

 def run(self,start,observer=None):
  s=self.sim;m=self.memory;r=s.registers;r[PC]=start;seen=collections.Counter()
  for _ in range(1200000):
   pc=r[PC]
   if pc==0x3FFF:break
   if observer:observer(self,pc)
   if pc in (0x68CC,0x68EA,0x6877,0xE13C,0xE07F,0x67E0,0x6945):seen[format(pc,'04X')]+=1
   if m[pc]==0x76:self.wake(pc)
   else:s.run()
  else:raise AssertionError(('instruction_limit',hex(start),hex(r[PC]),m.o7ffd))
  assert r[SP]==0x8000
  return dict(start=start,wakes=self.wakes,seen=dict(seen),final=list(r[:28]),page=m.o7ffd,callback=m[0x9A89]+256*m[0x9A8A],pending=m[0x68EB])


def main():
 _,_,banks=make_context();raw=payload(6);banks[4][:len(raw)]=list(raw);rows=[]
 for selector,count in ((0,7),(1,4)):
  for model in range(count):
   for rect in ((1,1,16,12),(1,1,2,3)):
    f=Fixture(banks,selector,model,rect);row=f.run(0x6877);row.update(selector=selector,model=model,rectangle=rect);rows.append(row)
 # Периодический кадр использует окно и исходные таблицы, созданные настоящим рисователем.
 f=Fixture(banks);f.run(0x6877);put(f.memory,0x7FFE,(255,63));f.sim.registers[SP]=0x7FFE;f.wakes=0;rows.append(f.run(0x68EA))
 # Отложенный проход рисует список, описание и перемещённую в конец модель.
 f=Fixture(banks);f.memory[0x68EB]=1;f.memory[0x9E78]=0;rows.append(f.run(0x68EA))
 report=dict(observation_only=True,cases=len(rows),real_halt_im2_wake=True,music_disabled=True,irq_only_at_explicit_halts=True,independent_bitmap_oracle=False,
  cases_detail=rows,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShipPreviewCallbacksProbe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='cases_detail'},ensure_ascii=False,indent=2));print('wakes',sum(r['wakes'] for r in rows))


if __name__=='__main__':main()

"""Наблюдение исполняемого кода MUZ1 и его самомодификации без сборки."""
from pathlib import Path
import collections, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from CheckMusic import Simulator, AyPorts, get_registers, PC, SP, word
from InspectZ80 import decoder


class Memory(list):
 def __setitem__(self,key,value):
  # Поиск писателей только в исходном блоке проигрывателя, стек не включается в реестр.
  if isinstance(key,int) and 0xDB00<=key<0xE700 and getattr(self,'recording',False):
   self.writes[key,self.registers[PC]].add(value)
  super().__setitem__(key,value)


def main():
 source=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
 m=Memory([0]*65536);m[0xDB00:0xDB00+len(source)]=source
 s=Simulator(m);s.registers[:]=get_registers({'IY':0x5C3A},None,False)
 ports=AyPorts(source);s.set_tracer(ports);m.registers=s.registers;m.writes=collections.defaultdict(set);m.recording=True
 dis=decoder(list(m));cache={};variants=collections.defaultdict(dict);visits=collections.Counter();edges=collections.Counter()
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));registered={i['address'] for g in flow if g['name']=='Music' for i in g['instructions']}
 frames=[];previous=None;looped=False
 # Исполнение исходной инициализации и кадров до первого возврата списка позиций на петлю.
 for tick in range(-1,12000):
  m[0xBFFE:0xC000]=[255,63];s.registers[SP]=0xBFFE;s.registers[PC]=0xDB00 if tick<0 else 0xDB05;ports.events=[];seen=set()
  for step in range(100000):
   pc=s.registers[PC]
   if pc==0x3FFF:break
   assert 0xDB00<=pc<0xE700,('execution_outside_player',tick,hex(pc))
   key=(pc,bytes(m[pc:pc+4]));instruction=cache.get(key)
   if instruction is None:
    dis.snapshot[pc:pc+4]=list(key[1]);instruction=dis.disassemble(pc,pc+1,'h')[0];cache[key]=instruction
    assert not instruction.operation.startswith('DEFB'),(hex(pc),instruction.operation)
   variants[pc][instruction.bytes.hex()]=instruction.operation;visits[pc]+=1;seen.add(pc)
   s.run()
   if instruction.operation.startswith(('JR ','JP ','CALL ','RET','DJNZ ')):edges[pc,s.registers[PC],instruction.operation]+=1
  else:raise AssertionError(('instruction_limit',tick))
  assert s.registers[SP]==0xC000 and s.registers[10]*256+s.registers[11]==0x5C3A
  if tick<0:previous=word(m,0xDF98);continue
  position=word(m,0xDF98)
  if tick%512==0:print('Music tick',tick,'observed PCs',len(visits),flush=True)
  frames.append({'tick':tick,'instructions':step,'unique_pcs':len(seen),'ay_writes':len(ports.events)})
  if position<previous:
   assert position==word(m,0xDF9F)+1;looped=True;break
  previous=position
 assert looped
 # Разделение наблюдавшихся новых начал инструкций и вариантов самомодификации.
 missing=sorted(set(visits)-registered)
 report={'passed':True,'method':'original_initialized_music_until_first_position_loop','ticks':tick+1,
  'source_sha256':hashlib.sha256(source).hexdigest(),'position_loop_reached':True,'unique_executed_pcs':len(visits),
  'unregistered_executed_pcs':[f'{p:04X}' for p in missing],
  'instructions':[{'address':p,'visits':visits[p],'variants':variants[p],'registered':p in registered} for p in sorted(visits)],
  'writes':[{'address':a,'writer':p,'values':sorted(v)} for (a,p),v in sorted(m.writes.items())],
  'edges':[{'source':a,'target':b,'operation':op,'count':count} for (a,b,op),count in sorted(edges.items())],
  'frames':frames,'independent_audio_oracle':False,'native_execution':False,'irq_executed':False,
  'all_possible_module_commands_proved':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicRuntimeFlow.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k not in ('instructions','writes','edges','frames')},indent=2),flush=True)


if __name__=='__main__':main()

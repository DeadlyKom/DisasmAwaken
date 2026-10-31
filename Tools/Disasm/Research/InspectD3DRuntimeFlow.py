"""Наблюдение исходных кадров D3D, косвенных потоков и самомодификации без IRQ и сборки."""
from pathlib import Path
import json,sys,hashlib,collections
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,PC,SP
from CheckRowHighlight import make_context
from Analyze import payload,analyze
from InspectZ80 import decoder


class WatchedMemory(list):
 def __setitem__(self,key,value):
  # Поиск писателей только в исходном окне D3D, экран не раздувает реестр.
  if isinstance(key,int) and 0xC000<=key<0xFE6A and getattr(self,'recording',False):
   self.writers[key,self.registers[PC]].add(value)
  super().__setitem__(key,value)


def main():
 _,_,banks=make_context();station=payload(4);raw=payload(6);original=bytearray(65536);original[0xC000:0xC000+len(raw)]=raw;dis=decoder(original);original_dis=decoder(original);cache={};decoded={};variants=collections.defaultdict(set);edges=collections.Counter();all_writers=collections.defaultdict(set);cases=[];roots=(0xE07F,0xE0B5,0xE0C5,0xE124,0xE13C,0xE154);static=analyze('D3D',extra_roots=roots,initial_bank=4);static_addresses={i['address'] for i in static['instructions']}
 for selector,count in ((0,7),(1,4)):
  for model in range(count):
   m=WatchedMemory([0]*65536);m[0x4000:0x8000]=banks[5];m[0x8000:0xC000]=banks[2];m[0xC000:0xC000+len(raw)]=raw;m[0x4000:0x42B5]=station[0x319:0x5CE];s=Simulator(m);s.run(start=0x40E0,stop=0x4107);m[0x4000:0x6000]=[0]*8192
   initial=get_registers({'SP':0x7FFE,'HL':0x8C50,'DE':0,'BC':0x36C9,'AF':0x005D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0,'^BC':0x58BE,'^AF':0x69CF},None,False);s.registers[:]=initial;s.registers[0]=selector;m[0xE146]=model;m[0x7FFE:0x8000]=[255,63];s.run(start=0xE13C,stop=0x3FFF);m.registers=s.registers;m.writers=collections.defaultdict(set)
   # Наблюдение нескольких последовательных кадров сохраняет предыдущие углы и переписанные заголовки граней.
   for frame in range(4):
    s.registers[SP]=0x7FFE;s.registers[0]=selector;s.registers[PC]=0xE07F;m.recording=True;visited=set();indirect_count=0
    for step in range(500000):
     pc=s.registers[PC]
     if pc==0x3FFF:break
     assert m[pc]!=0x76,('unexpected_halt',selector,model,frame,pc)
     operation=None
     if 0xC000<=pc<0xFE6A:
      key=(pc,bytes(m[pc:pc+4]));instruction=cache.get(key)
      if instruction is None:
       dis.snapshot[pc:pc+4]=list(key[1]);instruction=dis.disassemble(pc,pc+1,'h')[0];cache[key]=instruction
      operation=instruction.operation;assert not operation.startswith('DEFB'),(pc,operation);variants[pc].add(instruction.bytes);visited.add(pc)
      if pc not in decoded:decoded[pc]=original_dis.disassemble(pc,pc+1,'h')[0]
     s.run()
     # Поиск реальных целей непрямого JP и RET, включая возвраты на адреса продолжений в индексных регистрах.
     if operation in ('JP (HL)','JP (IX)','JP (IY)','RET'):
      edges[pc,s.registers[PC],operation]+=1;indirect_count+=1
    else:raise AssertionError(('instruction_limit',selector,model,frame))
    assert s.registers[SP]==0x8000
    cases.append(dict(selector=selector,model=model,frame=frame,instructions=step,unique_bank4_pcs=len(visited),indirect_transfers=indirect_count,returned=True))
   for key,values in m.writers.items():all_writers[key].update(values)
 # Проверка, может ли статический декодер принять наблюдавшиеся начала инструкций без перекрытия.
 observed=set(decoded);expanded=analyze('D3D',extra_roots=roots,observed=observed,initial_bank=4);expanded_by_address={i['address']:i for i in expanded['instructions']};mismatches=[];changed=[]
 for pc,instruction in sorted(decoded.items()):
  if pc not in expanded_by_address or expanded_by_address[pc]['hex']!=instruction.bytes.hex():mismatches.append(pc)
  live=variants[pc]
  if live!={instruction.bytes}:
   changes=sorted({pc+j for blob in live for j,value in enumerate(blob) if j>=len(instruction.bytes) or value!=instruction.bytes[j]})
   changed.append(dict(address=pc,original_hex=instruction.bytes.hex(),original_operation=instruction.operation,runtime_variants=[b.hex() for b in sorted(live)],changed_addresses=changes,opcode_changed=any(b[0]!=instruction.bytes[0] for b in live),length_changed=any(len(b)!=len(instruction.bytes) for b in live)))
 # Проверка связи уже оформленных исходников с расширенной разведкой, без подмены её корней самим реестром инструкций.
 source_flow=next(g for g in json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8')) if g['name']=='D3D')
 source_missing=[i['address'] for i in source_flow['instructions'] if i['address'] not in expanded_by_address or expanded_by_address[i['address']]['hex']!=i['hex']]
 report=dict(method='observed_original_d3d_frames_and_indirect_edges_without_irq',all_cases_returned=all(c['returned'] for c in cases),cases=cases,sector_sha256=hashlib.sha256(raw).hexdigest(),static_baseline_instruction_count=static['instruction_count'],static_baseline_code_bytes=static['code_bytes'],unique_observed_instructions=len(observed),observed_missing_from_static=sorted(observed-static_addresses),expanded_instruction_count=expanded['instruction_count'],expanded_code_bytes=expanded['code_bytes'],expanded_overlaps=expanded['overlaps'],observed_original_decode_mismatches=mismatches,registered_source_instructions=len(source_flow['instructions']),registered_source_missing_from_expanded=source_missing,changed_original_instructions=changed,indirect_edges=[dict(address=a,target=t,operation=o,count=n) for (a,t,o),n in sorted(edges.items())],bank4_writers=[dict(address=a,writer=pc,values=sorted(values)) for (a,pc),values in sorted(all_writers.items())],independent_bitmap_oracle=False,irq_executed=False,native_execution=False,assembly_executed=False,source_map_modified=False,full_semantic_analysis_complete=False)
 (ROOT/'Tools/Disasm/Reports/D3DRuntimeFlow.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:report[k] for k in ('all_cases_returned','unique_observed_instructions','expanded_instruction_count','expanded_code_bytes','expanded_overlaps','observed_original_decode_mismatches')},indent=2));print('cases',len(cases),'missing_static',len(report['observed_missing_from_static']),'changed_instructions',len(changed),'indirect_edges',len(edges))


if __name__=='__main__':main()

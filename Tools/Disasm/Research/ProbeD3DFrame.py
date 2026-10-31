"""Ограниченный исходный кадр D3D для наблюдения записей, без независимого оракула всего рисунка."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,PC,SP
from CheckRowHighlight import make_context
from Analyze import payload
from PreviewFaceFillFacts import HEADERS


class Memory(list):
 def __getitem__(self,key):
  value=super().__getitem__(key)
  if isinstance(key,int) and getattr(self,'recording',False) and key in self.targets:
   pair=(key,self.registers[PC])
   if pair not in self.read_keys:self.read_keys.add(pair);self.reads.append(dict(address=key,pc=self.registers[PC],value=value))
  return value
 def __setitem__(self,key,value):
  if isinstance(key,int) and getattr(self,'recording',False) and 0xF000<=key<0xF580:self.writes.append(dict(address=key,pc=self.registers[PC],before=list.__getitem__(self,key),after=value))
  super().__setitem__(key,value)


def run_case(selector,row):
 _,_,banks=make_context();station=payload(4);raw=payload(6);m=Memory([0]*65536);m[0x4000:0x8000]=banks[5];m[0x8000:0xC000]=banks[2];m[0xC000:0xC000+len(raw)]=list(raw)
 # Исполнение только точного исходного участка инициализации матрицы, без дисковых вызовов загрузчика.
 m[0x4000:0x42B5]=list(station[0x319:0x5CE]);s=Simulator(m);s.run(start=0x40E0,stop=0x4107);m[0x4000:0x6000]=[0]*8192
 # Подготовка фиксированной геометрии и выбранной исходной модели через настоящий SetupPreviewModel.
 initial=get_registers({'SP':0x7FFE,'HL':0x8C50,'DE':0,'BC':0x36C9,'AF':0x005D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0,'^BC':0x58BE,'^AF':0x69CF},None,False);s.registers[:]=initial;s.registers[0]=selector;m[0xE146]=row;m[0x7FFE:0x8000]=[255,63];s.run(start=0xE13C,stop=0x3FFF)
 s.registers[SP]=0x7FFE;s.registers[0]=selector;s.registers[PC]=0xE07F;m.registers=s.registers;m.writes=[];m.reads=[];m.read_keys=set();m.targets=set(HEADERS);m.recording=True;visited={};helper_snapshot=None;halt=None
 for count in range(500000):
  pc=s.registers[PC]
  if pc==0x3FFF:break
  if pc==0x6364:helper_snapshot={str(a):list.__getitem__(m,a) for a in (0xF0F0,0xF2B7)}
  if m[pc]==0x76:halt=pc;break
  if pc not in visited:visited[pc]=bytes(m[pc:pc+4]).hex()
  s.run()
 else:count=500000
 completed=s.registers[PC]==0x3FFF
 report=dict(method='limited_original_d3d_frame_without_irq',selector=selector,row=row,completed=completed,instructions=count,final_pc=s.registers[PC],final_sp=s.registers[SP],unique_pcs=len(visited),helper_6364_seed_bytes_before_call=helper_snapshot,writes_F000_F57F=m.writes,reads_helper_targets=m.reads,halt_address=halt,matrix_original_snippet_executed=True,real_setup_and_render_core=True,framebuffer_independent_oracle=False,irq_executed=False,native_execution=False,assembly_executed=False)
 return report


def main():
 cases=[run_case(selector,row) for selector,count in ((0,7),(1,4)) for row in range(count)]
 consumed={r['address'] for c in cases for r in c['reads_helper_targets'] if r['pc'] in (0xDBE9,0xDD4F)}
 assert consumed==set(HEADERS) and all(c['completed'] for c in cases)
 report=dict(all_13_headers_consumed_by_face_parsers=True,method='eleven_original_preview_models_without_irq_or_independent_bitmap_oracle',all_cases_returned=all(c['completed'] for c in cases),cases=cases,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/D3DFrameProbe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for case in cases:print(case['selector'],case['row'],'returned',case['completed'],'instructions',case['instructions'],'watched_reads',len(case['reads_helper_targets']))



if __name__=='__main__':main()

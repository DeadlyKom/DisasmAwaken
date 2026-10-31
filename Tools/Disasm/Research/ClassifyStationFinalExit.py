"""Выделение доказанного 92-байтового финального загрузчика и девяти байтов имени, без сборки."""
from pathlib import Path
import collections,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze
from FinalExitFacts import FUNCTIONS,CONTRACTS,COMMENTS,LABELS
from FinalFileKeyTable import render,PATH as KEY_PATH
from SemanticNames import name_operands,documentation_links
from SourcePresentation import format_function,instructions
from VerifySources import structure_symbols,main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/StationFinalExitScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeStationFinalExitCode'


def main():
 verify();assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('FinalExitVerification')['passed'];flow=analyze('StationFinalExit');assert flow['code_bytes']==92 and flow['instruction_count']==38 and not flow['overlaps']
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==4);raw=(ROOT/(e['path']+'.sectors.bin')).read_bytes()
 assert raw[0x10BD:0x1119]==b''.join(bytes.fromhex(i['hex']) for i in flow['instructions'])
 original=ROOT/'Source/Resources/04_STATIONF/Unclassified023.bin';assert original.read_bytes()==raw[0x10BD:0x1122]
 name,description=FUNCTIONS[0x4000];contract=CONTRACTS['StationFinalExit',0x4000];lines=['                module StationFinalExit','                module '+name,*documentation_links('StationFinalExit',0x4000),'; -----------------------------------------','; '+description,'; исходная запись 4, физическое хранение 6E11, исполнение 4000, файловые смещения #10BD..#1118']
 for heading,values in zip(('In','Out','Corrupt','Note'),contract):lines+=['; '+heading+':']+[';   '+v for v in values]
 lines+=['; -----------------------------------------'];symbols={};path='Source/StationFinalExit/'+name+'.asm'
 for item in flow['instructions']:
  address=item['address'];above,right=COMMENTS.get(address,([],None));lines+=['                ; '+v for v in above];label='Entry' if address==0x4000 else LABELS.get(('StationFinalExit',address),'')
  if label:symbols['StationFinalExit.'+name+'.'+label]=address
  op=name_operands('StationFinalExit',0x4000,item['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
  if right:assert len(line)<80;line=line.ljust(80)+'; '+right
  lines.append(line)
 lines+=['                ; -----------------------------------------','                endmodule','                endmodule'];code=format_function('\n'.join(lines)+'\n');key,key_symbols=render(raw);symbols.update(key_symbols)
 assert len(instructions(code))==38 and structure_symbols()['FTRDOSFILEKEY']==9
 pending={ROOT/path:code,ROOT/KEY_PATH:key}
 source_map=read('SourceMap');index=next(i for i,v in enumerate(source_map) if v['slot']==4 and v['offset']==0x10BD);old=source_map[index];assert old['length']==101 and old['path']==original.relative_to(ROOT).as_posix()
 source_map[index:index+1]=[dict(slot=4,offset=begin,length=end-begin,kind=kind,path=file,origin=origin,sha256=hashlib.sha256(raw[begin:end]).hexdigest()) for begin,end,kind,file,origin in ((0x10BD,0x1119,'code',path,0x4000),(0x1119,0x1122,'typed_data',KEY_PATH,0x405C))]
 functions=read('Functions');functions.append(dict(region='StationFinalExit',name=name,address=0x4000,slot=4,offset=0x10BD,end_offset=0x1119,description=description,semantic_status='described',path=path));cf=read('ControlFlow');assert not any(g['name']=='StationFinalExit' for g in cf);cf.append(flow)
 sy=read('Symbols');assert not set(symbols)&set(sy);sy.update(symbols);inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(g['instruction_count'] for g in cf));inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for filename,value in (('SourceMap',source_map),('Functions',functions),('ControlFlow',cf),('Symbols',sy),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+filename+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Source/Files/04_STATIONF.inc';text=p.read_text('utf-8');needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/04_STATIONF/Unclassified023.bin"';assert text.count(needle)==1
 replacement='                ; исходные байты 6E11..6E75, исполнение загрузчика после переноса в 4000\n                disp #4000\n                include "../StationFinalExit/LoadFinal.asm"\n                ent\n                assert $ == #1119\n                disp #405C\n                include "../StationFinalExit/Data/FinalFileName.asm"\n                ent';pending[p]=text.replace(needle,replacement,1)
 p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');needle='| StationExit | 1 | 1 | [Факты](FunctionDetails/StationExit.md) |';assert needle in text;pending[p]=text.replace(needle,needle+'\n| StationFinalExit | 1 | 1 | [Факты](FunctionDetails/StationFinalExit.md) |',1)+'\n| #4000 | [StationFinalExit.LoadFinal](../Source/StationFinalExit/LoadFinal.asm) | '+description+' |\n'
 p=ROOT/'Docs/FunctionDetails/StationFinalExit.md';assert not p.exists();pending[p]='# Финальный выход станции в контексте 4000\n\n[LoadFinal](../../Source/StationFinalExit/LoadFinal.asm) хранится физически в STATIONF по 6E11, выполняется после исходного переноса в 4000. Подробный договор и границы модели приведены в [FinalExit](../FinalExit.md).\n'
 plan=[]
 for p,text in pending.items():
  rel=p.relative_to(ROOT);data=text.encode('utf-8');target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,p.read_bytes() if p.exists() else None,data))
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists();assert (CANDIDATE/rel).read_bytes()==data
 # Сохранение только затрагиваемых файлов и исходного бинарного фрагмента, копия всего проекта не создаётся.
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 verify()
 # Удаление единственного бинарного дубликата только после проверки новой физической разметки и резервной копии.
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/04_STATIONF') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,instructions=38,code_bytes=92,typed_filename_bytes=9,original_physical_bytes_preserved=True,stored_address=28177,execution_address=16384,method='scoped_candidate_original_bytes_control_flow_and_full_source_map_verification',assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StationFinalExitClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report))


if __name__=='__main__':main()

"""Точечное выделение умножителя D3D EB10 с кандидатом, историей и сохранением байтов."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze,payload
from PreviewMultiplyFacts import FUNCTIONS,CONTRACTS,COMMENTS,LABELS,name_operands
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PreviewMultiplyScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePreviewMultiply'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewCoordinateMultiplyVerification')['passed'];raw=payload(6);g=analyze('D3D');flow=read('ControlFlow');previous=next(v for v in flow if v['name']=='D3D');old={i['address'] for i in previous['instructions']};added=[i for i in g['instructions'] if i['address'] not in old]
 assert not g['overlaps'] and all(i in g['instructions'] for i in previous['instructions'])
 assert b''.join(bytes.fromhex(i['hex']) for i in added)==raw[0x2B10:0x2B7E] and all(0xEB10<=i['address']<0xEB7E for i in added)
 validate_notes([g],{'D3D':COMMENTS})
 name,description=FUNCTIONS[0xEB10];path='Source/D3D/'+name+'.asm';lines=['                module D3D','                module '+name,'                ; Документация [переходный умножитель координаты](../../Docs/PreviewCoordinateMultiply.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #2B10..#2B7D']
 for title,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',0xEB10]):lines+=['                ; '+title+':']+['                ;   '+value for value in values]
 lines+=['                ; -----------------------------------------'];pending={};binaries={};symbols=read('Symbols');functions=read('Functions')
 for j,i in enumerate(added):
  above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];label='Entry' if j==0 else LABELS.get(('D3D',i['address']),'')
  if label:
   symbol='D3D.'+name+'.'+label;assert symbol not in symbols;symbols[symbol]=i['address']
  op=name_operands('D3D',0xEB10,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
  if right:assert len(line)<80;line=line.ljust(80)+'; '+right
  lines.append(line)
 lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n')
 functions.append(dict(region='D3D',name=name,address=0xEB10,slot=6,offset=0x2B10,end_offset=0x2B7E,path=path,description=description,semantic_status='described'))
 source_map=read('SourceMap');old_range=next(e for e in source_map if e['path']=='Source/Resources/06_D3D/BeforeDescriptionText.bin');original=ROOT/old_range['path'];assert original.read_bytes()==raw[old_range['offset']:old_range['offset']+old_range['length']]
 ranges=((old_range['offset'],0x2B10,'unclassified','Source/Resources/06_D3D/BeforeCoordinateMultiply.bin',None),(0x2B10,0x2B7E,'code',path,0xEB10),(0x2B7E,old_range['offset']+old_range['length'],'unclassified','Source/Resources/06_D3D/AfterCoordinateMultiply.bin',None));mapped=[];include_lines=[];position=old_range['offset']
 for start,end,kind,target,origin in ranges:
  assert start==position and start<end;position=end;blob=raw[start:end];mapped.append(dict(old_range,offset=start,length=end-start,kind=kind,path=target,origin=origin,sha256=hashlib.sha256(blob).hexdigest()))
  if kind=='unclassified':binaries[ROOT/target]=blob;include_lines.append('                incbin "../Resources/06_D3D/'+Path(target).name+'"')
  else:include_lines+=['                disp #EB10','                include "../D3D/'+name+'.asm"','                ent']
  include_lines.append('                assert $ == #'+format(end,'04X'))
 idx=source_map.index(old_range);source_map[idx:idx+1]=mapped
 p=ROOT/'Source/Files/06_D3D.inc';t=p.read_text('utf-8');needle='                incbin "../Resources/06_D3D/BeforeDescriptionText.bin"';assert t.count(needle)==1;pending[p]=t.replace(needle,'\n'.join(include_lines))
 flow[flow.index(previous)]=g;inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow));inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for report,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+report+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');assert '| D3D | 6 | 6 |' in t;t=t.replace('| D3D | 6 | 6 |','| D3D | 7 | 7 |');pending[p]=t+'\n| #EB10, банк 4 | [D3D.'+name+'](../'+path+') | '+description+' |\n'
 p=ROOT/'Docs/FunctionDetails/D3D.md';pending[p]=p.read_text('utf-8')+'\n['+name+'](../../'+path+') — см. [PreviewCoordinateMultiply](../PreviewCoordinateMultiply.md).\n'
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module PreviewMultiplyState' not in t;pending[p]=t.replace('                endif\n','                module PreviewMultiplyState\n'+('ReturnTarget    equ #EB7C'.ljust(80)+'; два байта изменяемого JP умножителя, адрес продолжения из входного DE\n')+'                endmodule\n\n                endif\n')
 plan=[]
 # Создание отдельного кандидата без замены текущих файлов до проверки их исходного состояния.
 for p,value in {**pending,**binaries}.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление только заменённого бинарного дубликата после проверки активных байтов и точной сохранённой копии.
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,instructions=len(added),code_bytes=110,bank=4,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewMultiplyClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

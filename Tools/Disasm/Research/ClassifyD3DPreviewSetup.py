"""Точечное выделение 24 исходных байтов подготовки просмотра D3D с отдельным кандидатом."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze,payload
from D3DSetupFacts import FUNCTIONS,CONTRACTS,COMMENTS,LABELS,name_operands
from SourcePresentation import format_function
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/D3DPreviewSetupScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeD3DPreviewSetup'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 assert read('PreviewSetupVerification')['passed'];g=analyze('D3D');raw=payload(6);rows=[i for i in g['instructions'] if 0xE13C<=i['address']<0xE154];assert sum(len(bytes.fromhex(i['hex'])) for i in rows)==24 and not g['overlaps']
 assert b''.join(bytes.fromhex(i['hex']) for i in rows)==raw[0x213C:0x2154]
 original=ROOT/'Source/Resources/06_D3D/AfterPreviewThird.bin';assert original.read_bytes()==raw[0x20C5:]
 name,description=FUNCTIONS[0xE13C];path='Source/D3D/'+name+'.asm';lines=['                module D3D','                module '+name,'                ; Документация [подготовка просмотра](../../Docs/PreviewSetup.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #213C..#2153']
 for heading,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',0xE13C]):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
 lines+=['                ; -----------------------------------------']
 for j,i in enumerate(rows):
  above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];op=name_operands('D3D',0xE13C,i['operation'].replace(',',', '));label='Entry' if j==0 else LABELS.get(('D3D',i['address']),'');line=((label+':').ljust(16) if label else ' '*16)+op;lines.append(line.ljust(80)+'; '+right if right else line)
 lines+=['                endmodule','                endmodule'];pending={ROOT/path:format_function('\n'.join(lines)+'\n')}
 resources=(('BeforePreviewSetup.bin',0x20C5,0x213C),('AfterPreviewSetup.bin',0x2154,len(raw)));binaries={ROOT/('Source/Resources/06_D3D/'+filename):raw[start:end] for filename,start,end in resources}
 source_map=read('SourceMap');old=next(e for e in source_map if e['path']==original.relative_to(ROOT).as_posix());assert old['path']==original.relative_to(ROOT).as_posix() and old['length']==len(raw)-0x20C5;parts=[]
 for start,end,kind,p,origin in ((0x20C5,0x213C,'unclassified','Source/Resources/06_D3D/BeforePreviewSetup.bin',None),(0x213C,0x2154,'code',path,0xE13C),(0x2154,len(raw),'unclassified','Source/Resources/06_D3D/AfterPreviewSetup.bin',None)):
  parts.append(dict(old,offset=start,length=end-start,kind=kind,path=p,origin=origin,sha256=hashlib.sha256(raw[start:end]).hexdigest()))
 index=source_map.index(old);source_map[index:index+1]=parts;functions=read('Functions');functions.append(dict(region='D3D',name=name,address=0xE13C,slot=6,offset=0x213C,end_offset=0x2154,path=path,description=description,semantic_status='described'));symbols=read('Symbols');assert 'D3D.SetupPreviewModel.Entry' not in symbols;symbols['D3D.SetupPreviewModel.Entry']=0xE13C;symbols['D3D.SetupPreviewModel.StoreOffset']=0xE150;flow=read('ControlFlow');index=next(i for i,v in enumerate(flow) if v['name']=='D3D');assert all(i in g['instructions'] for i in flow[index]['instructions']);flow[index]=g
 inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow));inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for filename,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+filename+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Source/Files/06_D3D.inc';text=p.read_text('utf-8');needle='                incbin "../Resources/06_D3D/AfterPreviewThird.bin"';assert text.count(needle)==1;pending[p]=text.replace(needle,'                incbin "../Resources/06_D3D/BeforePreviewSetup.bin"\n                assert $ == #213C\n                disp #E13C\n                include "../D3D/SetupPreviewModel.asm"\n                ent\n                assert $ == #2154\n                incbin "../Resources/06_D3D/AfterPreviewSetup.bin"')
 p=ROOT/'Includes/Variables/Include.inc';text=p.read_text('utf-8');start=text.index('                module D3DPreviewState');end=text.index('                endmodule',start);block=''
 for name,value,desc in (('ModelOffset',0xCDC6,'байтовое смещение модели в исходной записи просмотра'),('RowOperand',0xE146,'изменяемый операнд LD A с компонентом строки'),('BaseOperand',0xE148,'изменяемый операнд ADD A со смещением списка')):block+=(name.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+desc+'\n'
 assert 'ModelOffset' not in text[start:end];pending[p]=text[:end]+block+text[end:]
 p=ROOT/'Includes/Const/Include.inc';text=p.read_text('utf-8');start=text.index('                module D3DPreviewConst');end=text.index('                endmodule',start);assert 'SpecialBase' not in text[start:end];pending[p]=text[:end]+('SpecialBase     equ #1C').ljust(80)+'; добавка смещения модели только при исходном селекторе 1\n'+text[end:]
 p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');assert '| D3D | 2 | 2 |' in text;pending[p]=text.replace('| D3D | 2 | 2 |','| D3D | 3 | 3 |')+'\n| #E13C, банк 4 | [D3D.SetupPreviewModel](../Source/D3D/SetupPreviewModel.asm) | '+description+' |\n'
 p=ROOT/'Docs/FunctionDetails/D3D.md';pending[p]=p.read_text('utf-8')+'\n[SetupPreviewModel](../../Source/D3D/SetupPreviewModel.asm) — композиция границ, таблиц и смещения модели, см. [PreviewSetup](../PreviewSetup.md).\n'
 p=ROOT/'Source/Station/DrawItem26.asm';pending[p]=p.read_text('utf-8').replace('CALL #E13C','CALL @D3D.SetupPreviewModel.Entry')
 plan=[]
 # Запись отдельного кандидата и проверка актуальности файлов до замены рабочей копии.
 for p,value in {**pending,**binaries}.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists();assert (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление заменённого бинарного дубликата только после сверки исходных байтов и сохранённой копии.
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,instructions=len(rows),code_bytes=24,bank=4,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/D3DPreviewSetupClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

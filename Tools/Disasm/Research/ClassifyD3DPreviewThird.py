"""Точечное выделение 16 исходных байтов изменения третьей координаты D3D с отдельным кандидатом."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze,payload
from D3DThirdFacts import FUNCTIONS,CONTRACTS,COMMENTS,name_operands
from SourcePresentation import format_function
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/D3DPreviewThirdScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeD3DPreviewThird'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 assert read('PreviewThirdVerification')['passed'];g=analyze('D3D');raw=payload(6);rows=[i for i in g['instructions'] if 0xE0B5<=i['address']<0xE0C5];assert sum(len(bytes.fromhex(i['hex'])) for i in rows)==16 and not g['overlaps']
 assert b''.join(bytes.fromhex(i['hex']) for i in rows)==raw[0x20B5:0x20C5]
 original=ROOT/'Source/Resources/06_D3D/AfterPreviewClip.bin';assert original.read_bytes()==raw[0x207F:]
 name,description=FUNCTIONS[0xE0B5];path='Source/D3D/'+name+'.asm';lines=['                module D3D','                module '+name,'                ; Документация [третья координата просмотра](../../Docs/PreviewThird.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #20B5..#20C4']
 for heading,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',0xE0B5]):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
 lines+=['                ; -----------------------------------------']
 for j,i in enumerate(rows):
  above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];op=name_operands('D3D',0xE0B5,i['operation'].replace(',',', '));line=('Entry:'.ljust(16) if j==0 else ' '*16)+op;lines.append(line.ljust(80)+'; '+right if right else line)
 lines+=['                endmodule','                endmodule'];pending={ROOT/path:format_function('\n'.join(lines)+'\n')}
 resources=(('BeforePreviewThird.bin',0x207F,0x20B5),('AfterPreviewThird.bin',0x20C5,len(raw)));binaries={ROOT/('Source/Resources/06_D3D/'+filename):raw[start:end] for filename,start,end in resources}
 source_map=read('SourceMap');old=next(e for e in source_map if e['path']==original.relative_to(ROOT).as_posix());assert old['path']==original.relative_to(ROOT).as_posix() and old['length']==len(raw)-0x207F;parts=[]
 for start,end,kind,p,origin in ((0x207F,0x20B5,'unclassified','Source/Resources/06_D3D/BeforePreviewThird.bin',None),(0x20B5,0x20C5,'code',path,0xE0B5),(0x20C5,len(raw),'unclassified','Source/Resources/06_D3D/AfterPreviewThird.bin',None)):
  parts.append(dict(old,offset=start,length=end-start,kind=kind,path=p,origin=origin,sha256=hashlib.sha256(raw[start:end]).hexdigest()))
 index=source_map.index(old);source_map[index:index+1]=parts;functions=read('Functions');functions.append(dict(region='D3D',name=name,address=0xE0B5,slot=6,offset=0x20B5,end_offset=0x20C5,path=path,description=description,semantic_status='described'));symbols=read('Symbols');assert 'D3D.AdjustPreviewThird.Entry' not in symbols;symbols['D3D.AdjustPreviewThird.Entry']=0xE0B5;flow=read('ControlFlow');index=next(i for i,v in enumerate(flow) if v['name']=='D3D');assert all(i in g['instructions'] for i in flow[index]['instructions']);flow[index]=g
 inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow));inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for filename,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+filename+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Source/Files/06_D3D.inc';text=p.read_text('utf-8');needle='                incbin "../Resources/06_D3D/AfterPreviewClip.bin"';assert text.count(needle)==1;pending[p]=text.replace(needle,'                incbin "../Resources/06_D3D/BeforePreviewThird.bin"\n                assert $ == #20B5\n                disp #E0B5\n                include "../D3D/AdjustPreviewThird.asm"\n                ent\n                assert $ == #20C5\n                incbin "../Resources/06_D3D/AfterPreviewThird.bin"')
 p=ROOT/'Includes/Variables/Include.inc';text=p.read_text('utf-8');block='                module D3DPreviewState\n'+('ThirdCoordinate equ #CDC4').ljust(80)+'; третье слово позиции записи, единицы ещё не установлены\n                endmodule\n\n';assert 'module D3DPreviewState' not in text;pending[p]=text.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Includes/Const/Include.inc';text=p.read_text('utf-8');block='                module D3DPreviewConst\n'+('ThirdMinHigh    equ #02').ljust(80)+'; минимальный старший байт принятой суммы, 512\n'+('ThirdEndHigh    equ #10').ljust(80)+'; исключённый верхний старший байт, 4096\n                endmodule\n\n';assert 'module D3DPreviewConst' not in text;pending[p]=text.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');assert '| D3D | 1 | 1 |' in text;pending[p]=text.replace('| D3D | 1 | 1 |','| D3D | 2 | 2 |')+'\n| #E0B5, банк 4 | [D3D.AdjustPreviewThird](../Source/D3D/AdjustPreviewThird.asm) | '+description+' |\n'
 p=ROOT/'Docs/FunctionDetails/D3D.md';pending[p]=p.read_text('utf-8')+'\n[AdjustPreviewThird](../../Source/D3D/AdjustPreviewThird.asm) — ограниченное изменение третьей координаты, см. [PreviewThird](../PreviewThird.md).\n'
 p=ROOT/'Source/Station/Unknown683A.asm';pending[p]=p.read_text('utf-8').replace('CALL #E0B5','CALL @D3D.AdjustPreviewThird.Entry')
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
 report=dict(passed=True,instructions=len(rows),code_bytes=16,bank=4,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/D3DPreviewThirdClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Точечное выделение 110 исходных байтов настройки границ D3D с отдельным кандидатом."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze,payload
from D3DClipFacts import FUNCTIONS,CONTRACTS,COMMENTS,PATCHES,name_operands
from SourcePresentation import format_function
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/D3DPreviewClipScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeD3DPreviewClip'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 assert read('PreviewClipBoundsVerification')['passed'];g=analyze('D3D');raw=payload(6);assert g['code_bytes']==110 and not g['overlaps']
 assert b''.join(bytes.fromhex(i['hex']) for i in g['instructions'])==raw[0x2011:0x207F]
 original=ROOT/'Source/Resources/06_D3D/Unclassified000.bin';assert original.read_bytes()==raw
 name,description=FUNCTIONS[0xE011];path='Source/D3D/'+name+'.asm';lines=['                module D3D','                module '+name,'                ; Документация [границы просмотра](../../Docs/PreviewClipBounds.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #2011..#207E']
 for heading,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',0xE011]):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
 lines+=['                ; -----------------------------------------']
 for j,i in enumerate(g['instructions']):
  above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];op=name_operands('D3D',0xE011,i['operation'].replace(',',', '));line=('Entry:'.ljust(16) if j==0 else ' '*16)+op;lines.append(line.ljust(80)+'; '+right if right else line)
 lines+=['                endmodule','                endmodule'];pending={ROOT/path:format_function('\n'.join(lines)+'\n')}
 resources=(('BeforePreviewClip.bin',0,0x2011),('AfterPreviewClip.bin',0x207F,len(raw)));binaries={ROOT/('Source/Resources/06_D3D/'+filename):raw[start:end] for filename,start,end in resources}
 source_map=read('SourceMap');old=next(e for e in source_map if e['slot']==6);assert old['path']==original.relative_to(ROOT).as_posix() and old['length']==len(raw);parts=[]
 for start,end,kind,p,origin in ((0,0x2011,'unclassified','Source/Resources/06_D3D/BeforePreviewClip.bin',None),(0x2011,0x207F,'code',path,0xE011),(0x207F,len(raw),'unclassified','Source/Resources/06_D3D/AfterPreviewClip.bin',None)):
  parts.append(dict(old,offset=start,length=end-start,kind=kind,path=p,origin=origin,sha256=hashlib.sha256(raw[start:end]).hexdigest()))
 index=source_map.index(old);source_map[index:index+1]=parts;functions=read('Functions');functions.append(dict(region='D3D',name=name,address=0xE011,slot=6,offset=0x2011,end_offset=0x207F,path=path,description=description,semantic_status='described'));symbols=read('Symbols');assert 'D3D.ConfigurePreviewClip.Entry' not in symbols;symbols['D3D.ConfigurePreviewClip.Entry']=0xE011;flow=read('ControlFlow');assert not any(v['name']=='D3D' for v in flow);flow.append(g)
 inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow));inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for filename,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+filename+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Source/Files/06_D3D.inc';s=p.read_text('utf-8');needle='                incbin "../Resources/06_D3D/Unclassified000.bin"';assert s.count(needle)==1;pending[p]=s.replace(needle,'                incbin "../Resources/06_D3D/BeforePreviewClip.bin"\n                assert $ == #2011\n                disp #E011\n                include "../D3D/ConfigurePreviewClip.asm"\n                ent\n                assert $ == #207F\n                incbin "../Resources/06_D3D/AfterPreviewClip.bin"')
 p=ROOT/'Includes/Variables/Include.inc';s=p.read_text('utf-8');block='                module D3DClipState\n'
 for address,label in PATCHES.items():
  desc='существующее слово угла, старший X и младший Y' if label in ('MaxCorner','MinCorner','MaxXMinY','MinXMaxY') else 'существующий байтовый операнд границы, соседний байт сохраняется';block+=(label.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+desc+'\n'
 assert 'module D3DClipState' not in s;pending[p]=s.replace('                endif\n',block+'                endmodule\n\n                endif\n')
 p=ROOT/'Docs/Functions.md';s=p.read_text('utf-8');needle='| Text | 126 | 126 | [Факты](FunctionDetails/Text.md) |';assert needle in s;pending[p]=s.replace(needle,needle+'\n| D3D | 1 | 1 | [Факты](FunctionDetails/D3D.md) |')+'\n| #E011, банк 4 | [D3D.ConfigurePreviewClip](../Source/D3D/ConfigurePreviewClip.asm) | '+description+' |\n'
 pending[ROOT/'Docs/FunctionDetails/D3D.md']='# D3D, банк 4\n\n[ConfigurePreviewClip](../../Source/D3D/ConfigurePreviewClip.asm) — настройка операндов границ по #E011. Полный договор и модель приведены в [PreviewClipBounds](../PreviewClipBounds.md). Остальной банк ещё не выделен и не разобран полностью.\n'
 plan=[]
 # Запись отдельного кандидата и проверка актуальности файлов до замены рабочей копии.
 for p,value in {**pending,**binaries}.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists();assert (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление заменённого бинарного дубликата только после сверки исходных байтов и сохранённой копии.
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,instructions=g['instruction_count'],code_bytes=110,bank=4,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/D3DPreviewClipClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

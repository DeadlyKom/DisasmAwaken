"""Точечное оформление существующего рабочего блока, относительные пути и сохранение байтов."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from PreviewDrawStateTable import TABLE,FIELDS,render
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PreviewDrawStateScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePreviewDrawState'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 raw=payload(6);pending={};text,labels=render(raw,TABLE);symbols=read('Symbols');assert not symbols.keys()&labels.keys();symbols.update(labels);pending[ROOT/TABLE[1]]=text
 source_map=read('SourceMap');old_path='Source/Resources/06_D3D/BeforeModelPointers.bin';original=ROOT/old_path;old=next(e for e in source_map if e['path']==old_path)
 assert (old['offset'],old['length'])==(0xEFA,0x106) and original.read_bytes()==raw[0xEFA:0x1000]
 # Проверка, что типизированная запись и оставшийся хвост смежно покрывают прежний диапазон.
 mapped=[dict(old,offset=0xEFA,length=10,kind='typed_data',path=TABLE[1],origin=0xCEFA,sha256=hashlib.sha256(raw[0xEFA:0xF04]).hexdigest()),dict(old,offset=0xF04,length=0xFC,kind='unclassified',path='Source/Resources/06_D3D/AfterDrawState.bin',origin=None,sha256=hashlib.sha256(raw[0xF04:0x1000]).hexdigest())]
 idx=source_map.index(old);source_map[idx:idx+1]=mapped;pending[ROOT/mapped[1]['path']]=raw[0xF04:0x1000]
 p=ROOT/'Source/Files/06_D3D.inc';t=p.read_text('utf-8');needle='                incbin "../Resources/06_D3D/BeforeModelPointers.bin"';assert t.count(needle)==1
 replacement='\n'.join(('                disp #CEFA','                include "../D3D/Data/PreviewDrawState.asm"','                ent','                assert $ == #0F04','                incbin "../Resources/06_D3D/AfterDrawState.bin"'));pending[p]=t.replace(needle,replacement)
 p=ROOT/'Includes/Structs/Include.inc';t=p.read_text('utf-8');assert 'struct FPreviewDrawState' not in t;block='                ; Документация [рабочий блок очереди](../../Docs/PreviewQueueBuild.md)\n                struct FPreviewDrawState\n'
 for field,width,meaning in FIELDS:block+=(field.ljust(16)+('db #00' if width==1 else 'dw #0000')).ljust(80)+'; '+meaning+'\n'
 block+='                ends\n                assert FPreviewDrawState == #0A\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Source/D3D/ComposePreviewMatrix.asm';t=p.read_text('utf-8');assert t.count('(IY+#00)')==8;pending[p]=t.replace('(IY+#00)','(IY+@FPreviewDrawState.Flags)')
 p=ROOT/'Tools/Disasm/Research/PreviewMatrixComposeFacts.py';t=p.read_text('utf-8');needle=".replace('BIT 0, (IY+#00)','BIT @PreviewModelMatrixConst.OneAxisBit, (IY+#00)')";assert needle in t;pending[p]=t.replace(needle,".replace('BIT 0, (IY+#00)','BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)')")
 # Подключение той же физической схемы к проверке и будущему экспорту, экспорт здесь не запускается.
 p=ROOT/'Tools/Disasm/VerifySources.py';t=p.read_text('utf-8');needle='    preview_scene_records = {}\n    for module,path,start,end,structure,fields,names in PREVIEW_SCENE_TABLES:';assert needle in t
 pending[p]=t.replace(needle,"    from PreviewDrawStateTable import TABLE as PREVIEW_DRAW_STATE_TABLE\n    preview_scene_records = {}\n    for module,path,start,end,structure,fields,names in (*PREVIEW_SCENE_TABLES, PREVIEW_DRAW_STATE_TABLE):")
 p=ROOT/'Tools/Disasm/Research/ExportSources.py';t=p.read_text('utf-8');needle='    from PreviewSceneTables import TABLES as PREVIEW_SCENE_TABLES, render as render_preview_scene';assert needle in t;t=t.replace(needle,needle+'\n    from PreviewDrawStateTable import TABLE as PREVIEW_DRAW_STATE_TABLE')
 needle='    for table in PREVIEW_SCENE_TABLES:';assert t.count(needle)==1;pending[p]=t.replace(needle,'    for table in (*PREVIEW_SCENE_TABLES, PREVIEW_DRAW_STATE_TABLE):')
 inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for report,value in (('Symbols',symbols),('SourceMap',source_map),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+report+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Docs/PreviewQueueBuild.md';t=p.read_text('utf-8');needle='| [PreviewModelPointers]';position=t.index('\n',t.index(needle));t=t[:position]+'\n| [PreviewDrawState](../Source/D3D/Data/PreviewDrawState.asm) | #CEFA..#CF03 | Один FPreviewDrawState, 10 исходных рабочих байтов |'+t[position:]
 t+='\n## Физический рабочий блок\n\nFPreviewDrawState сохраняет исходные 10 байтов #CEFA..#CF03, без нового размещения. Его поля включают Flags, ModelOffset, RawFirst, RawSecond, RawThird, Head и NextFree. Дисковые инициализаторы сохранены точно. Перед обходом реальный код отдельно устанавливает Head=1 и NextFree=0, дисковый нуль головы не заменяется единицей.\n\nСхема Flags, разряды 7..0: [SecondKey, ?, ?, ?, ?, ?, ?, OneAxis]. Маски известных разрядов равны #80 и #01. В разобранном построителе биты 6..1 всегда нулевые, их возможный смысл в других путях не установлен. Нулевой Flags выбирает общую матрицу и сравнение по ThirdResult, бит 7 независимо выбирает SecondInput при сравнении узлов. Это два независимых признака, не числовой код режима.\n\nОдноосный потребитель держит IY=#CEFA и использует физическое поле FPreviewDrawState.Flags со смещением 0. Имеющиеся адресные имена PreviewQueueState и PreviewQueueBuildState остаются совместимыми ссылками на те же байты. Проверка VerifySources сверяет размер, смещения и все исходные инициализаторы.\n';pending[p]=t
 plan=[]
 # Создание отдельного кандидата и проверка, что рабочие файлы не изменились во время подготовки.
 for p,value in pending.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 # Проверка новой схемы должна загрузить обновлённый модуль VerifySources в этом же процессе.
 import importlib,VerifySources
 with contextlib.redirect_stdout(io.StringIO()):importlib.reload(VerifySources).main()
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,typed_bytes=10,physical_struct_fields=len(FIELDS),named_index_fields=8,original_bytes_preserved=True,scoped_candidate_and_history=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewDrawStateClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

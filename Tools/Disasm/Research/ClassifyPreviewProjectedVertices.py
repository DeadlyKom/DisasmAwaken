"""Физическая типизация исходного буфера C600 без изменения рабочих адресов и начальных значений."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from PreviewProjectedVertexTable import PATH,FIELDS,render
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 candidate=ROOT/'Tools/Disasm/Research/Candidates/PreviewProjectedVerticesScoped';history=ROOT/'Tools/Disasm/Research/History/BeforePreviewProjectedVertices'
 assert not candidate.exists() and not history.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewVertexClassVerification')['passed'];raw=payload(6);text,labels=render(raw);pending={ROOT/PATH:text};symbols=read('Symbols');assert not symbols.keys()&labels.keys();symbols.update(labels)
 p=ROOT/'Includes/Structs/Include.inc';text=p.read_text('utf-8');assert 'struct FPreviewProjectedVertex' not in text;block='                ; Документация [пятибайтовая запись проекции](../../Docs/PreviewVertexClass.md)\n                struct FPreviewProjectedVertex\n'
 for field,width,meaning in FIELDS:block+=(field.ljust(16)+('dw #0000' if width==2 else 'db #00')).ljust(80)+'; '+meaning+'\n'
 block+='                ends\n                assert FPreviewProjectedVertex == #05\n\n';pending[p]=text.replace('                endif\n',block+'                endif\n')
 source_map=read('SourceMap');old_path='Source/Resources/06_D3D/AfterSquareTable.bin';original=ROOT/old_path;old=next(v for v in source_map if v['path']==old_path)
 assert (old['offset'],old['length'])==(0x400,0x300) and original.read_bytes()==raw[0x400:0x700]
 target='Source/Resources/06_D3D/BeforeProjectedVertices.bin';pending[ROOT/target]=raw[0x400:0x600]
 mapped=[dict(old,offset=0x400,length=0x200,path=target,sha256=hashlib.sha256(raw[0x400:0x600]).hexdigest()),dict(old,offset=0x600,length=0x100,kind='typed_data',path=PATH,origin=0xC600,sha256=hashlib.sha256(raw[0x600:0x700]).hexdigest())]
 idx=source_map.index(old);source_map[idx:idx+1]=mapped
 p=ROOT/'Source/Files/06_D3D.inc';text=p.read_text('utf-8');needle='                incbin "../Resources/06_D3D/AfterSquareTable.bin"';assert text.count(needle)==1
 pending[p]=text.replace(needle,'\n'.join(('                incbin "../Resources/06_D3D/BeforeProjectedVertices.bin"','                assert $ == #0600','                disp #C600','                include "../D3D/Data/PreviewProjectedVertices.asm"','                ent')))
 p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    # Проверка исходных DB свёрнутых квадратов';assert text.count(needle)==1
 check="""    # Проверка физических пятибайтовых записей и хвоста исходной страницы проекции.
    from PreviewProjectedVertexTable import PATH as PROJECTED_PATH, FIELDS as PROJECTED_FIELDS, parse as parse_projected
    preview_projected_vertices = 0
    projected_entries = [item for item in source_map if item['path'] == PROJECTED_PATH]
    if projected_entries:
        if len(projected_entries) != 1:
            raise ValueError('Неоднозначный буфер проекции')
        item = projected_entries[0]
        if (item['slot'],item['offset'],item['length'],item['origin']) != (6,0x600,256,0xC600):
            raise ValueError('Изменилось размещение исходного буфера проекции')
        raw, labels = parse_projected((ROOT/PROJECTED_PATH).read_text('utf-8'))
        if raw != sources[6][0x600:0x700] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились байты или метки исходного буфера проекции')
        offset = 0
        for field,width,meaning in PROJECTED_FIELDS:
            if symbols.get('FPREVIEWPROJECTEDVERTEX.'+field.upper()) != offset:
                raise ValueError('Изменилось поле пятибайтовой записи')
            offset += width
        if symbols.get('FPREVIEWPROJECTEDVERTEX') != 5:
            raise ValueError('Изменился размер пятибайтовой записи')
        preview_projected_vertices = 51

"""
 text=text.replace(needle,check+needle);needle="    report['preview_model_group_records'] = preview_model_records";assert needle in text;pending[p]=text.replace(needle,needle+"\n    report['preview_projected_vertices'] = preview_projected_vertices")
 p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle='    # Исходная страница свёрнутых квадратов';assert text.count(needle)==1
 block="""    # Исходный рабочий буфер проекции, экспорт на этапе исследования не запускается.
    from PreviewProjectedVertexTable import PATH as PROJECTED_PATH, render as render_projected
    text, labels = render_projected(data_by_slot[6])
    write(PROJECTED_PATH, text)
    symbols.update(labels)
    special[6,0x600] = (0x700,PROJECTED_PATH,0xC600)
"""
 pending[p]=text.replace(needle,block+needle)
 p=ROOT/'Docs/PreviewVertexClass.md';pending[p]=p.read_text('utf-8')+'\nБуфер [PreviewProjectedVertices.asm](../Source/D3D/Data/PreviewProjectedVertices.asm) сохраняет исходные 256 байтов страницы C6. Он содержит 51 физический FPreviewProjectedVertex с полями SecondAxis, FirstAxis, Outcode и отдельный TailByte по #C6FF. Начальные коды сохраняются из образа, значение #F0 не подставляется вместо исходных байтов. Декларация физической ёмкости не заменяет ограничения штатного прохода, подтверждённые модели имеют не больше 32 вершин.\n'
 inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 plan=[]
 for p,value in pending.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 # Проверка текущих файлов до применения отдельного кандидата.
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (candidate/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=history/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 import importlib,VerifySources
 with contextlib.redirect_stdout(io.StringIO()):importlib.reload(VerifySources).main()
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(history/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,typed_bytes=256,records=51,record_size=5,tail_bytes=1,original_initial_values_preserved=True,scoped_candidate_and_history=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewProjectedVerticesClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

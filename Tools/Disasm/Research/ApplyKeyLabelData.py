"""Одноразовая типизация ровно двенадцати байтов трёх клавишных обозначений."""
from pathlib import Path
import collections,contextlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from KeyLabelFacts import TABLE
from PreviewSceneTables import render
from Analyze import payload
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('KeyLabelVerification')['passed'];candidate=ROOT/'Tools/Disasm/Research/Candidates/KeyLabelDataScoped';history=ROOT/'Tools/Disasm/Research/History/BeforeKeyLabelData';assert not candidate.exists() and not history.exists()
 source=payload(4);module,path,start,end,structure,fields,names=TABLE;source_map=read('SourceMap');entry=next(e for e in source_map if e['slot']==4 and e['offset']==start);oldpath=ROOT/entry['path'];raw=oldpath.read_bytes();assert entry['length']==12 and raw==source[start:end]
 text,labels=render(source,TABLE,0x6000);text=text.replace('подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','три клавишных обозначения](../../../Docs/KeyLabels.md)');pending={ROOT/path:text.encode('utf-8')}
 entry.update(kind='typed_data',path=path,origin=0xBE1B);pending[ROOT/'Tools/Disasm/Reports/SourceMap.json']=encode(source_map)
 symbols=read('Symbols');assert not any(k in symbols for k in labels);symbols.update(labels);pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=encode(symbols)
 p=ROOT/'Includes/Structs/Include.inc';t=p.read_text('utf-8');block='                ; Документация [обозначения клавиш](../../Docs/KeyLabels.md)\n                struct FKeyAbbreviation\n'
 for name,width,meaning in fields:block+=(name.ljust(16)+'db #00').ljust(80)+'; '+meaning+'\n'
 block+='                ends\n                assert FKeyAbbreviation == #04\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n').encode('utf-8')
 p=ROOT/'Source/Files/04_STATIONF.inc';t=p.read_text('utf-8');needle='                incbin "../Resources/04_STATIONF/EventGap5E1B.bin"';assert t.count(needle)==1
 pending[p]=t.replace(needle,'                disp #BE1B\n                include "../Station/Data/KeyAbbreviations.asm"\n                ent').replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                ; Unknown, сохранённые байты вне новых доказанных входов\n                disp #BE1B','                ; три исходные четырёхсимвольные клавишные подписи\n                disp #BE1B').encode('utf-8')
 inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(e['length'] for e in source_map if e['kind']==kind) for kind in inventory['physical_bytes_by_kind']};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encode(inventory)
 p=ROOT/'Tools/Disasm/VerifySources.py';t=p.read_text('utf-8');needle='    # Проверка реальных структур, меток и каждого исходного байта префиксов моделей.';assert t.count(needle)==1
 check='''    # Проверка трёх физических четырёхбайтовых обозначений клавиш в фиксированном банке 2.
    from KeyLabelFacts import TABLE as KEY_LABEL_TABLE
    module,path,start,end,structure,fields,names = KEY_LABEL_TABLE
    entries = [item for item in source_map if item['path'] == path]
    if len(entries) != 1 or (entries[0]['slot'],entries[0]['offset'],entries[0]['length'],entries[0]['origin']) != (4,start,end-start,0x6000+start):
        raise ValueError('Изменилось размещение клавишных обозначений')
    raw,labels = parse_preview_scene((ROOT/path).read_text('utf-8'), KEY_LABEL_TABLE, 0x6000)
    if raw != sources[4][start:end] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
        raise ValueError('Изменились клавишные обозначения либо их поля')
    if symbols.get(structure.upper()) != 4 or any(symbols.get(structure.upper()+'.'+field.upper()) != index for index,(field,_,_) in enumerate(fields)):
        raise ValueError('Изменилась структура клавишного обозначения')

''';pending[p]=t.replace(needle,check+needle).replace("    report['preview_scene_records'] = preview_scene_records","    report['key_abbreviation_records'] = 3\n    report['help_line_cache_records'] = 1024\n    report['preview_scene_records'] = preview_scene_records").encode('utf-8')
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);old=p.read_bytes() if p.exists() else None;plan.append((rel,old,data));target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,old,data in plan:assert (ROOT/rel).read_bytes()==old if old is not None else not (ROOT/rel).exists()
 for rel,old,data in plan:
  if old is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old)
 target=history/oldpath.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 for rel,old,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert oldpath.read_bytes()==raw==(history/oldpath.relative_to(ROOT)).read_bytes();oldpath.unlink()
 report=dict(passed=True,physical_records=3,typed_bytes=12,original_bytes_preserved=True,fields_and_symbols_checked=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/KeyLabelDataClassification.json').write_bytes(encode(report));print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

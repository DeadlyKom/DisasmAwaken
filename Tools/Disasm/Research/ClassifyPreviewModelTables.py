"""Типизация доказанных префиксов моделей, все промежутки граней сохраняются отдельно."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from PreviewModelGroupTables import tables,render,STRUCTURES
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PreviewModelTablesScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePreviewModelTables'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewModelWalkVerification')['passed'];raw=payload(6);models=tables(raw);assert len(models)==10 and sum(len(m['groups']) for m in models)==62
 pending={};symbols=read('Symbols')
 for model in models:
  text,labels=render(raw,model);assert not symbols.keys()&labels.keys();symbols.update(labels);pending[ROOT/model['path']]=text
 p=ROOT/'Includes/Structs/Include.inc';text=p.read_text('utf-8');block='                ; Документация [заголовки и физические группы](../../Docs/PreviewModelGroups.md)\n'
 for name,fields in STRUCTURES:
  assert 'struct '+name not in text;block+='                struct '+name+'\n'
  for field,width,meaning in fields:block+=(field.ljust(16)+'db #00').ljust(80)+'; '+meaning+'\n'
  block+='                ends\n                assert '+name+' == #'+format(sum(width for field,width,meaning in fields),'02X')+'\n\n'
 pending[p]=text.replace('                endif\n',block+'                endif\n')
 source_map=read('SourceMap');old_path='Source/Resources/06_D3D/AfterModelMatrix.bin';original=ROOT/old_path;old=next(e for e in source_map if e['path']==old_path)
 assert original.read_bytes()==raw[old['offset']:old['offset']+old['length']]
 mapped=[];include=[];position=old['offset'];end=position+old['length']
 # Проверка непересекающихся префиксов с сохранением каждой оставшейся области данных граней.
 for index,model in enumerate(models):
  assert model['start']==position;blob=raw[position:model['end']]
  mapped.append(dict(old,offset=position,length=len(blob),kind='typed_data',path=model['path'],origin=0xC000+position,sha256=hashlib.sha256(blob).hexdigest()))
  include+=['                disp #'+format(0xC000+position,'04X'),'                include "../D3D/Data/ModelGroups/'+model['name']+'.asm"','                ent','                assert $ == #'+format(model['end'],'04X')]
  next_start=models[index+1]['start'] if index+1<len(models) else end;position=model['end'];assert position<next_start
  target='Source/Resources/06_D3D/After'+model['name']+'Groups.bin';blob=raw[position:next_start];pending[ROOT/target]=blob
  mapped.append(dict(old,offset=position,length=len(blob),kind='unclassified',path=target,origin=None,sha256=hashlib.sha256(blob).hexdigest()))
  include+=['                incbin "../Resources/06_D3D/'+Path(target).name+'"','                assert $ == #'+format(next_start,'04X')];position=next_start
 assert position==end;idx=source_map.index(old);source_map[idx:idx+1]=mapped
 p=ROOT/'Source/Files/06_D3D.inc';text=p.read_text('utf-8');needle='                incbin "../Resources/06_D3D/AfterModelMatrix.bin"';assert text.count(needle)==1;pending[p]=text.replace(needle,'\n'.join(include))
 p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    # Проверка исходных DB свёрнутых квадратов';assert text.count(needle)==1
 check="""    # Проверка реальных структур, меток и каждого исходного байта префиксов моделей.
    from PreviewModelGroupTables import tables as preview_model_tables, parse as parse_preview_model, STRUCTURES as PREVIEW_MODEL_STRUCTURES
    preview_model_records = {}
    for model in preview_model_tables(sources[6]):
        entries = [item for item in source_map if item['path'] == model['path']]
        if not entries:
            continue
        if len(entries) != 1:
            raise ValueError('Неоднозначная регистрация групп модели')
        item = entries[0]
        if (item['slot'], item['offset'], item['length'], item['origin']) != (6, model['start'], model['end']-model['start'], model['pointer']):
            raise ValueError('Изменилось физическое размещение групп модели')
        raw, labels = parse_preview_model((ROOT/model['path']).read_text('utf-8'), model)
        if raw != sources[6][model['start']:model['end']] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились исходные байты или метки групп модели')
        preview_model_records[model['name']] = len(model['groups'])
    if preview_model_records:
        for structure,fields in PREVIEW_MODEL_STRUCTURES:
            offset = 0
            for field,width,meaning in fields:
                if symbols.get(structure.upper()+'.'+field.upper()) != offset:
                    raise ValueError('Изменилось поле структуры модели')
                offset += width
            if symbols.get(structure.upper()) != offset:
                raise ValueError('Изменился размер структуры модели')

"""
 text=text.replace(needle,check+needle);needle="    report['preview_scene_records'] = preview_scene_records";assert needle in text;pending[p]=text.replace(needle,needle+"\n    report['preview_model_group_records'] = preview_model_records")
 p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle='    # Исходная страница свёрнутых квадратов';assert text.count(needle)==1
 block="""    # Исходные заголовки и группы моделей, ручной экспорт здесь не запускается.
    from PreviewModelGroupTables import tables as preview_model_tables, render as render_preview_model
    for model in preview_model_tables(data_by_slot[6]):
        text, labels = render_preview_model(data_by_slot[6], model)
        write(model['path'], text)
        symbols.update(labels)
        special[6, model['start']] = (model['end'], model['path'], model['pointer'])
"""
 pending[p]=text.replace(needle,block+needle)
 p=ROOT/'Docs/PreviewModelGroups.md';text=p.read_text('utf-8')
 for model in models:
  address='#'+format(model['pointer'],'04X');name='Dominion и Karen' if model['name']=='Dominion' else model['name'];needle='| '+address+' | '+name+' |';assert text.count(needle)==1
  text=text.replace(needle,'| '+address+' | ['+name+'](../'+model['path']+') |')
 text+='\nПрефиксы оформлены физическими FPreviewModelHeader и FPreviewVertexGroup, всего 278 исходных байтов, 10 заголовков, 62 группы и 10 отдельных DB #00. У каждого значения указано его поле. Размеры структур равны 2 и 4, смещения и все инициализаторы проверяет VerifySources. Все промежутки после ограничителей сохранены бинарно до дальнейшего разбора граней.\n';pending[p]=text
 inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 plan=[]
 # Создание кандидата с проверкой текущей рабочей копии перед заменой.
 for p,value in pending.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 import importlib,VerifySources
 with contextlib.redirect_stdout(io.StringIO()):importlib.reload(VerifySources).main()
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,typed_bytes=sum(m['end']-m['start'] for m in models),headers=len(models),groups=sum(len(m['groups']) for m in models),single_byte_terminators=len(models),structures=2,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewModelTablesClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

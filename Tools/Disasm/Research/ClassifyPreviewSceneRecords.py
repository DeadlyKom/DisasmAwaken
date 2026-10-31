"""Общее точечное выделение физических записей D3D, со снимком кандидата и сверкой всех байтов."""
from pathlib import Path
import collections,contextlib,hashlib,importlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from VerifySources import main as verify,structure_symbols


def apply(facts,tag,replacements,verification,document):
 with contextlib.redirect_stdout(io.StringIO()):verify()
 candidate=ROOT/('Tools/Disasm/Research/Candidates/'+tag+'Scoped');history=ROOT/('Tools/Disasm/Research/History/Before'+tag)
 assert not candidate.exists() and not history.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read(verification)['passed'];raw=payload(6);pending={};symbols=read('Symbols');source_map=read('SourceMap')
 # Создание отдельных текстовых кандидатов физических записей, существующие символы не заменяются.
 for table in facts.TABLES:
  text,labels=facts.render(raw,table);assert not symbols.keys()&labels.keys();symbols.update(labels);pending[ROOT/table[1]]=text
 p=ROOT/'Includes/Structs/Include.inc';text=p.read_text('utf-8');block='                ; Документация [физические записи](../../Docs/'+document+'.md)\n';declared=set();known=structure_symbols();reused=set()
 for module,path,start,end,structure,fields,names in facts.TABLES:
  # Повторное использование структуры разрешено только после сверки фактического размера и всех смещений полей.
  if structure.upper() in known:
   assert known[structure.upper()]==sum(width for _,width,_ in fields);offset=0
   for field,width,_ in fields:assert known[(structure+'.'+field).upper()]==offset;offset+=width
   reused.add(structure);continue
  assert structure not in declared;declared.add(structure);block+='                struct '+structure+'\n'
  for field,width,meaning in fields:block+=(field.ljust(16)+('dw #0000' if width==2 else 'db #00')).ljust(80)+'; '+meaning+'\n'
  block+='                ends\n                assert '+structure+' == #'+format(sum(width for _,width,_ in fields),'02X')+'\n\n'
  # Следующий физический экземпляр той же новой структуры переиспользует это объявление.
  known[structure.upper()]=sum(width for _,width,_ in fields);offset=0
  for field,width,_ in fields:known[(structure+'.'+field).upper()]=offset;offset+=width
 assert text.count('                endif\n')==1
 if declared:pending[p]=text.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Source/Files/06_D3D.inc';include=p.read_text('utf-8');originals=[]
 # Проверка смежного покрытия каждого явно указанного исходного бинарного диапазона.
 for old_path,parts in replacements:
  old=next(v for v in source_map if v['path']==old_path);original=ROOT/old_path;originals.append(original)
  assert original.read_bytes()==raw[old['offset']:old['offset']+old['length']];mapped=[];rows=[];position=old['offset']
  for start,end,kind,target in parts:
   assert start==position and start<end;position=end;blob=raw[start:end]
   mapped.append(dict(old,offset=start,length=end-start,kind=kind,path=target,origin=0xC000+start if kind=='typed_data' else None,sha256=hashlib.sha256(blob).hexdigest()))
   if kind=='typed_data':
    assert ROOT/target in pending;rows+=['                disp #'+format(0xC000+start,'04X'),'                include "../D3D/Data/'+Path(target).name+'"','                ent']
   else:assert kind=='unclassified';pending[ROOT/target]=blob;rows.append('                incbin "../Resources/06_D3D/'+Path(target).name+'"')
   rows.append('                assert $ == #'+format(end,'04X'))
  assert position==old['offset']+old['length'];index=source_map.index(old);source_map[index:index+1]=mapped
  needle='                incbin "../Resources/06_D3D/'+original.name+'"';assert include.count(needle)==1;include=include.replace(needle,'\n'.join(rows))
 pending[p]=include
 # Подключение этих же полей к статическому проверяющему парсеру и неисполняемому массовому экспортёру.
 p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    preview_scene_records = {}';assert text.count(needle)==1
 text=text.replace(needle,'    from '+facts.__name__+' import TABLES as '+tag.upper()+'_TABLES\n'+needle)
 needle=next(line for line in text.splitlines() if line.startswith('    for module,path,start,end,structure,fields,names in (*PREVIEW_SCENE_TABLES,'));assert text.count(needle)==1
 pending[p]=text.replace(needle,needle[:-2]+', *'+tag.upper()+'_TABLES):')
 p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle=next(line for line in text.splitlines() if line.startswith('    for table in (*PREVIEW_SCENE_TABLES,'));assert text.count(needle)==1
 text=text.replace(needle,'    from '+facts.__name__+' import TABLES as '+tag.upper()+'_TABLES, render as render_'+tag.lower()+'\n'+needle[:-2]+', *'+tag.upper()+'_TABLES):')
 needle=next(line for line in text.splitlines() if 'text, labels = (' in line and 'render_preview_scene' in line and '(data_by_slot[6], table)' in line);assert text.count(needle)==1
 prefix,expression=needle.split(' = ',1);assert expression.startswith('(')
 pending[p]=text.replace(needle,prefix+' = (render_'+tag.lower()+' if table in '+tag.upper()+'_TABLES else '+expression[1:])
 inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 plan=[]
 # Сохранение кандидата до изменения рабочей копии и контроль неизменности текущих файлов.
 for p,value in pending.items():
  assert p.resolve().is_relative_to(ROOT);data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None
  target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (candidate/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 for original in originals:target=history/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 import VerifySources
 with contextlib.redirect_stdout(io.StringIO()):importlib.reload(VerifySources).main()
 # Удаление только заменённых бинарных файлов после сверки с их единственным точным снимком этого этапа.
 for original in originals:
  assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(history/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,typed_bytes=sum(t[3]-t[2] for t in facts.TABLES),physical_structures=len({t[4] for t in facts.TABLES}),newly_declared_structures=sorted(declared),reused_structures=sorted(reused),physical_records=sum(len(t[6]) for t in facts.TABLES),original_initial_values_preserved=True,scoped_candidate_and_history=True,assembly_executed=False)
 (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))

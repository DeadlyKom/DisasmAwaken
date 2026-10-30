"""Точечный кандидат новых EventHandler+3 и их банковых целей, ручные процедуры не перевыпускаются.

Исследовательский инструмент, обычная сборка его не использует. --prepare создаёт
отдельный проверяемый кандидат, --apply применяет его только при прежних хешах
рабочих файлов. Оба режима запрещают перезапись уже сохранённой истории.
"""
from pathlib import Path
import argparse,collections,hashlib,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze
from SourcePresentation import format_function,continuity
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/EventActionCodeScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeEventActionCode'


def digest(data):return hashlib.sha256(data).hexdigest()


def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))


def entry_notes(text,entries):
 notes={0xCBE2:'дополнительный вход обходит RES 7,A, отдельный контракт сохранения бита 7 ещё Unknown',
  0xA499:'дополнительный вход обходит ResumePointer, отдельный контракт этого входа ещё Unknown'}
 for entry in entries:
  label=entry['name'].rsplit('.',1)[1]+':'
  pattern=re.compile(r'^'+re.escape(label)+r'\s+.+$',re.M);match=pattern.search(text);assert match
  text=text[:match.start()]+'                ; '+notes[entry['address']]+'\n'+text[match.start():]
 link='; Дополнительные входы [новые ветви событий](../../Docs/StationEventActions.md)'
 assert link not in text
 return text.replace('; -----------------------------------------',link+'\n; -----------------------------------------',1)


def prepare():
 verify();assert not HISTORY.exists() and not CANDIDATE.exists()
 flow=read('ControlFlow');functions=read('Functions');source_map=read('SourceMap');symbols=read('Symbols');interface=read('InterfaceItems')
 roots={row['values'][6]+3 for row in interface};probes={'Station':analyze('Station',extra_roots=roots)}
 map_roots={x['target'] for x in probes['Station']['unresolved'] if x.get('bank')==1 and x.get('target')}
 # D0C3 следует за явным выбором банка 1 и двумя доказанными помощниками без переключения страниц.
 map_roots.add(0xD0C3);probes['Map']=analyze('Map',extra_roots=map_roots)
 additions={};contexts={};ops_by_region={};new_by_region={};affected={};payloads={}
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 for region,probe in probes.items():
  assert not probe['overlaps'],probe['overlaps'];old=next(g for g in flow if g['name']==region)
  known={(i['slot'],i['offset']):i for i in old['instructions']};added=[]
  for i in probe['instructions']:
   key=i['slot'],i['offset']
   if key in known:assert all(i[k]==known[key][k] for k in ('address','hex','operation')),(region,i,known[key])
   else:
    e=next(x for x in source_map if x['slot']==i['slot'] and x['offset']<=i['offset']<x['offset']+x['length'])
    assert e['kind']=='unclassified' and i['offset']+len(bytes.fromhex(i['hex']))<=e['offset']+e['length'],(i,e)
    added.append(i);affected[e['path']]=e
  additions[region]=added;ops_by_region[region]={i['address']:i for i in old['instructions']+added};new_by_region[region]={i['address']:i for i in added}
  for item in probe['unresolved']:
   if item.get('target') is not None:contexts.setdefault((region,item['address'],item['target']),set()).add(item.get('bank'))
 for slot in {i['slot'] for rows in additions.values() for i in rows}:
  e=next(e for e in manifest['entries'] if e['slot']==slot);payloads[slot]=(ROOT/(e['path']+'.sectors.bin')).read_bytes()
 # Поиск только настоящих меток существующих процедур, адресный реестр сам по себе не доказывает наличие метки в тексте.
 label_at={};existing_lines={};existing_ops={}
 for f in functions:
  if f['region'] not in probes:continue
  path=ROOT/f['path'];lines=path.read_text('utf-8').splitlines();selected=[i for i in ops_by_region[f['region']].values() if i['slot']==f['slot'] and f['offset']<=i['offset']<f['end_offset']];selected.sort(key=lambda i:i['offset']);iterator=iter(selected)
  for number,line in enumerate(lines):
   if not line.strip() or line.lstrip().startswith(';') or line[16:].strip().lower().startswith(('module ','endmodule')):continue
   i=next(iterator);key=f['region'],i['address'];existing_ops[key]=(f,number);label=line[:16].strip().removesuffix(':')
   if label:label_at[key]=f['region']+'.'+f['name']+'.'+label
  assert next(iterator,None) is None;existing_lines[path]=lines
 def target_region(region,pc,target):
  if region=='Map':return 'Map' if target>=0xC000 else 'Station'
  if target<0xC000:return 'Station'
  banks=contexts.get((region,pc,target),set())
  if len(banks)==1:return {0:'Station',1:'Map',3:'Music',6:'Text',7:'Help'}.get(next(iter(banks)))
  if not banks and target in ops_by_region['Station']:return 'Station'
  return None
 # Разделение только новых непрерывных участков по доказанным корням и CALL, существующие файлы не разделяются.
 pieces=[]
 for region,rows in additions.items():
  runs=[]
  for i in sorted(rows,key=lambda x:(x['slot'],x['offset'])):
   if not runs or i['slot']!=runs[-1][-1]['slot'] or i['offset']!=runs[-1][-1]['offset']+len(bytes.fromhex(runs[-1][-1]['hex'])):runs.append([])
   runs[-1].append(i)
  starts=set(probes[region]['roots'])
  for caller_region,caller_rows in additions.items():
   for i in caller_rows:
    match=re.fullmatch(r'CALL (?:(?:NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]+)',i['operation'])
    if match:
     target=int(match[1],16)
     if target_region(caller_region,i['address'],target)==region:starts.add(target)
  for run in runs:
   groups=[]
   for i in run:
    if not groups or i['address'] in starts:groups.append([])
    groups[-1].append(i)
   for group in groups:
    first=group[0];end=group[-1]['offset']+len(bytes.fromhex(group[-1]['hex']));name='Unknown'+format(first['address'],'04X');path='Source/'+region+'/'+name+'.asm'
    assert not (ROOT/path).exists() and not any(f['region']==region and f['address']==first['address'] for f in functions)
    f=dict(region=region,name=name,address=first['address'],slot=first['slot'],offset=first['offset'],end_offset=end,
     description='Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются',semantic_status='unknown',path=path)
    pieces.append((f,group));label_at[region,first['address']]=region+'.'+name+'.Entry'
 new_owner={(f['region'],i['address']):f for f,rows in pieces for i in rows};pending={};extra_labels=[]
 # Поиск целей новых переходов, дополнительные входы старых файлов получают только метку без перезаписи инструкций и комментариев.
 for region,rows in additions.items():
  for i in rows:
   match=re.fullmatch(r'(CALL|JP|JR|DJNZ) (?:(NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]+)',i['operation'])
   if not match:continue
   target=int(match[3],16);destination=target_region(region,i['address'],target);key=destination,target
   if key in label_at:continue
   if key in new_owner:
    f=new_owner[key];label_at[key]=f['region']+'.'+f['name']+'.Point'+format(target,'04X')
   elif key in existing_ops:
    f,number=existing_ops[key];lines=existing_lines[ROOT/f['path']];assert not lines[number][:16].strip()
    label='Point'+format(target,'04X');lines[number]=(label+':').ljust(16)+lines[number][16:];label_at[key]=f['region']+'.'+f['name']+'.'+label
    extra_labels.append(dict(path=f['path'],address=target,name=label_at[key]));pending[ROOT/f['path']]='\n'.join(lines)+'\n'
 for path in list(pending):
  local=[x for x in extra_labels if ROOT/x['path']==path]
  if local:pending[path]=entry_notes(pending[path],local)
 for (region,address),label in label_at.items():
  if (region,address) in new_owner or any(x['name']==label for x in extra_labels):symbols[label]=address
 # Обновление реестра потока выполняется объединением, прежние инструкции и контексты не удаляются.
 for region,probe in probes.items():
  old=next(g for g in flow if g['name']==region);old['instructions']=sorted(old['instructions']+additions[region],key=lambda i:(i['slot'],i['offset']))
  for key in ('roots','calls','branches'):old[key]=sorted(set(old[key])|set(probe[key]))
  seen={json.dumps(x,sort_keys=True,ensure_ascii=False) for x in old['unresolved']}
  for x in probe['unresolved']:
   encoded=json.dumps(x,sort_keys=True,ensure_ascii=False)
   if encoded not in seen:old['unresolved'].append(x);seen.add(encoded)
  old['instruction_count']=len(old['instructions']);old['code_bytes']=sum(len(bytes.fromhex(i['hex'])) for i in old['instructions']);old['classified_fraction']=old['code_bytes']/old['total_bytes']
 new_functions=[f for f,_ in pieces];functions+=new_functions;following,order=continuity(functions,flow)
 for f,rows in pieces:
  lines=['                module '+f['region'],'                module '+f['name'],
   '; Документация [новые входы действий](../../Docs/StationEventActions.md)',
   '; -----------------------------------------','; '+f['description'],
   '; исходная запись '+str(f['slot'])+', файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X'),
   '; In:',';   Unknown, отдельный контракт нового входа ещё не установлен',
   '; Out:',';   исходные инструкции, адреса и порядок байтов сохранены',
   '; Corrupt:',';   Unknown, достижимость не доказывает назначение или регистровый договор',
   '; -----------------------------------------']
  for i in rows:
   full=label_at.get((f['region'],i['address']));label=full.rsplit('.',1)[1] if full else '';operation=i['operation'].replace(',',', ')
   operation=re.sub(r'\((IX|IY)([+-])#([0-9A-F]+)\)',r'(\1 \2 #\3)',operation)
   match=re.fullmatch(r'(CALL|JP|JR|DJNZ) (?:(NZ|Z|NC|C|PO|PE|P|M),\s*)?#([0-9A-F]+)',operation)
   if match:
    target=int(match[3],16);destination=target_region(f['region'],i['address'],target);name=label_at.get((destination,target))
    if name:operation=match[1]+' '+(match[2]+', ' if match[2] else '')+'@'+name
   lines.append(((label+':').ljust(16) if label else ' '*16)+operation)
  lines+=['                endmodule','                endmodule'];pending[ROOT/f['path']]=format_function('\n'.join(lines)+'\n',following.get(f['path']))
 # Сохранение полного физического диапазона каждого прежнего INCBIN, промежутки остаются отдельными Unknown-байтами.
 deletes=[];include_files={};new_ranges=[]
 for path,e in affected.items():
  original=ROOT/path;raw=payloads[e['slot']];assert original.read_bytes()==raw[e['offset']:e['offset']+e['length']];deletes.append(path)
  local=sorted([f for f in new_functions if f['slot']==e['slot'] and e['offset']<=f['offset']<e['offset']+e['length']],key=lambda f:f['offset']);position=e['offset'];parts=[]
  for f in [*local,None]:
   end=f['offset'] if f else e['offset']+e['length']
   if position<end:
    gap=str(Path(path).parent/('EventGap'+format(position,'04X')+'.bin')).replace('\\','/');assert not (ROOT/gap).exists();pending[ROOT/gap]=raw[position:end]
    parts.append(dict(slot=e['slot'],offset=position,length=end-position,kind='unclassified',path=gap,origin=None,sha256=digest(raw[position:end])))
   if f:
    end=f['end_offset'];parts.append(dict(slot=f['slot'],offset=f['offset'],length=end-f['offset'],kind='code',path=f['path'],origin=f['address'],sha256=digest(raw[f['offset']:end])))
   position=end
  needle='                incbin "../'+path.removeprefix('Source/')+'"';matches=[]
  for inc in (ROOT/'Source/Files').glob('*.inc'):
   content=include_files.get(inc,inc.read_text('utf-8'))
   if needle in content:matches.append((inc,content))
  assert len(matches)==1,(path,matches);inc,content=matches[0];lines=[]
  for item in parts:
   relative='../'+item['path'].removeprefix('Source/')
   if item['kind']=='code':
    line='                include "'+relative+'"'
    if item['path'] in order:line=line.ljust(80)+'; ('+str(order[item['path']])+') жёсткий порядок, последовательное исполнение'
    lines+=['                disp #'+format(item['origin'],'04X'),line,'                ent']
   else:lines+=['                ; Unknown, сохранённые байты вне новых доказанных входов','                incbin "'+relative+'"']
   lines+=['                assert $ == #'+format(item['offset']+item['length'],'04X')]
  include_files[inc]=content.replace(needle,'\n'.join(lines),1);new_ranges.extend(parts)
 source_map=[e for e in source_map if e['path'] not in affected]+new_ranges
 # Согласование только затронутых цепочек INCLUDE, номера существующих соседей меняются при новом продолжении.
 for inc in (ROOT/'Source/Files').glob('*.inc'):
  before=include_files.get(inc,inc.read_text('utf-8'));lines=[]
  for line in before.splitlines():
   match=re.match(r'\s*include "\.\./([^\"]+)"',line)
   if match:
    path='Source/'+match[1]
    if path in order:
     left,separator,comment=line.partition(';')
     if not separator or 'жёсткий порядок' in comment:line=left.rstrip().ljust(80)+'; ('+str(order[path])+') жёсткий порядок, последовательное исполнение'
   lines.append(line)
  after='\n'.join(lines)+'\n'
  if after!=inc.read_text('utf-8'):pending[inc]=after
 docs=ROOT/'Docs/Functions.md';text=docs.read_text('utf-8')
 for region in probes:
  local=[f for f in functions if f['region']==region];text=re.sub(r'^\| '+region+r' \| \d+ \| \d+ \|','| '+region+' | '+str(len(local))+' | '+str(sum(f['semantic_status']=='described' for f in local))+' |',text,flags=re.M)
 for f in new_functions:text+='\n| #'+format(f['address'],'04X')+' | ['+f['region']+'.'+f['name']+'](../'+f['path']+') | Unknown, новый вход действия или его достижимый помощник |\n'
 pending[docs]=text
 for region in probes:
  p=ROOT/'Docs/FunctionDetails'/(region+'.md');text=p.read_text('utf-8')
  for f in new_functions:
   if f['region']==region:text+='\n## '+f['name']+'\n\n['+f['region']+'.'+f['name']+'](../../'+f['path']+') — '+f['description']+'.\n'
  pending[p]=text
 documentation=['# Новые входы действий интерфейса и банковые продолжения','',
  'Исходный DispatchInterfaceEvent передаёт управление по EventHandler+3, минуя трёхбайтовую обёртку. Проверка фактических 46 записей обнаружила 19 прежде непокрытых входов. Их прямые пути дают новые станционные инструкции и вызовы банка карты. Это восстановление достижимости и физических инструкций, алгоритмы перечисленных ниже фрагментов пока Unknown. Ручные исходники не перевыпускаются.','',
  'Дополнительный D0C3 подтверждён вызовом из Unknown6D58 после выбора банка 1 и двух разобранных помощников без переключения банков. Неопределённый банковый контекст не заменяется предположением по одному CPU-адресу.','',
  '| Регион | Адрес | Новый исходник | Байтов |','| --- | --- | --- | --- |']
 for f in new_functions:documentation.append('| '+f['region']+' | '+format(f['address'],'04X')+' | ['+f['name']+'](../'+f['path']+') | '+str(f['end_offset']-f['offset'])+' |')
 documentation+=['','## Дополнительные входы в существующих файлах','',
  'Существующие инструкции и комментарии сохранены. Отдельные договоры новых внутренних входов пока Unknown.']
 for x in extra_labels:documentation.append('- ['+x['name']+'](../'+x['path']+'), адрес '+format(x['address'],'04X')+'.')
 documentation+=['','Сборка и исполнение новых ветвей не выполнялись. Совпадение инструкций с исходными байтами не доказывает полной семантики. Исходные разметки и причины корней находятся в [StationEventRootsAudit](../Tools/Disasm/Reports/StationEventRootsAudit.json) и [MapEventRootsAudit](../Tools/Disasm/Reports/MapEventRootsAudit.json).']
 pending[ROOT/'Docs/StationEventActions.md']='\n'.join(documentation)+'\n'
 inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(g['instruction_count'] for g in flow))
 inventory['physical_bytes_by_kind']={k:sum(e['length'] for e in source_map if e['kind']==k) for k in sorted({e['kind'] for e in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map))
 for name,value in (('Functions',functions),('ControlFlow',flow),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 plan=dict(method='scoped_event_action_code_candidate_from_actual_bytes_and_dispatcher_roots',new_instructions=sum(map(len,additions.values())),new_code_bytes=sum(len(bytes.fromhex(i['hex'])) for rows in additions.values() for i in rows),new_fragments=len(new_functions),extra_existing_labels=extra_labels,deletes=deletes,files=[],semantic_completeness_proved=False,assembly_executed=False)
 CANDIDATE.mkdir(parents=True)
 for path,data in pending.items():
  if isinstance(data,str):data=data.encode('utf-8')
  relative=path.relative_to(ROOT).as_posix();candidate=CANDIDATE/relative;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_bytes(data)
  plan['files'].append(dict(path=relative,before_sha256=digest(path.read_bytes()) if path.exists() else None,candidate_sha256=digest(data)))
 plan['deleted_file_hashes']={p:digest((ROOT/p).read_bytes()) for p in deletes};(CANDIDATE/'Plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in plan.items() if k not in ('files','deletes','deleted_file_hashes','extra_existing_labels')},ensure_ascii=False,indent=2));print('candidate_files',len(plan['files']),'extra_existing_labels',len(extra_labels))


def apply():
 assert not HISTORY.exists();plan=json.loads((CANDIDATE/'Plan.json').read_text('utf-8'));verify()
 checked=read('EventActionCandidateVerification');assert checked['passed'] and checked['plan_sha256']==digest((CANDIDATE/'Plan.json').read_bytes())
 # Проверка каждого текущего файла и каждого кандидата до первой записи в рабочую копию.
 for item in plan['files']:
  path=(ROOT/item['path']).resolve();candidate=(CANDIDATE/item['path']).resolve();assert path.is_relative_to(ROOT) and candidate.is_relative_to(CANDIDATE)
  assert (digest(path.read_bytes()) if path.exists() else None)==item['before_sha256'],item['path'];assert digest(candidate.read_bytes())==item['candidate_sha256'],item['path']
 for relative,expected in plan['deleted_file_hashes'].items():assert digest((ROOT/relative).read_bytes())==expected,relative
 for relative in {item['path'] for item in plan['files'] if item['before_sha256'] is not None}|set(plan['deletes']):
  path=ROOT/relative;target=HISTORY/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 for item in plan['files']:
  path=ROOT/item['path'];path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(CANDIDATE/item['path'],path)
 verify()
 # Удаление только побайтово сохранённых прежних INCBIN после проверки нового полного физического покрытия.
 for relative in plan['deletes']:
  path=(ROOT/relative).resolve();assert path.is_relative_to(ROOT/'Source/Resources') and path.read_bytes()==(HISTORY/relative).read_bytes();path.unlink()
 report={k:v for k,v in plan.items() if k not in ('files','deletes','deleted_file_hashes')};report.update(passed=True,candidate_files=len(plan['files']),history_preserved=True)
 (ROOT/'Tools/Disasm/Reports/EventActionCodeVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--prepare',action='store_true');group.add_argument('--apply',action='store_true');args=parser.parse_args();prepare() if args.prepare else apply()

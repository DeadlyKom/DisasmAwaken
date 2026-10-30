"""Отдельный кандидат 370 байтов по фактическому банковому вызову C677, без общего экспорта."""
from pathlib import Path
import argparse,collections,hashlib,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze
from SourcePresentation import format_function,continuity
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/AnimatedVariantCodeScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeAnimatedVariantCode'
STARTS=(0xC677,0xC6C0,0xC6DD,0xC6FA,0xC717,0xC734,0xC751,0xC76E,0xC827)


def digest(data):return hashlib.sha256(data).hexdigest()
def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))


def prepare():
 verify();assert not HISTORY.exists() and not CANDIDATE.exists()
 assert read('AnimatedVariantsVerification')['passed']
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 def payload(slot):return (ROOT/(next(e for e in manifest['entries'] if e['slot']==slot)['path']+'.sectors.bin')).read_bytes()
 station=payload(4);raw=payload(7)
 assert station[0x1BDF:0x1BE8]==bytes.fromhex('3e11cd9663f1cd77c6')
 flow=read('ControlFlow');functions=read('Functions');source_map=read('SourceMap');symbols=read('Symbols')
 region=next(g for g in flow if g['name']=='Map');known={(i['slot'],i['offset']) for i in region['instructions']}
 probe=analyze('Map',extra_roots=(0xC677,));assert not probe['overlaps']
 added=[i for i in probe['instructions'] if (i['slot'],i['offset']) not in known]
 assert len(added)==228 and sum(len(bytes.fromhex(i['hex'])) for i in added)==370
 assert {i['offset'] for i in added}=={i['offset'] for i in probe['instructions'] if 0x677<=i['offset']<0x781 or 0x827<=i['offset']<0x88F}
 pieces=[]
 for start in STARTS:
  end=STARTS[STARTS.index(start)+1] if start<0xC76E else 0xC781 if start==0xC76E else 0xC88F
  rows=[i for i in added if start<=i['address']<end];assert rows and rows[0]['address']==start
  name='Unknown'+format(start,'04X');path='Source/Map/'+name+'.asm';assert not (ROOT/path).exists()
  f=dict(region='Map',name=name,address=start,slot=7,offset=start-0xC000,end_offset=end-0xC000,
   description='Unknown, доказанный код анимации вариантов, подробное оформление контракта продолжается',semantic_status='unknown',path=path)
  pieces.append((f,rows));functions.append(f)
 labels={f['address']:'Map.'+f['name']+'.Entry' for f,_ in pieces}
 for f,rows in pieces:
  for i in rows:
   match=re.fullmatch(r'(?:CALL|JP|JR|DJNZ) (?:(?:NZ|Z|NC|C|M|P),)?#([0-9A-F]+)',i['operation'])
   if match:
    target=int(match[1],16)
    if target not in labels:
     owner=next((p for p,_ in pieces if p['address']<=target<p['end_offset']+0xC000),None)
     assert owner is not None,(i,target)
     labels[target]='Map.'+owner['name']+'.Point'+format(target,'04X')
 region['instructions']=sorted(region['instructions']+added,key=lambda i:(i['slot'],i['offset']))
 for key in ('roots','calls','branches'):region[key]=sorted(set(region[key])|set(probe[key]))
 region['instruction_count']+=len(added);region['code_bytes']+=370;region['classified_fraction']=region['code_bytes']/region['total_bytes']
 following,order=continuity(functions,flow);pending={}
 for f,rows in pieces:
  lines=['                module Map','                module '+f['name'],
   '; Документация [доказанные потоки вариантов](../../Docs/AnimatedVariants.md)',
   '; -----------------------------------------','; '+f['description'],
   '; исходная запись 7, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X'),
   '; In:',';   Unknown, точный регистровый договор оформляется после физического выделения',
   '; Out:',';   исходные инструкции, адреса и последовательное исполнение сохранены',
   '; Corrupt:',';   Unknown, наличие модели не заменяет описание договора в исходнике',
   '; -----------------------------------------']
  for i in rows:
   label=labels.get(i['address'],'').rsplit('.',1)[-1];operation=i['operation'].replace(',',', ')
   match=re.fullmatch(r'(CALL|JP|JR|DJNZ) (?:(NZ|Z|NC|C|M|P),\s*)?#([0-9A-F]+)',operation)
   if match:operation=match[1]+' '+(match[2]+', ' if match[2] else '')+'@'+labels[int(match[3],16)]
   if re.fullmatch(r'(?:JR|JP) (?:NZ|Z|NC|C|M|P),.+',operation):operation=operation.ljust(64)+'; переход, если выполнено исходное условие, смысл описывается отдельно'
   elif operation=='RET M':operation=operation.ljust(64)+'; выход, если флаг Sign установлен, смысл описывается отдельно'
   lines.append(((label+':').ljust(16) if label else ' '*16)+operation)
  lines+=['                endmodule','                endmodule'];pending[ROOT/f['path']]=format_function('\n'.join(lines)+'\n',following.get(f['path']))
 symbols.update({name:address for address,name in labels.items()});include=ROOT/'Source/Files/07_KARTA.inc';content=include.read_text('utf-8');deletes=[]
 for old_name,begin,end in (('EventGap0677.bin',0x677,0x781),('Unclassified003.bin',0x827,0x88F)):
  relative='Source/Resources/07_KARTA/'+old_name;old=ROOT/relative;assert old.read_bytes()==raw[begin:end]
  item=next(e for e in source_map if e['path']==relative);assert (item['offset'],item['length'])==(begin,end-begin)
  local=[f for f,_ in pieces if begin<=f['offset']<end];parts=[];lines=[]
  for f in local:
   parts.append(dict(slot=7,offset=f['offset'],length=f['end_offset']-f['offset'],kind='code',path=f['path'],origin=f['address'],sha256=digest(raw[f['offset']:f['end_offset']])))
   line='                include "../Map/'+f['name']+'.asm"'
   if f['path'] in order:line=line.ljust(80)+'; ('+str(order[f['path']])+') жёсткий порядок, последовательное исполнение'
   lines+=['                disp #'+format(f['address'],'04X'),line,'                ent','                assert $ == #'+format(f['end_offset'],'04X')]
  index=source_map.index(item);source_map[index:index+1]=parts
  needle='                incbin "../Resources/07_KARTA/'+old_name+'"';assert content.count(needle)==1;content=content.replace(needle,'\n'.join(lines),1);deletes.append(relative)
 pending[include]=content
 document=['# Анимация вариантов вокруг исходной позиции','',
  'Корень C677 подтверждён исходным станционным CALL по 7939 после LD A,11 и SelectRamBank. Этот участок станции пока хранится в непрозрачных данных. Статическое основание не выдано за наблюдавшийся игровой вызов.',
  '', 'Поток содержит подготовку общего начала, шесть последовательных обёрток, выбор мигающего ресурса и трёхстрочный XOR. Подробные регистровые договоры оформляются отдельно. Все исходные адреса сохранены, новой памяти не выделено.', '']
 for f,_ in pieces:document+=['- [Map.'+f['name']+'](../'+f['path']+') по '+format(f['address'],'04X')+'.']
 document+=['','Модель CheckAnimatedVariants исполняет настоящие вызовы, сравнивает bitmap, все байты счётчика и маски мигания, курсоры и стек. Это не нативный игровой запуск.']
 pending[ROOT/'Docs/AnimatedVariants.md']='\n'.join(document)+'\n'
 p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');local=[f for f in functions if f['region']=='Map'];text=re.sub(r'^\| Map \| \d+ \| \d+ \|','| Map | '+str(len(local))+' | '+str(sum(f['semantic_status']=='described' for f in local))+' |',text,flags=re.M)
 detail=(ROOT/'Docs/FunctionDetails/Map.md').read_text('utf-8')
 for f,_ in pieces:
  text+='\n| #'+format(f['address'],'04X')+' | [Map.'+f['name']+'](../'+f['path']+') | '+f['description']+' |\n'
  detail+='\n## '+f['name']+'\n\n[Map.'+f['name']+'](../../'+f['path']+') — '+f['description']+'.\n'
 pending[p]=text;pending[ROOT/'Docs/FunctionDetails/Map.md']=detail
 p=ROOT/'Tools/Disasm/Research/Analyze.py';text=p.read_text('utf-8');old='"Map", (0xC000, 0xC44A, 0xC474, 0xD0C3))';assert text.count(old)==1
 pending[p]=text.replace(old,'"Map", (0xC000, 0xC44A, 0xC474, 0xC677, 0xD0C3))')
 inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(g['instruction_count'] for g in flow))
 inventory['physical_bytes_by_kind']={k:sum(e['length'] for e in source_map if e['kind']==k) for k in sorted({e['kind'] for e in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map))
 for name,value in (('Functions',functions),('ControlFlow',flow),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 plan=dict(method='actual_station_banked_call_and_scoped_direct_map_flow',new_instructions=228,new_code_bytes=370,new_fragments=9,
  extra_existing_labels=[],deletes=deletes,deleted_file_hashes={rel:digest((ROOT/rel).read_bytes()) for rel in deletes},files=[],semantic_completeness_proved=False,assembly_executed=False)
 for path,data in pending.items():
  data=data.encode('utf-8');relative=path.relative_to(ROOT).as_posix();candidate=CANDIDATE/relative;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_bytes(data)
  plan['files'].append(dict(path=relative,before_sha256=digest(path.read_bytes()) if path.exists() else None,candidate_sha256=digest(data)))
 (CANDIDATE/'Plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
 print('Scoped candidate prepared, 228 instructions and 370 original bytes, existing manual sources preserved')


def apply(candidate=None,history=None,check_name="AnimatedVariantCandidateVerification",report_name="AnimatedVariantCodeVerification"):
 candidate=candidate or CANDIDATE;history=history or HISTORY
 assert not history.exists();verify();plan=json.loads((candidate/'Plan.json').read_text('utf-8'))
 checked=read(check_name);assert checked['passed'] and checked['plan_sha256']==digest((candidate/'Plan.json').read_bytes())
 # Проверка прежних хешей всего набора до первой записи в рабочую копию.
 for item in plan['files']:
  path=ROOT/item['path'];assert (digest(path.read_bytes()) if path.exists() else None)==item['before_sha256'],item['path']
  assert digest((candidate/item['path']).read_bytes())==item['candidate_sha256']
 for rel,sha in plan['deleted_file_hashes'].items():assert digest((ROOT/rel).read_bytes())==sha
 for rel in {i['path'] for i in plan['files'] if i['before_sha256'] is not None}|set(plan['deletes']):
  target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
 for item in plan['files']:
  target=ROOT/item['path'];assert target.resolve().is_relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(candidate/item['path'],target)
 verify()
 for rel in plan['deletes']:
  path=ROOT/rel;assert path.resolve().is_relative_to(ROOT/'Source/Resources') and path.read_bytes()==(history/rel).read_bytes();path.unlink()
 report=dict(passed=True,new_instructions=plan["new_instructions"],new_code_bytes=plan["new_code_bytes"],new_fragments=plan["new_fragments"],history_preserved=True,assembly_executed=False)
 (ROOT/('Tools/Disasm/Reports/'+report_name+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report))


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('prepare','check','apply'));args=parser.parse_args()
 if args.mode=='prepare':prepare()
 elif args.mode=='apply':apply()
 else:
  from CheckEventActionCandidate import main
  main(CANDIDATE,'Docs/AnimatedVariants.md','AnimatedVariantCandidateVerification')

"""Два станционных входа по реальной записи callback MainLoop, отдельный кандидат 139 байтов."""
from pathlib import Path
import argparse,collections,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze
from ClassifyAnimatedVariantCode import digest,read,apply
from SourcePresentation import format_function
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PeriodicVariantCodeScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePeriodicVariantCode'


def prepare():
 verify();assert not CANDIDATE.exists() and not HISTORY.exists()
 flow=read('ControlFlow');functions=read('Functions');source_map=read('SourceMap');symbols=read('Symbols')
 region=next(g for g in flow if g['name']=='Station');old_by_address={i['address']:i for i in region['instructions']}
 assert old_by_address[0x78A3]['operation']=='LD HL,#78D6' and old_by_address[0x78A6]['operation']=='LD (#9A89),HL'
 assert old_by_address[0x9A88]['operation']=='CALL #9A58'
 probe=analyze('Station',extra_roots=(0x78D6,));known={(i['slot'],i['offset']) for i in region['instructions']}
 added=[i for i in probe['instructions'] if (i['slot'],i['offset']) not in known]
 assert not probe['overlaps'] and len(added)==75 and sum(len(bytes.fromhex(i['hex'])) for i in added)==139
 assert all(i['slot']==4 and 0x1B69<=i['offset']<0x1BF4 for i in added)
 pieces=[]
 for start,end in ((0x78BD,0x78D6),(0x78D6,0x7948)):
  name='Unknown'+format(start,'04X');path='Source/Station/'+name+'.asm';assert not (ROOT/path).exists()
  f=dict(region='Station',name=name,address=start,slot=4,offset=start-0x5D54,end_offset=end-0x5D54,path=path,
   description='Unknown, доказанный периодический путь анимации вариантов, регистровый договор оформляется отдельно',semantic_status='unknown');pieces.append((f,[i for i in added if start<=i['address']<end]));functions.append(f)
 new_labels={f['address']:'Station.'+f['name']+'.Entry' for f,_ in pieces}
 labels={f['address']:f['region']+'.'+f['name']+'.Entry' for f in functions if f['region']=='Station'};labels[0xC677]='Map.DrawVariantCluster.Entry'
 for f,rows in pieces:
  for i in rows:
   match=re.fullmatch(r'(?:CALL|JP|JR|DJNZ) (?:(?:NZ|Z|NC|C|M|P),)?#([0-9A-F]+)',i['operation'])
   if match:
    target=int(match[1],16)
    if target not in labels:
     owner=next((p for p,_ in pieces if p['address']<=target<p['end_offset']+0x5D54),None);assert owner is not None,(i,target)
     labels[target]='Station.'+owner['name']+'.Point'+format(target,'04X');new_labels[target]=labels[target]
 pending={}
 for f,rows in pieces:
  lines=['                module Station','                module '+f['name'],
   '; Документация [периодический путь вариантов](../../Docs/PeriodicVariants.md)',
   '; -----------------------------------------','; '+f['description'],
   '; исходная запись 4, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X'),
   '; In:',';   Unknown, точный регистровый договор оформляется отдельно',
   '; Out:',';   исходный поток, банковые вызовы, стек и байты сохранены',
   '; Corrupt:',';   Unknown, статическая запись callback не доказывает полный игровой запуск','; -----------------------------------------']
  for i in rows:
   label=new_labels.get(i['address'],'').rsplit('.',1)[-1];operation=i['operation'].replace(',',', ')
   match=re.fullmatch(r'(CALL|JP|JR|DJNZ) (?:(NZ|Z|NC|C|M|P),\s*)?#([0-9A-F]+)',operation)
   if match:operation=match[1]+' '+(match[2]+', ' if match[2] else '')+'@'+labels[int(match[3],16)]
   lines.append(((label+':').ljust(16) if label else ' '*16)+operation)
  lines+=['                endmodule','                endmodule'];pending[ROOT/f['path']]=format_function('\n'.join(lines)+'\n')
 symbols.update({name:address for address,name in new_labels.items()});region['instructions']=sorted(region['instructions']+added,key=lambda i:(i['slot'],i['offset']))
 for key in ('roots','calls','branches'):region[key]=sorted(set(region[key])|set(probe[key]))
 existing={json.dumps(i,sort_keys=True,ensure_ascii=False) for i in region['unresolved']}
 region['unresolved'] += [i for i in probe['unresolved'] if json.dumps(i,sort_keys=True,ensure_ascii=False) not in existing]
 region['instruction_count']+=75;region['code_bytes']+=139;region['classified_fraction']=region['code_bytes']/region['total_bytes']
 relative='Source/Resources/04_STATIONF/Unclassified040.bin';old=ROOT/relative;item=next(e for e in source_map if e['path']==relative);assert (item['offset'],item['length'])==(0x1B69,139)
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));raw=(ROOT/(next(e for e in manifest['entries'] if e['slot']==4)['path']+'.sectors.bin')).read_bytes();assert old.read_bytes()==raw[0x1B69:0x1BF4]
 index=source_map.index(item);source_map[index:index+1]=[dict(item,kind='code',offset=f['offset'],length=f['end_offset']-f['offset'],path=f['path'],origin=f['address'],sha256=digest(raw[f['offset']:f['end_offset']])) for f,_ in pieces]
 include=ROOT/'Source/Files/04_STATIONF.inc';text=include.read_text('utf-8');needle='                incbin "../Resources/04_STATIONF/Unclassified040.bin"';assert text.count(needle)==1
 replacement='\n'.join('                disp #'+format(f['address'],'04X')+'\n                include "../Station/'+f['name']+'.asm"\n                ent\n                assert $ == #'+format(f['end_offset'],'04X') for f,_ in pieces);pending[include]=text.replace(needle,replacement,1)
 p=ROOT/'Tools/Disasm/Research/Analyze.py';text=p.read_text('utf-8');needle='            # Расчёт константы A для последующих явных переключений банков.';assert text.count(needle)==1
 addition='''            # Поиск фактического callback MainLoop по записи в операнд периодического CALL.
            if name == "Station" and operation == "LD (#9A89),HL" and hl_constant in origins:
                roots.add(hl_constant)
                pending.append((hl_constant, bank, None))
''';pending[p]=text.replace(needle,addition+needle,1)
 document=['# Периодический вызывающий путь анимации вариантов','',
  '[DrawItem20](../Source/Station/DrawItem20.asm) записывает 78D6 в операнд MenuCommandState.PeriodicCall по 9A89. MainLoop имеет исходный CALL по 9A88, поле цели начинается с 9A89. Это прямое основание кода callback, адреса не выбраны по сходству байтов.', '']
 for f,_ in pieces:document+=['- [Station.'+f['name']+'](../'+f['path']+') по '+format(f['address'],'04X')+'.']
 document+=['','Нормальный путь вращает временную маску, проверяет последний обработчик списка, получает количество выбранных вариантов, очищает тело и вызывает [DrawVariantCluster](../Source/Map/DrawVariantCluster.asm) в банке 1. Отложенный путь зависит от наличия активного элемента. Подробный договор обоих входов ещё оформляется. Статическое основание callback не является нативным запуском.']
 pending[ROOT/'Docs/PeriodicVariants.md']='\n'.join(document)+'\n'
 p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');local=[f for f in functions if f['region']=='Station'];text=re.sub(r'^\| Station \| \d+ \| \d+ \|','| Station | '+str(len(local))+' | '+str(sum(f['semantic_status']=='described' for f in local))+' |',text,flags=re.M)
 detail=(ROOT/'Docs/FunctionDetails/Station.md').read_text('utf-8')
 for f,_ in pieces:
  text+='\n| #'+format(f['address'],'04X')+' | [Station.'+f['name']+'](../'+f['path']+') | '+f['description']+' |\n'
  detail+='\n## '+f['name']+'\n\n[Station.'+f['name']+'](../../'+f['path']+') — '+f['description']+'.\n'
 pending[p]=text;pending[ROOT/'Docs/FunctionDetails/Station.md']=detail
 inventory=read('Inventory');inventory.update(fragments=len(functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(g['instruction_count'] for g in flow));inventory['physical_bytes_by_kind']={k:sum(e['length'] for e in source_map if e['kind']==k) for k in sorted({e['kind'] for e in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map))
 for name,value in (('Functions',functions),('ControlFlow',flow),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 plan=dict(method='actual_periodic_CALL_operand_store_and_direct_station_flow',new_instructions=75,new_code_bytes=139,new_fragments=2,extra_existing_labels=[],deletes=[relative],deleted_file_hashes={relative:digest(old.read_bytes())},files=[],semantic_completeness_proved=False,assembly_executed=False)
 for path,text in pending.items():
  data=text.encode('utf-8');rel=path.relative_to(ROOT).as_posix();target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  plan['files'].append(dict(path=rel,before_sha256=digest(path.read_bytes()) if path.exists() else None,candidate_sha256=digest(data)))
 (CANDIDATE/'Plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8');print('Prepared 75 instructions, 139 original bytes and two callback entries')


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('prepare','check','apply'));args=parser.parse_args()
 if args.mode=='prepare':prepare()
 elif args.mode=='check':
  from CheckEventActionCandidate import main
  main(CANDIDATE,'Docs/PeriodicVariants.md','PeriodicVariantCandidateVerification')
 else:apply(CANDIDATE,HISTORY,'PeriodicVariantCandidateVerification','PeriodicVariantCodeVerification')

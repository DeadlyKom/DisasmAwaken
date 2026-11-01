"""Точечное применение доказанных фактов к уже выделенным станционным фрагментам."""
from pathlib import Path
import collections,contextlib,importlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify


def apply(facts,tag,verification):
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read(verification)['passed'];candidate=ROOT/('Tools/Disasm/Research/Candidates/'+tag+'Scoped');history=ROOT/('Tools/Disasm/Research/History/Before'+tag)
 assert not candidate.exists() and not history.exists()
 def rename(text):
  for old,new in facts.RENAMES.items():
   text=re.sub(r'\bStation\.'+re.escape(old)+r'\b','Station.'+new,text).replace('Source/Station/'+old+'.asm','Source/Station/'+new+'.asm').replace('../Station/'+old+'.asm','../Station/'+new+'.asm')
  for old,new in getattr(facts,'LABEL_RENAMES',{}).items():text=text.replace('Station.'+old,'Station.'+new)
  return text
 functions=read('Functions');previous_described=sum(f['region']=='Station' and f.get('semantic_status')=='described' for f in functions)
 selected=[f for f in functions if f['region']=='Station' and f['address'] in facts.FUNCTIONS];assert len(selected)==len(facts.FUNCTIONS)
 flow=read('ControlFlow');group=next(g for g in flow if g['name']=='Station');validate_notes([group],{'Station':facts.COMMENTS});pending={};removed={}
 for folder,pattern in (('Source','*.asm'),('Source','*.inc'),('Includes','*.inc'),('Docs','*.md')):
  for p in (ROOT/folder).rglob(pattern):
   t=p.read_text('utf-8');updated=rename(t)
   if t!=updated and p.suffix in ('.asm','.inc'):
    # Выравнивание только изменённых ссылок, имя процедуры не должно сдвигать её правый комментарий.
    lines=updated.splitlines();previous=t.splitlines();assert len(lines)==len(previous)
    for index,line in enumerate(lines):
     code,separator,note=line.partition(';')
     if line!=previous[index] and separator and code.strip() and (('@Station.' in code and '"' not in code) or code.lstrip().lower().startswith('include "')):
      assert len(code.rstrip())<80;lines[index]=code.rstrip().ljust(80)+';'+note
    updated='\n'.join(lines)+ ('\n' if updated.endswith('\n') else '')
   if p==ROOT/'Docs/FunctionDetails/Station.md':
    for old,new in facts.RENAMES.items():updated=updated.replace('## '+old+'\n','## '+new+'\n')
   if t!=updated:pending[p]=updated.encode('utf-8')
 # Создание четырёх разделов контракта и комментариев только для согласованных адресов.
 for f in selected:
  address=f['address'];name,description=facts.FUNCTIONS[address];old=ROOT/f['path'];pending.pop(old,None)
  path='Source/Station/'+name+'.asm'
  if old==ROOT/path:assert address in getattr(facts,'IN_PLACE',set())
  else:assert not (ROOT/path).exists();removed[old]=old.read_bytes()
  document,title=facts.DOCUMENTS['Station',address]
  lines=['                module Station','                module '+name,'                ; Документация ['+title+'](../../Docs/'+document+'.md)',
   '                ; -----------------------------------------','                ; '+description,'                ; исходная запись 4, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')]
  for header,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Station',address]):lines+=['                ; '+header+':']+['                ;   '+v for v in values]
  lines+=['                ; -----------------------------------------']
  rows=[i for i in group['instructions'] if i['slot']==4 and f['offset']<=i['offset']<f['end_offset']]
  for index,i in enumerate(rows):
   before,right=facts.COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in before];label='Entry' if index==0 else facts.LABELS.get(('Station',i['address']),'')
   operation=facts.name_operands('Station',address,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+operation
   if right:assert len(line)<80;line=line.ljust(80)+'; '+right
   lines.append(line)
  lines+=['                endmodule','                endmodule'];following=getattr(facts,'CONTINUATIONS',{}).get(address);target=None
  if following:
   target_name=facts.FUNCTIONS[following][0];target=dict(region='Station',name=target_name,path='Source/Station/'+target_name+'.asm')
   f.update(fallthrough_continuation=following,fragment_scope=getattr(facts,'CONTINUATION_SCOPES',{}).get(address,'conditional_branch_then_next_physical_fragment'))
  pending[ROOT/path]=format_function('\n'.join(lines)+'\n',target).encode('utf-8');f.update(name=name,description=description,path=path,semantic_status='described')
 # Обновление текущих ссылок, неизменность исходного потока и банковой цели каждой новой записи проверяется явно.
 modified=json.loads(rename(json.dumps(read('ModifiedCode'),ensure_ascii=False)));by_address={(g['name'],i['address']):i for g in flow for i in g['instructions']}
 for writer,target,target_region,target_instruction,size,bank in getattr(facts,'MODIFIED_WRITES',()):
  item=by_address['Station',writer];assert re.fullmatch(r'LD \(#'+format(target,'04X')+r'\),(A|HL|DE|BC)',item['operation'])
  owner=by_address[target_region,target_instruction];assert target_instruction<target and target+size<=target_instruction+len(bytes.fromhex(owner['hex']))
  existing=next((v for v in modified if v['region']=='Station' and v['writer']==writer),None)
  if existing:assert (existing['target'],existing['size'])==(target,size)
  else:
   source=next(f for f in selected if f['offset']<=item['offset']<f['end_offset']);existing=dict(region='Station',writer=writer,target=target,target_instruction=target_instruction,size=size,target_operation=owner['operation'],path=source['path']);modified.append(existing)
  existing.update(target_region=target_region,target_bank=bank,target_slot=owner['slot'],writer_bank=5 if writer<0x8000 else 2 if writer<0xC000 else 0)
 for name,value in (('Functions',functions),('SourceMap',read('SourceMap')),('Symbols',read('Symbols')),('ModifiedCode',modified)):
  changed=json.loads(rename(encoded(value).decode('utf-8')))
  if name=='Functions':assert [f for f in changed if f['region']!='Station']==[f for f in read('Functions') if f['region']!='Station']
  if name=='Symbols':assert {k:v for k,v in changed.items() if not k.startswith('Station.')}=={k:v for k,v in value.items() if not k.startswith('Station.')}
  if name=='Symbols':
   # Регистрация нового внутреннего входа только внутри реально переоформляемой процедуры.
   for (region,address),label in facts.LABELS.items():
    owners=[f for f in selected if f['region']==region and f['address']<=address<f['address']+f['end_offset']-f['offset']]
    assert len(owners)==1,(region,address,label)
    key=region+'.'+owners[0]['name']+'.'+label;assert changed.get(key,address)==address;changed[key]=address
  pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encoded(changed)
 # Проверка точных имён и адресов процедур до записи кандидата поверх текущих исходников.
 future_symbols=json.loads(pending[ROOT/'Tools/Disasm/Reports/Symbols.json'].decode('utf-8'))
 for address,target in getattr(facts,'TARGETS',{}).items():
  if target.startswith('Station.'):assert future_symbols.get(target)==address,('unknown_or_wrong_station_target',target,address)
 inventory=read('Inventory');inventory['described']=sum(f.get('semantic_status')=='described' for f in functions);inventory['unknown']=len(functions)-inventory['described'];pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 module=facts.__name__;prefix=tag.upper()
 for filename,extra in (
  ('Knowledge.py','\nfrom '+module+' import FUNCTIONS as '+prefix+'_FUNCTIONS\nFUNCTIONS[\'Station\'].update('+prefix+'_FUNCTIONS)\n'),
  ('Contracts.py','\nfrom '+module+' import CONTRACTS as '+prefix+'_CONTRACTS\nCONTRACTS.update('+prefix+'_CONTRACTS)\n'),
  ('StationNotes.py','\nfrom '+module+' import COMMENTS as '+prefix+'_COMMENTS\nCOMMENTS.update('+prefix+'_COMMENTS)\n'),
  ('SemanticNames.py','\nfrom '+module+' import LABELS as '+prefix+'_LABELS, DOCUMENTS as '+prefix+'_DOCUMENTS, name_operands as '+tag.lower()+'_name_operands\nLABELS.update('+prefix+'_LABELS)\nDOCUMENTS.update('+prefix+'_DOCUMENTS)\n')):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from '+module+' import' not in t
  if filename=='SemanticNames.py':
   needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = '+tag.lower()+'_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 p=ROOT/'Docs/Functions.md';t=pending.get(p,p.read_bytes()).decode('utf-8');total=sum(f['region']=='Station' for f in functions);new_described=sum(f['region']=='Station' and f.get('semantic_status')=='described' for f in functions)
 needle='| Station | '+str(total)+' | '+str(previous_described)+' |';assert t.count(needle)==1;pending[p]=t.replace(needle,'| Station | '+str(total)+' | '+str(new_described)+' |').encode('utf-8')
 p=ROOT/'Docs/FunctionDetails/Station.md';t=pending.get(p,p.read_bytes()).decode('utf-8')
 for address,(name,description) in facts.FUNCTIONS.items():document,_=facts.DOCUMENTS['Station',address];t+='\n['+name+'](../../Source/Station/'+name+'.asm) — '+description+', [алгоритм и проверка](../'+document+'.md).\n'
 pending[p]=t.encode('utf-8');p=ROOT/'Docs/ModifiedCode.md';t=pending.get(p,p.read_bytes()).decode('utf-8')
 for writer,target,target_region,target_instruction,size,bank in getattr(facts,'MODIFIED_WRITES',()):
  if not any(v['region']=='Station' and v['writer']==writer for v in read('ModifiedCode')):
   source=next(v['path'] for v in modified if v['region']=='Station' and v['writer']==writer)
   t+='\n| Station | #'+format(writer,'04X')+' | #'+format(target,'04X')+' | '+target_region+', банк '+str(bank)+', '+by_address[target_region,target_instruction]['operation']+' | ['+Path(source).name+'](../'+source+') |\n'
 pending[p]=t.encode('utf-8')
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);old=p.read_bytes() if p.exists() else None;plan.append((rel,old,data));target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,old,data in plan:assert (ROOT/rel).read_bytes()==old if old is not None else not (ROOT/rel).exists()
 for rel,old,data in plan:
  if old is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old)
 for p,data in removed.items():target=history/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,old,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 for p,data in removed.items():assert p.resolve().is_relative_to((ROOT/'Source/Station').resolve()) and p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
 result=dict(passed=True,functions_described=len(selected),instructions_changed=0,physical_bytes_preserved=True,scoped_candidate_and_history=True,explicit_banked_modified_targets=True,assembly_executed=False)
 (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).write_bytes(encoded(result));print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
 assert len(sys.argv)==4;apply(importlib.import_module(sys.argv[1]),sys.argv[2],sys.argv[3])

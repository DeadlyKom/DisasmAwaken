"""Точечное применение доказанных D3D-фрагментов через отдельный кандидат, без сборки."""
from pathlib import Path
import collections,contextlib,copy,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from InspectZ80 import decoder
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify


def apply(facts,tag,original_path,ranges,verification,extra_texts=None):
 with contextlib.redirect_stdout(io.StringIO()):verify()
 candidate=ROOT/('Tools/Disasm/Research/Candidates/'+tag+'Scoped');history=ROOT/('Tools/Disasm/Research/History/Before'+tag)
 assert not candidate.exists() and not history.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read(verification)['passed']
 raw=payload(6);memory=bytearray(65536);memory[0xC000:0xC000+len(raw)]=raw;dis=decoder(memory)
 functions=read('Functions');old_count=sum(f['region']=='D3D' for f in functions);symbols=read('Symbols');pending=dict(extra_texts or {});binaries={};added=[]
 flow=read('ControlFlow');previous=next(v for v in flow if v['name']=='D3D');g=copy.deepcopy(previous)
 for begin,(name,description) in facts.FUNCTIONS.items():
  end=facts.ENDS[begin];rows=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=6,offset=i.address-0xC000) for i in dis.disassemble(begin,end,'h')]
  assert b''.join(bytes.fromhex(i['hex']) for i in rows)==raw[begin-0xC000:end-0xC000];added+=rows
  document,meaning=facts.DOCUMENTS['D3D',begin];path='Source/D3D/'+name+'.asm'
  lines=['                module D3D','                module '+name,'                ; Документация ['+meaning+'](../../Docs/'+document+'.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #'+format(begin-0xC000,'04X')+'..#'+format(end-0xC001,'04X')]
  for title,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['D3D',begin]):lines+=['                ; '+title+':']+['                ;   '+v for v in values]
  lines+=['                ; -----------------------------------------']
  for index,i in enumerate(rows):
   above,right=facts.COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];label='Entry' if index==0 else facts.LABELS.get(('D3D',i['address']),'')
   if label:
    symbol='D3D.'+name+'.'+label;assert symbol not in symbols;symbols[symbol]=i['address']
   op=facts.name_operands('D3D',begin,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
   if right:assert len(line)<80,(i,line);line=line.ljust(80)+'; '+right
   lines.append(line)
  lines+=['                endmodule','                endmodule'];continuation=getattr(facts,'CONTINUATIONS',{}).get(begin);target=next((f for f in functions if f['region']=='D3D' and f['address']==continuation),None)
  assert not continuation or target
  pending[ROOT/path]=format_function('\n'.join(lines)+'\n',target=target)
  function=dict(region='D3D',name=name,address=begin,slot=6,offset=begin-0xC000,end_offset=end-0xC000,path=path,description=description,semantic_status='described')
  if continuation:function['fragment_scope']='products_then_group';function['fallthrough_continuation']=continuation
  functions.append(function)
 old_bytes={i['address']+j for i in g['instructions'] for j in range(len(bytes.fromhex(i['hex'])))}
 assert all(i['address']+j not in old_bytes for i in added for j in range(len(bytes.fromhex(i['hex']))))
 g['instructions']=sorted(g['instructions']+added,key=lambda i:i['address']);g['roots']=sorted(set(g['roots'])|set(facts.FUNCTIONS))
 g['instruction_count']=len(g['instructions']);g['code_bytes']=sum(len(bytes.fromhex(i['hex'])) for i in g['instructions']);g['classified_fraction']=g['code_bytes']/g['total_bytes']
 validate_notes([g],{'D3D':facts.COMMENTS})
 # Проверка прямых целей по реальным зарегистрированным инструкциям, без переноса всей разведки в исходники.
 calls=set();branches=set();addresses={i['address'] for i in g['instructions']}
 g['unresolved']=[v for v in g['unresolved'] if v.get('target') not in addresses]
 for i in g['instructions']:
  match=re.fullmatch(r'(CALL|JP|JR|DJNZ) (?:[A-Z]+,)?#([0-9A-F]+)',i['operation'])
  if match:(calls if match[1]=='CALL' else branches).add(int(match[2],16))
 g['calls']=sorted(calls);g['branches']=sorted(branches)
 source_map=read('SourceMap');originals=[];replacements=((original_path,ranges),) if isinstance(original_path,str) else original_path
 p=ROOT/'Source/Files/06_D3D.inc';t=p.read_text('utf-8')
 # Проверка полного смежного покрытия каждого явно указанного заменяемого диапазона.
 for original_path,parts in replacements:
  old_range=next(e for e in source_map if e['path']==original_path);original=ROOT/original_path;originals.append(original)
  assert original.read_bytes()==raw[old_range['offset']:old_range['offset']+old_range['length']]
  mapped=[];include_lines=[];position=old_range['offset']
  for start,finish,entry,target in parts:
   assert start==position and start<finish;position=finish;blob=raw[start:finish];kind='code' if entry is not None else 'unclassified'
   mapped.append(dict(old_range,offset=start,length=finish-start,kind=kind,path=target,origin=entry,sha256=hashlib.sha256(blob).hexdigest()))
   if entry is None:binaries[ROOT/target]=blob;include_lines.append('                incbin "../Resources/06_D3D/'+Path(target).name+'"')
   else:
    assert entry==0xC000+start and facts.ENDS[entry]==0xC000+finish
    include_lines+=['                disp #'+format(entry,'04X'),'                include "../D3D/'+Path(target).name+'"','                ent']
   include_lines.append('                assert $ == #'+format(finish,'04X'))
  assert position==old_range['offset']+old_range['length'];idx=source_map.index(old_range);source_map[idx:idx+1]=mapped
  needle='                incbin "../Resources/06_D3D/'+original.name+'"';assert t.count(needle)==1;t=t.replace(needle,'\n'.join(include_lines))
 for name,number in getattr(facts,'ORDERED_INCLUDES',{}).items():
  needle='                include "../D3D/'+name+'.asm"';pattern=re.compile(re.escape(needle)+r'(?:[ \t]*;[^\n]*)?');assert len(pattern.findall(t))==1
  t=pattern.sub(needle.ljust(80)+'; ('+str(number)+') жёсткий порядок, последовательное исполнение',t)
 pending[p]=t
 if getattr(facts,'STATE',None):
  p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module '+facts.STATE_MODULE not in t;block='                module '+facts.STATE_MODULE+'\n'
  for pointer,label in facts.STATE.items():block+=(label.ljust(16)+'equ #'+format(pointer,'04X')).ljust(80)+'; '+facts.STATE_DESCRIPTIONS[label]+'\n'
  block+='                endmodule\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n')
 if getattr(facts,'CONSTANTS',None):
  p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8');assert 'module '+facts.CONST_MODULE not in t;block='                module '+facts.CONST_MODULE+'\n'
  for label,value,meaning in facts.CONSTANTS:block+=(label.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+meaning+'\n'
  block+='                endmodule\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');needle='| D3D | '+str(old_count)+' | '+str(old_count)+' |';assert t.count(needle)==1;new_count=old_count+len(facts.FUNCTIONS);t=t.replace(needle,'| D3D | '+str(new_count)+' | '+str(new_count)+' |')
 for begin,(name,description) in facts.FUNCTIONS.items():t+='\n| #'+format(begin,'04X')+', банк 4 | [D3D.'+name+'](../Source/D3D/'+name+'.asm) | '+description+' |\n'
 pending[p]=t;p=ROOT/'Docs/FunctionDetails/D3D.md';t=p.read_text('utf-8')
 for begin,(name,description) in facts.FUNCTIONS.items():document,_=facts.DOCUMENTS['D3D',begin];t+='\n['+name+'](../../Source/D3D/'+name+'.asm) — см. ['+document+'](../'+document+'.md).\n'
 pending[p]=t
 # Поиск реального владельца операнда, включая старший байт слова, по точным длинам уже выделенного кода.
 owners={i['address']+j:i for i in g['instructions'] for j in range(len(bytes.fromhex(i['hex'])))}
 modified=read('ModifiedCode');p=ROOT/'Docs/ModifiedCode.md';t=p.read_text('utf-8');writers=0
 for i in added:
  match=re.fullmatch(r'LD \(#([0-9A-F]+)\),(A|HL|DE|BC|SP)',i['operation'])
  if not match:continue
  target=int(match[1],16);size=1 if match[2]=='A' else 2;owner=owners[target];assert owner['address']<target and all(owners[target+j]['address']==owner['address'] for j in range(size))
  assert not any(v['region']=='D3D' and v['writer']==i['address'] and v['target']==target for v in modified)
  path=next(f['path'] for f in functions if f['region']=='D3D' and f['address']<=i['address']<0xC000+f['end_offset'])
  modified.append(dict(region='D3D',writer=i['address'],target=target,target_instruction=owner['address'],size=size,target_operation=owner['operation'],path=path));writers+=1
  t+='| D3D | #'+format(i['address'],'04X')+' | #'+format(target,'04X')+' | '+owner['operation']+' | ['+Path(path).name+'](../'+path+') |\n'
 pending[p]=t
 # Подключение фактов к существующим реестрам исследовательских операций.
 module=facts.__name__;upper=re.sub(r'(?<!^)(?=[A-Z])','_',tag).upper()
 for filename,extra in (
  ('Knowledge.py',"\nfrom "+module+" import FUNCTIONS as "+upper+"_FUNCTIONS\nFUNCTIONS['D3D'].update("+upper+"_FUNCTIONS)\n"),
  ('Contracts.py',"\nfrom "+module+" import CONTRACTS as "+upper+"_CONTRACTS\nCONTRACTS.update("+upper+"_CONTRACTS)\n"),
  ('D3DClipFacts.py',"\nfrom "+module+" import COMMENTS as "+upper+"_COMMENTS\nCOMMENTS.update("+upper+"_COMMENTS)\n"),
  ('SemanticNames.py',"\nfrom "+module+" import LABELS as "+upper+"_LABELS, DOCUMENTS as "+upper+"_DOCUMENTS, name_operands as "+tag.lower()+"_name_operands\nLABELS.update("+upper+"_LABELS)\nDOCUMENTS.update("+upper+"_DOCUMENTS)\n")):
  p=ROOT/('Tools/Disasm/Research/'+filename);t=p.read_text('utf-8');assert 'from '+module+' import' not in t
  if filename=='SemanticNames.py':
   needle='    operation = preview_vertex_group_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = '+tag.lower()+'_name_operands(region, function_address, operation)')
  pending[p]=t+extra
 flow[flow.index(previous)]=g;inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow))
 inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for report,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory),('ModifiedCode',modified)):pending[ROOT/('Tools/Disasm/Reports/'+report+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 plan=[]
 # Создание отдельного кандидата и проверка текущих файлов до применения.
 for p,value in {**pending,**binaries}.items():
  assert p.resolve().is_relative_to(ROOT);data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (candidate/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 for original in originals:
  target=history/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 for original in originals:
  assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(history/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,functions=len(facts.FUNCTIONS),instructions=len(added),code_bytes=sum(facts.ENDS[p]-p for p in facts.FUNCTIONS),registered_operand_writers=writers,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))

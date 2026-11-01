"""Применение проверенного музыкального блока и его пропускаемых JR байтов."""
from pathlib import Path
import collections, contextlib, hashlib, importlib, io, json, re, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from InspectZ80 import decoder
from SourcePresentation import format_function, continuity
from ValidateNotes import validate_notes


def apply(facts,tag,proof):
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read(proof)['passed'];candidate=ROOT/('Tools/Disasm/Research/Candidates/'+tag);history=ROOT/('Tools/Disasm/Research/History/Before'+tag);assert not candidate.exists() and not history.exists()
 pending={};removed={};functions=read('Functions');selected=[f for f in functions if f['region']=='Music' and f['address'] in facts.FUNCTIONS];assert len(selected)==len(facts.FUNCTIONS)
 old_described=sum(f['region']=='Music' and f['semantic_status']=='described' for f in functions);total=sum(f['region']=='Music' for f in functions)
 old_metadata={f['address']:dict(f) for f in selected};new_described=sum(f['semantic_status']!='described' for f in selected)
 renames={f['name']:facts.FUNCTIONS[f['address']][0] for f in selected}
 def rename(t):
  for old,new in getattr(facts,'OLD_LABELS',{}).items():t=t.replace('Music.'+old,'Music.'+new)
  for old,new in renames.items():t=re.sub(r'\bMusic\.'+old+r'\b','Music.'+new,t).replace('/Music/'+old+'.asm','/Music/'+new+'.asm')
  return t
 # Сопоставление старых областей с фактическими байтами, расширяется только соседний доказанный диапазон.
 sm=read('SourceMap');flow=read('ControlFlow');g=next(x for x in flow if x['name']=='Music');raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();memory=[0]*65536;memory[0xDB00:0xDB00+len(raw)]=raw;dis=decoder(memory);new_count=0;new_bytes=0;old_binaries={}
 for f in selected:
  end=facts.END_OFFSETS.get(f['address'],f['end_offset'])
  if end==f['end_offset']:continue
  gap=next(e for e in sm if e['slot']==10 and e['offset']==f['end_offset']);assert gap['kind']=='unclassified' and gap['offset']+gap['length']==end
  p=ROOT/gap['path'];assert p.read_bytes()==raw[gap['offset']:end];old_binaries[p]=p.read_bytes()
  new=dis.disassemble(0xDB00+gap['offset'],0xDB00+end,'h');assert sum(len(i.bytes) for i in new)==gap['length'] and all(not i.operation.startswith('DEFB') for i in new)
  for i in new:
   assert not any(x['address']==i.address for x in g['instructions']);g['instructions'].append(dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=10,offset=i.address-0xDB00))
  new_count+=len(new);new_bytes+=gap['length'];entry=next(e for e in sm if e['path']==f['path']);entry['length']=end-f['offset'];entry['sha256']=hashlib.sha256(raw[f['offset']:end]).hexdigest();sm.remove(gap);f['end_offset']=end
  p=ROOT/'Source/Files/10_MUZ1.inc';t=pending.get(p,p.read_bytes()).decode('utf-8');needle='                assert $ == #'+format(gap['offset'],'04X')+'\n                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/10_MUZ1/'+Path(gap['path']).name+'"';assert t.count(needle)==1;t=t.replace(needle,'');pending[p]=t.encode('utf-8')
 g['instructions'].sort(key=lambda x:(x['address'],x['slot'],x['offset']));g['instruction_count']+=new_count;g['code_bytes']+=new_bytes;g['classified_fraction']=g['code_bytes']/g['total_bytes'];validate_notes([g],{'Music':facts.COMMENTS});pending[ROOT/'Tools/Disasm/Reports/ControlFlow.json']=encoded(flow)
 # Обновление текущих ссылок без затрагивания контрольных снимков.
 for folder,glob in (('Source','*.asm'),('Source','*.inc'),('Includes','*.inc'),('Docs','*.md')):
  for p in (ROOT/folder).rglob(glob):
   old=pending.get(p,p.read_bytes()).decode('utf-8').replace('\r\n','\n');t=rename(old)
   if p==ROOT/'Docs/FunctionDetails/Music.md':
    for a,b in renames.items():t=t.replace('## '+a+'\n','## '+b+'\n')
   if t!=old:
    lines=t.splitlines()
    for n,(before,after) in enumerate(zip(old.splitlines(),lines)):
     code,sep,note=after.partition(';')
     if before!=after and sep and code.strip() and (code.lstrip().startswith('include ') or '@Music.' in code):assert len(code.rstrip())<80;lines[n]=code.rstrip().ljust(80)+';'+note
    pending[p]=('\n'.join(lines)+'\n').encode('utf-8')
 for f in selected:
  a=f['address'];name,description=facts.FUNCTIONS[a];old=ROOT/f['path'];pending.pop(old,None);path='Source/Music/'+name+'.asm';assert not (ROOT/path).exists() or ROOT/path==old
  if ROOT/path!=old:removed[old]=old.read_bytes()
  lines=['                module Music','                module '+name,'                ; Документация [отложенные состояния каналов](../../Docs/'+facts.DOCUMENT+'.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 10, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')]
  for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Music',a]):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
  lines+=['                ; -----------------------------------------']
  rows=[i for i in g['instructions'] if f['offset']<=i['offset']<f['end_offset']]
  for n,i in enumerate(rows):
   before,right=facts.COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in before];label='Entry' if n==0 else facts.LABELS.get(('Music',i['address']),'');op=facts.name_operands('Music',a,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
   if right:assert len(line)<80;line=line.ljust(80)+'; '+right
   lines.append(line)
  target_name,target_address=facts.CONTINUATIONS[a];target=dict(region='Music',name=target_name,path='Source/Music/'+target_name+'.asm');lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n',target).encode('utf-8');f.update(name=name,description=description,path=path,semantic_status='described',fallthrough_continuation=target_address,fragment_scope='modified_jr_then_next_physical_fragment')
  p=ROOT/'Source/Files/10_MUZ1.inc';t=pending.get(p,p.read_bytes()).decode('utf-8');needle='                include "../Music/'+name+'.asm"';line=next(l for l in t.splitlines() if l.startswith(needle));t=t.replace(line,needle.ljust(80)+'; ('+str(sorted(facts.FUNCTIONS).index(a))+') жёсткий порядок, последовательное исполнение');pending[p]=t.encode('utf-8')
 for stem,v in (('Functions',functions),('SourceMap',sm),('Symbols',read('Symbols')),('ModifiedCode',read('ModifiedCode'))):pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=rename(encoded(v).decode('utf-8')).encode('utf-8')
 symbols=json.loads(pending[ROOT/'Tools/Disasm/Reports/Symbols.json'].decode('utf-8'))
 for (region,a),label in facts.LABELS.items():assert any(f['address']<=a<0xDB00+f['end_offset'] for f in selected);owner=next(f for f in selected if f['address']<=a<0xDB00+f['end_offset']);symbols['Music.'+owner['name']+'.'+label]=a
 pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=encoded(symbols)
 inventory=read('Inventory');inventory.update(described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']!='described' for f in functions),instructions=inventory['instructions']+new_count);inventory['physical_bytes_by_kind']={k:sum(e['length'] for e in sm if e['kind']==k) for k in inventory['physical_bytes_by_kind']};inventory['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module '+facts.FIELD_MODULE not in t;block='\n                ; Исходные изменяемые операнды '+facts.FIELD_MODULE+', память не выделяется\n                module '+facts.FIELD_MODULE+'\n'
 for name,(a,note) in facts.FIELDS.items():assert len(name)<16;block+=name.ljust(16)+('equ #'+format(a,'04X')).ljust(64)+'; '+note+'\n'
 block+='                endmodule\n';assert t.count('                endif')==1;pending[p]=t.replace('                endif',block+'\n                endif').encode('utf-8')
 module=facts.__name__;prefix=tag.upper()
 for filename,extra in (
  ('Knowledge.py',"\nfrom "+module+" import FUNCTIONS as "+prefix+"_FUNCTIONS\nFUNCTIONS['Music'].update("+prefix+"_FUNCTIONS)\n"),
  ('Contracts.py','\nfrom '+module+' import CONTRACTS as '+prefix+'_CONTRACTS\nCONTRACTS.update('+prefix+'_CONTRACTS)\n'),
  ('MusicNotes.py','\nfrom '+module+' import COMMENTS as '+prefix+'_COMMENTS\nCOMMENTS.update('+prefix+'_COMMENTS)\n'),
  ('SemanticNames.py','\nfrom '+module+' import LABELS as '+prefix+'_LABELS, name_operands as '+tag.lower()+'_name_operands\nLABELS.update('+prefix+'_LABELS)\nDOCUMENTS.update({("Music",a):("'+facts.DOCUMENT+'","отложенные состояния каналов") for a in '+repr(tuple(facts.FUNCTIONS))+ '})\n')):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from '+module+' import' not in t
  if filename=='SemanticNames.py':needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = '+tag.lower()+'_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 p=ROOT/'Docs/Functions.md';t=pending.get(p,p.read_bytes()).decode('utf-8');needle='| Music | '+str(total)+' | '+str(old_described)+' |';assert t.count(needle)==1;t=t.replace(needle,'| Music | '+str(total)+' | '+str(old_described+new_described)+' |')
 for f in selected:
  description=old_metadata[f['address']]['description'];row='| #'+format(f['address'],'04X')+' | [Music.'+f['name']+'](../'+f['path']+') | '+description+' |';assert t.count(row)==1;t=t.replace(row,row.replace(description,f['description']))
 pending[p]=t.encode('utf-8');p=ROOT/'Docs/FunctionDetails/Music.md';t=pending.get(p,p.read_bytes()).decode('utf-8')
 for f in selected:
  start=t.index('## '+f['name']+'\n');end=t.find('\n## ',start+4);end=len(t) if end<0 else end;block=t[start:end].replace(old_metadata[f['address']]['description']+'.',f['description']+'.');block=re.sub(r'смещения `#[0-9A-F]+\.\.#[0-9A-F]+`','смещения `#'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')+'`',block);t=t[:start]+block+t[end:]
 pending[p]=t.encode('utf-8')
 # Регистрация наблюдаемых операндов новых инструкций, включая отключение JR его собственным телом.
 mod=json.loads(pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json'].decode('utf-8'));by_address={i['address']:i for i in g['instructions']}
 for i in g['instructions']:
  match=re.fullmatch(r'LD \(#([0-9A-F]{4})\),(A|HL|DE|BC)',i['operation'])
  if not match:continue
  a=int(match[1],16);size=1 if match[2]=='A' else 2;owner=next((j for j in g['instructions'] if j['address']<=a and a+size<=j['address']+len(bytes.fromhex(j['hex']))),None)
  if owner is None or not any(f['address']<=owner['address']<0xDB00+f['end_offset'] for f in selected):continue
  item=next((x for x in mod if x['region']=='Music' and x['writer']==i['address']),None)
  if item is None:
   source=next((f for f in functions if f['region']=='Music' and f['offset']<=i['offset']<f['end_offset']),None);assert source is not None
   mod.append(dict(region='Music',writer=i['address'],target=a,target_instruction=owner['address'],size=size,target_operation=owner['operation'],path=source['path'],target_region='Music',target_bank=3,target_slot=10,writer_bank=3))
 for item in mod:
  if item['region']=='Music' and item.get('target_source_classified') is False and item['target_instruction'] in by_address:
   owner=by_address[item['target_instruction']];assert item['target_original_hex']==owner['hex'];item['target_source_classified']=True
 pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=encoded(mod)
 # Согласование номеров всей затронутой физической цепочки, включая её прежние продолжения.
 following,order=continuity(functions,flow);p=ROOT/'Source/Files/10_MUZ1.inc';t=pending.get(p,p.read_bytes()).decode('utf-8')
 for f in functions:
  if f['region']!='Music' or f['path'] not in order:continue
  needle='                include "../Music/'+Path(f['path']).name+'"';line=next(l for l in t.splitlines() if l.startswith(needle));t=t.replace(line,needle.ljust(80)+'; ('+str(order[f['path']])+') жёсткий порядок, последовательное исполнение')
 pending[p]=t.encode('utf-8');plan=[]
 for p,data in pending.items():
  old=p.read_bytes() if p.exists() else None;plan.append((p,old,data));c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,old,data in plan:assert p.read_bytes()==old if old is not None else not p.exists()
 for p,old,data in plan:
  if old is not None:h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(old)
 for p,data in {**removed,**old_binaries}.items():h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(data)
 for p,old,data in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 for p,data in {**removed,**old_binaries}.items():assert p.resolve().is_relative_to((ROOT/'Source').resolve()) and p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
 result=dict(passed=True,functions_described=len(selected),new_instructions=new_count,new_code_bytes=new_bytes,instructions_changed=0,physical_bytes_preserved=True,assembly_executed=False);(ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).write_bytes(encoded(result));print(json.dumps(result,indent=2))


if __name__=='__main__':
 assert len(sys.argv)==4;apply(importlib.import_module(sys.argv[1]),sys.argv[2],sys.argv[3])

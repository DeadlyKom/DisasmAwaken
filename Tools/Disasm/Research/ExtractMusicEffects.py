"""Кандидат четырнадцати обработчиков и 21 физического указателя, без массового экспорта."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function
from InspectZ80 import decoder
from ValidateNotes import validate_notes
from MusicEffectTables import TABLES,render,parse
import MusicEffectFacts as facts


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 for proof in ('MusicEffectsVerification','MusicEffectsCompositionVerification','MusicGateSetterBVerification'):assert read(proof)['passed']
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MusicEffects';history=ROOT/'Tools/Disasm/Research/History/BeforeMusicEffects';assert not candidate.exists() and not history.exists();pending={};removed={}
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();memory=[0]*65536;memory[0xDB00:0xDB00+len(raw)]=raw;dis=decoder(memory)
 functions=read('Functions');flow=read('ControlFlow');g=next(x for x in flow if x['name']=='Music');new_functions=[];new_instructions=[];symbols=read('Symbols');code_ranges=[]
 for a,(name,description) in sorted(facts.FUNCTIONS.items()):
  b=facts.RANGES[a];path='Source/Music/'+name+'.asm';assert not (ROOT/path).exists() and not any(f['region']=='Music' and f['address']==a for f in functions)
  items=dis.disassemble(a,b,'h');assert sum(len(i.bytes) for i in items)==b-a and all(not i.operation.startswith('DEFB') for i in items)
  for i in items:assert not any(v['address']==i.address for v in g['instructions']);new_instructions.append(dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=10,offset=i.address-0xDB00))
  f=dict(region='Music',name=name,address=a,slot=10,offset=a-0xDB00,end_offset=b-0xDB00,path=path,description=description,semantic_status='described');new_functions.append(f);symbols['Music.'+name+'.Entry']=a;code_ranges.append((a,b,path,'code'))
  lines=['                module Music','                module '+name,'                ; Документация [музыкальные эффекты](../../Docs/MusicEffects.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 10, файловые смещения #'+format(a-0xDB00,'04X')+'..#'+format(b-0xDB01,'04X')]
  for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Music',a]):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
  lines+=['                ; -----------------------------------------']
  for n,i in enumerate(items):
   before,right=facts.COMMENTS.get(i.address,([],None));assert right is None;lines+=['                ; '+v for v in before];lines.append(('Entry:'.ljust(16) if n==0 else ' '*16)+facts.name_operands('Music',a,i.operation.replace(',',', ')))
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
 g['instructions']+=new_instructions;g['instructions'].sort(key=lambda i:(i['address'],i['slot'],i['offset']));g['roots']=sorted(set(g['roots'])|set(facts.FUNCTIONS));g['instruction_count']+=len(new_instructions);g['code_bytes']+=sum(b-a for a,b,path,kind in code_ranges);g['classified_fraction']=g['code_bytes']/g['total_bytes'];g['branches']=sorted(set(g['branches'])|{0xDDF2});validate_notes([g],{'Music':facts.COMMENTS})
 first=min(n for n,f in enumerate(functions) if f['region']=='Music');last=max(n for n,f in enumerate(functions) if f['region']=='Music')+1;assert all(f['region']=='Music' for f in functions[first:last]);functions[first:last]=sorted(functions[first:last]+new_functions,key=lambda f:f['address'])
 table_ranges=[]
 for table in TABLES:
  module,path,a,entries=table;text,bindings=render(raw,table);assert not (ROOT/path).exists();pending[ROOT/path]=text.encode('utf-8');symbols.update(bindings);table_ranges.append((a,a+len(entries)*2,path,'typed'));data,labels=parse(text,table,{k.upper():v for k,v in symbols.items()});assert data==raw[a-0xDB00:a-0xDB00+len(data)]
 # Деление только шести доказанных исходных бинарных диапазонов, оставшиеся байты сохраняются явно.
 all_ranges=sorted(code_ranges+table_ranges);sm=read('SourceMap');updated=[];source_file=ROOT/'Source/Files/10_MUZ1.inc';file_text=source_file.read_text('utf-8');changed_resources=0
 for e in sm:
  if e['slot']!=10:updated.append(e);continue
  a=0xDB00+e['offset'];b=a+e['length'];parts=[v for v in all_ranges if a<=v[0]<b]
  if not parts:updated.append(e);continue
  assert e['kind']=='unclassified' and all(v[1]<=b for v in parts);oldpath=ROOT/e['path'];assert oldpath.read_bytes()==raw[e['offset']:e['offset']+e['length']];removed[oldpath]=oldpath.read_bytes();cursor=a;pieces=[]
  for x,y,path,kind in parts:
   assert cursor<=x
   if cursor<x:
    keep='Source/Resources/10_MUZ1/BeforeEffectPointersA.bin';assert cursor==0xDBA0 and x==0xDDC0 and not (ROOT/keep).exists();pending[ROOT/keep]=raw[cursor-0xDB00:x-0xDB00];pieces.append((cursor,x,keep,'unclassified'))
   pieces.append((x,y,path,kind));cursor=y
  assert cursor==b
  lines=[]
  for n,(x,y,path,kind) in enumerate(pieces):
   updated.append(dict(slot=10,offset=x-0xDB00,length=y-x,kind=kind,path=path,origin=x if kind!='unclassified' else None,sha256=hashlib.sha256(raw[x-0xDB00:y-0xDB00]).hexdigest()))
   if n:lines.append('                assert $ == #'+format(x-0xDB00,'04X'))
   if kind=='unclassified':lines+=['                ; Unknown, прежние байты перед первым словом эффектов A сохранены без интерпретации','                incbin "../Resources/10_MUZ1/'+Path(path).name+'"']
   else:lines+=['                disp #'+format(x,'04X'),'                include "../Music/'+('Data/' if kind=='typed' else '')+Path(path).name+'"','                ent']
  needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/10_MUZ1/'+oldpath.name+'"';assert file_text.count(needle)==1;file_text=file_text.replace(needle,'\n'.join(lines));changed_resources+=1
 assert changed_resources==6;pending[source_file]=file_text.encode('utf-8')
 p=ROOT/'Includes/Structs/Include.inc';t=p.read_text('utf-8');assert 'struct FMusicEffectTarget' not in t;block='\n                ; Два физических байта адреса отложенного обработчика, код команды задан положением записи\n                struct FMusicEffectTarget\nHandler         dw #0000                                                        ; адрес обработчика в исходном банке MUZ1\n                ends\n                assert FMusicEffectTarget == 2\n';assert t.count('                endif')==1;pending[p]=t.replace('                endif',block+'\n                endif').encode('utf-8')
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module MusicEffectState' not in t;block='\n                ; Исходные изменяемые операнды музыкальных команд, память не выделяется\n                module MusicEffectState\n'
 for name,(a,note) in facts.FIELDS.items():assert len(name)<16;block+=name.ljust(16)+('equ #'+format(a,'04X')).ljust(64)+'; '+note+'\n'
 block+='                endmodule\n';assert t.count('                endif')==1;pending[p]=t.replace('                endif',block+'\n                endif').encode('utf-8')
 p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8');assert 'module MusicCommandConst' not in t;block='\n                module MusicCommandConst\nEnableDeferred  equ #06                                                         ; LD B,n вместо JR в переключателе отложенной команды\nSkipToneLimit   equ #1D                                                         ; смещение JR для обхода сравнения с целевой нотой\n                endmodule\n';assert t.count('                endif')==1;pending[p]=t.replace('                endif',block+'\n                endif').encode('utf-8')
 p=ROOT/'Source/Music/UnknownE583.asm';t=p.read_text('utf-8');assert t.count('LD (#E6EC), A')==1;line=next(l for l in t.splitlines() if 'LD (#E6EC), A' in l);pending[p]=t.replace(line,line.replace('(#E6EC)','(@MusicEffectState.PreviousNoteC)')).encode('utf-8')
 # Реестр записей учитывает также доказанные косвенные LD (HL),A и LD (HL),n.
 modified=read('ModifiedCode');writers=[]
 for i in new_instructions:
  m=re.fullmatch(r'LD \(#([0-9A-F]{4})\),(A|HL|DE|BC)',i['operation'])
  if m:writers.append((i['address'],int(m[1],16),1 if m[2]=='A' else 2))
 writers += [(0xE642,0xDE4D,1),(0xE693,0xDEDB,1),(0xE6EB,0xE2B9,1)]
 for writer,target,size in writers:
  assert not any(v['region']=='Music' and v['writer']==writer for v in modified);owner=next((i for i in g['instructions'] if i['address']<=target and target+size<=i['address']+len(bytes.fromhex(i['hex']))),None);extracted=owner is not None
  if owner is None:
   address=facts.UNEXTRACTED_TARGETS[target];i=dis.disassemble(address,address+1,'h')[0];assert address<target and target+size<=address+len(i.bytes);owner=dict(address=address,operation=i.operation,hex=i.bytes.hex())
  f=next(f for f in new_functions if f['address']<=writer<0xDB00+f['end_offset']);modified.append(dict(region='Music',writer=writer,target=target,target_instruction=owner['address'],size=size,target_operation=owner['operation'],path=f['path'],target_region='Music',target_bank=3,target_slot=10,writer_bank=3,target_source_classified=extracted,target_original_hex=owner['hex'],indirect_target_proved=writer in (0xE642,0xE693,0xE6EB)))
 for stem,value in (('Functions',functions),('ControlFlow',flow),('SourceMap',updated),('Symbols',symbols),('ModifiedCode',modified)):pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encoded(value)
 inventory=read('Inventory');inventory['fragments']+=14;inventory['described']+=14;inventory['instructions']+=len(new_instructions);inventory['physical_bytes_by_kind']={k:sum(e['length'] for e in updated if e['kind']==k) for k in inventory['physical_bytes_by_kind']};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in updated));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 for filename,extra in (
  ('Knowledge.py',"\nfrom MusicEffectFacts import FUNCTIONS as MUSIC_EFFECT_FUNCTIONS\nFUNCTIONS['Music'].update(MUSIC_EFFECT_FUNCTIONS)\n"),
  ('Contracts.py','\nfrom MusicEffectFacts import CONTRACTS as MUSIC_EFFECT_CONTRACTS\nCONTRACTS.update(MUSIC_EFFECT_CONTRACTS)\n'),
  ('MusicNotes.py','\nfrom MusicEffectFacts import COMMENTS as MUSIC_EFFECT_COMMENTS\nCOMMENTS.update(MUSIC_EFFECT_COMMENTS)\n'),
  ('SemanticNames.py','\nfrom MusicEffectFacts import name_operands as music_effect_name_operands\nDOCUMENTS.update({("Music",a):("MusicEffects","отложенные музыкальные команды") for a in '+repr(tuple(facts.FUNCTIONS))+'})\n')):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from MusicEffectFacts import' not in t
  if filename=='SemanticNames.py':needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = music_effect_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 for rel,prefix in (('Docs/Functions.md','../'),('Docs/FunctionDetails/Music.md','../../')):
  p=ROOT/rel;t=p.read_text('utf-8')
  if rel=='Docs/Functions.md':assert '| Music | 30 | 24 |' in t;t=t.replace('| Music | 30 | 24 |','| Music | 44 | 38 |')
  for f in new_functions:t+='\n'+('## '+f['name']+'\n\n' if 'FunctionDetails' in rel else '')+'[Music.'+f['name']+']('+prefix+f['path']+') — '+f['description']+'. [Договор и проверка]('+('../' if 'FunctionDetails' in rel else '')+'MusicEffects.md).\n'
  pending[p]=t.encode('utf-8')
 p=ROOT/'Docs/ModifiedCode.md';t=p.read_text('utf-8')
 for writer,target,size in writers:
  x=next(x for x in modified if x['region']=='Music' and x['writer']==writer);t+='\n| Music | #'+format(writer,'04X')+' | #'+format(target,'04X')+' | '+x['target_operation']+(' , целевой код ещё не выделен' if not x['target_source_classified'] else '')+' | ['+Path(x['path']).name+'](../'+x['path']+') |\n'
 pending[p]=t.encode('utf-8');plan=[]
 for p,data in pending.items():
  old=p.read_bytes() if p.exists() else None;plan.append((p,old,data));c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,old,data in plan:assert p.read_bytes()==old if old is not None else not p.exists()
 for p,old,data in plan:
  if old is not None:h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(old)
 for p,data in removed.items():h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(data)
 for p,old,data in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 for p,data in removed.items():assert p.resolve().is_relative_to((ROOT/'Source/Resources/10_MUZ1').resolve()) and p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
 result=dict(passed=True,new_functions=14,new_instructions=len(new_instructions),new_code_bytes=235,typed_pointer_records=21,typed_pointer_bytes=42,unextracted_target_operands_explicit=True,physical_bytes_preserved=True,assembly_executed=False);(ROOT/'Tools/Disasm/Reports/MusicEffectsClassification.json').write_bytes(encoded(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()

"""Разделение синтеза и завершений A/B, выделение трёх доказанных хвостов ограничения тона."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from InspectZ80 import decoder
from SourcePresentation import format_function,continuity
from ValidateNotes import validate_notes
from MusicSynthesisNotes import build as build_notes
import MusicSynthesisFacts as facts


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 proof=read('MusicSynthesisVerification');assert proof['passed'] and proof['per_channel_body_boundaries_checked'];assert read('MusicChannelABFinishVerification')['passed'] and read('OriginalMusicSynthesisVerification')['passed']
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MusicSynthesis';history=ROOT/'Tools/Disasm/Research/History/BeforeMusicSynthesis';assert not candidate.exists() and not history.exists();pending={};removed={}
 functions=read('Functions');old_functions=[f.copy() for f in functions if f['region']=='Music' and 0xDFE3<=f['address']<0xE2CB];assert {f['name'] for f in old_functions}=={'RenderChannelA','UnknownE0CD','UnknownE1CD'}
 old_paths={f['path'] for f in old_functions};new=[]
 for address,(name,description) in sorted(facts.FUNCTIONS.items()):new.append(dict(region='Music',name=name,address=address,slot=10,offset=address-0xDB00,end_offset=facts.ENDS[address]-0xDB00,path='Source/Music/'+name+'.asm',description=description,semantic_status='described'))
 music=[f for f in functions if f['region']=='Music' and f['path'] not in old_paths]+new;first=min(i for i,f in enumerate(functions) if f['region']=='Music');last=max(i for i,f in enumerate(functions) if f['region']=='Music')+1;assert all(f['region']=='Music' for f in functions[first:last]);functions[first:last]=sorted(music,key=lambda f:f['address'])
 def owner(a):return next((f for f in new if f['address']<=a<0xDB00+f['end_offset']),None)
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();memory=[0]*65536;memory[0xDB00:0xDB00+len(raw)]=raw;dis=decoder(memory);flow=read('ControlFlow');g=next(v for v in flow if v['name']=='Music');added=[]
 for a,b in ((0xE0B0,0xE0CD),(0xE1B0,0xE1CD),(0xE2AE,0xE2CB)):
  decoded=dis.disassemble(a,b,'h');assert sum(len(i.bytes) for i in decoded)==b-a
  for i in decoded:assert not i.operation.startswith('DEFB') and not any(j['address']==i.address for j in g['instructions']);added.append(dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=10,offset=i.address-0xDB00))
 g['instructions']+=added;g['instructions'].sort(key=lambda i:(i['address'],i['slot'],i['offset']));g['roots']=sorted(set(g['roots'])|set(facts.FUNCTIONS));g['instruction_count']+=len(added);g['code_bytes']+=87;g['classified_fraction']=g['code_bytes']/g['total_bytes']
 for kind,stem in (('calls','CALL'),('branches','(?:JP|JR|DJNZ)')):g[kind]=sorted({int(m[1],16) for i in g['instructions'] if (m:=re.fullmatch(stem+r' (?:[A-Z]+,)?#([0-9A-F]+)',i['operation']))})
 # Имена внутренних целей меняются только внутри трёх прежних музыкальных пространств.
 symbols=read('Symbols');renames={};labels={}
 for key,a in list(symbols.items()):
  if not key.startswith(('Music.RenderChannelA.','Music.UnknownE0CD.','Music.UnknownE1CD.')):continue
  f=owner(a);assert f is not None;label='Entry' if a==f['address'] else facts.LABELS.get(('Music',a),key.rsplit('.',1)[1]);new_key='Music.'+f['name']+'.'+label;renames[key]=new_key;del symbols[key];assert symbols.get(new_key,a)==a;symbols[new_key]=a;labels[a]=label
 for (region,a),label in facts.LABELS.items():
  f=owner(a);assert f is not None;symbols['Music.'+f['name']+'.'+label]=a;labels[a]=label
 for f in new:symbols['Music.'+f['name']+'.Entry']=f['address'];labels[f['address']]='Entry'
 def rename(t):
  for a,b in sorted(renames.items(),key=lambda v:-len(v[0])):t=re.sub(r'\b'+re.escape(a)+r'\b',b,t)
  for old,name in (('UnknownE0CD','FinishChannelA'),('UnknownE1CD','FinishChannelB')):t=t.replace('Music.'+old,'Music.'+name).replace('/Music/'+old+'.asm','/Music/'+name+'.asm')
  return t
 for folder,glob in (('Source','*.asm'),('Source','*.inc'),('Includes','*.inc'),('Docs','*.md')):
  for p in (ROOT/folder).rglob(glob):
   t=p.read_text('utf-8');u=rename(t)
   if u!=t:
    lines=u.splitlines()
    for n,(before,after) in enumerate(zip(t.splitlines(),lines)):
     code,sep,note=after.partition(';')
     if before!=after and sep and code.strip() and ('@Music.' in code or code.lstrip().startswith('include ')):assert len(code.rstrip())<80;lines[n]=code.rstrip().ljust(80)+';'+note
    pending[p]=('\n'.join(lines)+'\n').encode('utf-8')
 # Повторно используются существующие привязки музыкального банка, совпадения адресов других банков не учитываются.
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');available={};module=None
 for line in t.splitlines():
  code=line.partition(';')[0].strip();m=re.fullmatch(r'module (\w+)',code,re.I)
  if m:module=m[1]
  m=re.fullmatch(r'(\w+)\s+equ\s+#([0-9A-F]+)',code,re.I)
  if m and module and module.startswith('Music'):available.setdefault(int(m[2],16),module+'.'+m[1])
 blocks=[]
 for channel,pf in enumerate(facts.PROFILES):
  fields=[];module='MusicSynthesis'+pf['name']
  for key,name in facts.FIELD_NAMES.items():
   a=pf[key]
   if a not in available:available[a]=module+'.'+name;fields.append((name,a,facts.FIELD_NOTES[key]))
  if fields:
   blocks+=['                ; Исходные операнды синтеза '+pf['name']+', память не выделяется','                module '+module]
   for name,a,note in fields:assert len(name)<16;blocks.append(name.ljust(16)+('equ #'+format(a,'04X')).ljust(64)+'; '+note)
   blocks+=['                endmodule','']
 for a,name,note in ((0xDFE4,'EnvelopeSeed','исходный операнд младшего байта общего вклада огибающей'),(0xDFE8,'MixerSeed','исходный младший байт IX, сохраняется при пропуске A')):
  if a not in available:available[a]='MusicSynthesisState.'+name;blocks+=['                module MusicSynthesisState',name.ljust(16)+('equ #'+format(a,'04X')).ljust(64)+'; '+note,'                endmodule','']
 assert t.count('                endif')==1;pending[p]=t.replace('                endif','\n'+'\n'.join(blocks)+'\n                endif').encode('utf-8');facts.OPERANDS.update(available)
 notes=build_notes(new,g['instructions'],facts);validate_notes([g],{'Music':notes});facts_path=ROOT/'Tools/Disasm/Research/MusicSynthesisFacts.py';pending[facts_path]=(facts_path.read_text('utf-8')+'\n# Привязки существующего музыкального банка, зафиксированные при точечном выпуске.\nOPERANDS.update('+repr(available)+')\nCOMMENTS.update('+repr(notes)+')\n').encode('utf-8')
 targets={f['address']:'Music.'+f['name']+'.Entry' for f in functions if f['region']=='Music'}
 for f in new:
  path=ROOT/f['path'];pending.pop(path,None);address=f['address'];lines=['                module Music','                module '+f['name'],'                ; Документация [синтез трёх каналов](../../Docs/MusicSynthesis.md)','                ; -----------------------------------------','                ; '+f['description'],'                ; исходная запись 10, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')]
  for heading,items in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Music',address]):lines+=['                ; '+heading+':']+['                ;   '+v for v in items]
  lines+=['                ; -----------------------------------------'];rows=[i for i in g['instructions'] if f['offset']<=i['offset']<f['end_offset']]
  for i in rows:
   before,right=notes.get(i['address'],([],None));lines+=['                ; '+v for v in before];op=i['operation'].replace(',',', ')
   def named(m):
    a=int(m[1],16);f_owner=owner(a)
    if f_owner is not None and a in labels:return '@Music.'+f_owner['name']+'.'+labels[a]
    if a in targets:return '@'+targets[a]
    if ('Music',a) in symbols:return '@'+symbols['Music',a]
    target=next((k for k,v in symbols.items() if k.startswith('Music.') and v==a),None)
    return '@'+target if target else m[0]
   if op.startswith(('JP ','JR ','CALL ','DJNZ ')):op=re.sub(r'#([0-9A-F]{4})',named,op)
   op=facts.name_operands('Music',address,op);label=labels.get(i['address'],'');line=((label+':').ljust(16) if label else ' '*16)+op
   if right:assert len(line)<80;line=line.ljust(80)+'; '+right
   lines.append(line)
  lines+=['                endmodule','                endmodule'];following=None
  if f['name'].startswith('Finish'):
   following=next(v for v in functions if v['region']=='Music' and v['address']==0xDB00+f['end_offset']);f.update(fallthrough_continuation=following['address'],fragment_scope='completed_channel_then_next_synthesis')
  pending[path]=format_function('\n'.join(lines)+'\n',following).encode('utf-8')
 sm=read('SourceMap');affected=[e for e in sm if e['slot']==10 and 0x4E3<=e['offset']<0x7CB];assert len(affected)==6 and sum(e['length'] for e in affected)==0x7CB-0x4E3
 start=sm.index(affected[0]);assert sm[start:start+6]==affected
 for e in affected:
  if e['kind']=='unclassified':p=ROOT/e['path'];assert p.read_bytes()==raw[e['offset']:e['offset']+e['length']];removed[p]=p.read_bytes()
 sm[start:start+6]=[dict(slot=10,offset=f['offset'],length=f['end_offset']-f['offset'],kind='code',path=f['path'],origin=f['address'],sha256=hashlib.sha256(raw[f['offset']:f['end_offset']]).hexdigest()) for f in new]
 for old in old_functions:
  if old['name'].startswith('Unknown'):p=ROOT/old['path'];pending.pop(p,None);removed[p]=p.read_bytes()
 p=ROOT/'Source/Files/10_MUZ1.inc';t=pending.get(p,p.read_bytes()).decode('utf-8').replace('\r\n','\n');a=t.index('                assert $ == #04E3\n');b=t.index('                assert $ == #07CB\n',a);lines=[]
 for f in new:lines+=['                assert $ == #'+format(f['offset'],'04X'),'                disp #'+format(f['address'],'04X'),'                include "../Music/'+Path(f['path']).name+'"','                ent']
 t=t[:a]+'\n'.join(lines)+'\n'+t[b:];following,order=continuity(functions,flow)
 for f in functions:
  if f['region']!='Music' or f['path'] not in order:continue
  needle='                include "../Music/'+Path(f['path']).name+'"';line=next(l for l in t.splitlines() if l.startswith(needle));t=t.replace(line,needle.ljust(80)+'; ('+str(order[f['path']])+') жёсткий порядок, последовательное исполнение')
 pending[p]=t.encode('utf-8')
 p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8');assert 'module MusicSampleConst' not in t;constants=(('FixedLevelBit',0),('AccumShiftBit',5),('AccumToneBit',6),('AdjustUpBit',6),('AdjustBit',7),('EnvShiftBit',7),('VolumePage',0xDC),('PitchPage',0xDD),('HighNibbleMask',0xF0),('ShiftMask',0x1F),('MaxAdjust',0x1F),('NibbleBoundary',0x10),('MaxLevel',0x0F),('MixerMaskA',9),('MixerMaskB',0x12),('MixerMaskC',0x24));block=['                module MusicSampleConst']
 constant_notes=('бит пропуска добавления маски огибающей','бит сохранения шумового либо огибающего вклада','бит сохранения тональной поправки','единица выбирает увеличение поправки уровня','бит изменения поправки уровня из сэмпла','выбор вклада огибающей и бита старшей тройки микшера','старший байт страницы таблицы громкости','старший байт страницы слов периодов нот','маска старшей тетрады для смещения уровня и раскрытия знака','пять младших битов сдвига огибающей после SRL E','предел увеличения поправки уровня 31','граница 16 при ограничении уровня и раскрытии знака','максимальный вычисленный базовый уровень 15','два формируемых бита микшера канала A','два формируемых бита микшера канала B','два формируемых бита микшера канала C')
 for (name,value),note in zip(constants,constant_notes):assert len(name)<16;block.append(name.ljust(16)+('equ #'+format(value,'02X')).ljust(64)+'; '+note)
 block+=['                endmodule',''];assert t.count('                endif')==1;pending[p]=t.replace('                endif','\n'+'\n'.join(block)+'\n                endif').encode('utf-8')
 # Согласование владельцев самомодификации и ранее явно не выделенных целевых операндов.
 modified=read('ModifiedCode');by_address={i['address']:i for i in g['instructions']}
 for x in modified:
  if x['region']!='Music':continue
  f=owner(x['writer'])
  if f is not None:x['path']=f['path']
  target=by_address.get(x.get('target_instruction'))
  if target is not None and 'target_source_classified' in x:x['target_source_classified']=True
 for i in added:
  m=re.fullmatch(r'LD \(#([0-9A-F]{4})\),(A|HL)',i['operation'])
  if not m:continue
  target=int(m[1],16);size=1 if m[2]=='A' else 2;target_i=next(j for j in g['instructions'] if j['address']<target and target+size<=j['address']+len(bytes.fromhex(j['hex'])));f=owner(i['address']);assert not any(x['region']=='Music' and x['writer']==i['address'] for x in modified);modified.append(dict(region='Music',writer=i['address'],target=target,target_instruction=target_i['address'],size=size,target_operation=target_i['operation'],path=f['path'],target_region='Music',target_bank=3,target_slot=10,writer_bank=3,target_source_classified=True,target_original_hex=target_i['hex']))
 for stem,value in (('Functions',functions),('ControlFlow',flow),('SourceMap',sm),('Symbols',symbols),('ModifiedCode',modified)):pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encoded(value)
 inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']!='described' for f in functions),instructions=inventory['instructions']+len(added));inventory['physical_bytes_by_kind']={k:sum(e['length'] for e in sm if e['kind']==k) for k in inventory['physical_bytes_by_kind']};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in sm));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 for filename,extra in (
  ('Knowledge.py',"\nfrom MusicSynthesisFacts import FUNCTIONS as MUSIC_SYNTHESIS_FUNCTIONS\nFUNCTIONS['Music'].update(MUSIC_SYNTHESIS_FUNCTIONS)\n"),
  ('Contracts.py','\nfrom MusicSynthesisFacts import CONTRACTS as MUSIC_SYNTHESIS_CONTRACTS\nCONTRACTS.update(MUSIC_SYNTHESIS_CONTRACTS)\n'),
  ('MusicNotes.py','\nfrom MusicSynthesisFacts import COMMENTS as MUSIC_SYNTHESIS_COMMENTS\nCOMMENTS.update(MUSIC_SYNTHESIS_COMMENTS)\n'),
  ('SemanticNames.py','\nfrom MusicSynthesisFacts import LABELS as MUSIC_SYNTHESIS_LABELS, name_operands as music_synthesis_name_operands\nLABELS.update(MUSIC_SYNTHESIS_LABELS)\nDOCUMENTS.update({("Music",a):("MusicSynthesis","синтез трёх каналов") for a in '+repr(tuple(facts.FUNCTIONS))+'})\n')):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from MusicSynthesisFacts import' not in t
  if filename=='SemanticNames.py':needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = music_synthesis_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 p=ROOT/'Tools/Disasm/Research/Analyze.py';t=p.read_text('utf-8');needle='0xDF02}';assert t.count(needle)==1;pending[p]=t.replace(needle,'0xDF02, 0xE0B0, 0xE1B0, 0xE2AE}').encode('utf-8')
 p=ROOT/'Docs/Functions.md';t=pending.get(p,p.read_bytes()).decode('utf-8');assert '| Music | 44 | 38 |' in t;t=t.replace('| Music | 44 | 38 |','| Music | 46 | 42 |')
 for f in new:
  row='| #'+format(f['address'],'04X')+' | [Music.'+f['name']+'](../'+f['path']+') | '+f['description']+' |';matches=[l for l in t.splitlines() if l.startswith('| #'+format(f['address'],'04X')+' |') and '](../'+f['path']+')' in l]
  if matches:assert len(matches)==1;t=t.replace(matches[0],row)
  else:t+='\n'+row+'\n'
 pending[p]=t.encode('utf-8');p=ROOT/'Docs/FunctionDetails/Music.md';t=pending.get(p,p.read_bytes()).decode('utf-8').replace('\r\n','\n')
 for old in old_functions:
  name=old['name'];a=t.index('## '+name+'\n');b=t.find('\n## ',a+4);assert b>a;f=owner(old['address']);block='## '+f['name']+'\n\n[Music.'+f['name']+'](../../'+f['path']+') — '+f['description']+'. [Алгоритм и договор](../MusicSynthesis.md).\n';t=t[:a]+block+t[b:]
 for f in new:
  if f['name'] not in ('RenderChannelB','RenderChannelC'):continue
  t+='\n## '+f['name']+'\n\n[Music.'+f['name']+'](../../'+f['path']+') — '+f['description']+'. [Алгоритм](../MusicSynthesis.md).\n'
 pending[p]=t.encode('utf-8');p=ROOT/'Docs/ModifiedCode.md';t=pending.get(p,p.read_bytes()).decode('utf-8');lines=t.splitlines()
 for n,line in enumerate(lines):
  m=re.match(r'\| Music \| #([0-9A-F]{4}) \|',line)
  if not m:continue
  writer=int(m[1],16);f=owner(writer)
  if f is not None:line=re.sub(r'\[[^\]]+\.asm\]\(\.\./Source/Music/[^)]+\)', '['+Path(f['path']).name+'](../'+f['path']+')',line)
  item=next((x for x in modified if x['region']=='Music' and x['writer']==writer),None)
  if item and item.get('target_source_classified'):line=line.replace(' , целевой код ещё не выделен','')
  lines[n]=line
 for i in added:
  x=next((v for v in modified if v['region']=='Music' and v['writer']==i['address']),None)
  if x:lines.append('| Music | #'+format(x['writer'],'04X')+' | #'+format(x['target'],'04X')+' | '+x['target_operation']+' | ['+Path(x['path']).name+'](../'+x['path']+') |')
 pending[p]=('\n'.join(lines)+'\n').encode('utf-8');plan=[]
 for p,data in pending.items():
  old=p.read_bytes() if p.exists() else None;plan.append((p,old,data));c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,old,data in plan:assert p.read_bytes()==old if old is not None else not p.exists()
 for p,old,data in plan:
  if old is not None:h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(old)
 for p,data in removed.items():h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(data)
 for p,old,data in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 for p,data in removed.items():assert p.resolve().is_relative_to((ROOT/'Source').resolve()) and p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
 result=dict(passed=True,described_sources=5,new_functions=2,new_instructions=len(added),new_code_bytes=87,physical_bytes_preserved=True,assembly_executed=False);(ROOT/'Tools/Disasm/Reports/MusicSynthesisClassification.json').write_bytes(encoded(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()

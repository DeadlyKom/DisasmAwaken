"""Выделение доказанных завершения C и вывода AY, Unknown остатка сохраняется."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function,continuity
from ValidateNotes import validate_notes
from MusicNotes import COMMENTS as MUSIC_COMMENTS
import MusicAyOutputFacts as facts


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('MusicAyFrameVerification')['passed'] and read('MusicChannelCFinishVerification')['passed']
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MusicAyOutput';history=ROOT/'Tools/Disasm/Research/History/BeforeMusicAyOutput';assert not candidate.exists() and not history.exists();pending={}
 functions=read('Functions');old=next(f for f in functions if f['region']=='Music' and f['address']==0xE2CB);assert old['path']=='Source/Music/UnknownE2CB.asm' and old['end_offset']==0x939;oldpath=ROOT/old['path'];oldbytes=oldpath.read_bytes();start_index=functions.index(old)
 ranges=((0xE2CB,0xE2EB),(0xE2EB,0xE37C),(0xE37C,0xE439));new=[]
 for a,b in ranges:
  name,description=facts.FUNCTIONS[a];new.append(dict(region='Music',name=name,address=a,slot=10,offset=a-0xDB00,end_offset=b-0xDB00,path='Source/Music/'+name+'.asm',description=description,semantic_status='unknown' if description.startswith('Unknown') else 'described',fallthrough_continuation=b,fragment_scope='original_sequential_music_stage'))
 functions[start_index:start_index+1]=new
 def owner(a):return next((f for f in new if f['address']<=a<0xDB00+f['end_offset']),None)
 symbols=read('Symbols');symbol_renames={};labels={}
 for key,a in list(symbols.items()):
  if not key.startswith('Music.UnknownE2CB.'):continue
  f=owner(a);assert f is not None;label='Entry' if a==f['address'] else facts.LABELS.get(a,key.rsplit('.',1)[1]);replacement='Music.'+f['name']+'.'+label;symbol_renames[key]=replacement;del symbols[key];assert symbols.get(replacement,a)==a;symbols[replacement]=a;labels[a]=label
 for f in new:symbols['Music.'+f['name']+'.Entry']=f['address'];labels[f['address']]='Entry'
 def rename(t):
  for a,b in sorted(symbol_renames.items(),key=lambda v:-len(v[0])):t=re.sub(r'\b'+re.escape(a)+r'\b',b,t)
  return t.replace('Music.UnknownE2CB','Music.FinishChannelC').replace('/Music/UnknownE2CB.asm','/Music/FinishChannelC.asm')
 for folder,glob in (('Source','*.asm'),('Source','*.inc'),('Includes','*.inc'),('Docs','*.md')):
  for p in (ROOT/folder).rglob(glob):
   t=p.read_text('utf-8');updated=rename(t)
   if updated!=t:
    lines=updated.splitlines()
    for n,(before,after) in enumerate(zip(t.splitlines(),lines)):
     code,sep,note=after.partition(';')
     if before!=after and sep and code.strip() and ('@Music.' in code or code.lstrip().startswith('include ')):assert len(code.rstrip())<80;lines[n]=code.rstrip().ljust(80)+';'+note
    pending[p]=('\n'.join(lines)+'\n').encode('utf-8')
 pending.pop(oldpath,None);flow=read('ControlFlow');g=next(x for x in flow if x['name']=='Music');g['roots']=sorted(set(g['roots'])|set(facts.FUNCTIONS));validate_notes([g],{'Music':facts.COMMENTS});comments={**MUSIC_COMMENTS,**facts.COMMENTS};entry_targets={f['address']:'Music.'+f['name']+'.Entry' for f in functions if f['region']=='Music'}
 for f in new:
  a=f['address'];lines=['                module Music','                module '+f['name'],'                ; Документация [огибающая и вывод AY](../../Docs/MusicAyOutput.md)','                ; -----------------------------------------','                ; '+f['description'],'                ; исходная запись 10, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')]
  contract=facts.CONTRACTS.get(('Music',a),(['Unknown, полный договор последующего разбора паттернов ещё не доказан'],['исходный поток управления, границы следующего разбора описаны в документации'],['Unknown, полный договор последующего разбора паттернов ещё не доказан'],['выделение проверенного вывода AY не доказывает оставшийся алгоритм']))
  for heading,values in zip(('In','Out','Corrupt','Note'),contract):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
  lines+=['                ; -----------------------------------------'];rows=[i for i in g['instructions'] if f['offset']<=i['offset']<f['end_offset']]
  for i in rows:
   before,right=comments.get(i['address'],([],None));lines+=['                ; '+v for v in before];op=i['operation'].replace(',',', ')
   def target(m):
    v=int(m[1],16);part=owner(v)
    if part is not None and v in labels:return '@Music.'+part['name']+'.'+labels[v]
    return '@'+entry_targets[v] if v in entry_targets else m[0]
   if op.startswith(('JP ','JR ','CALL ','DJNZ ')):op=re.sub(r'#([0-9A-F]{4})',target,op)
   op=facts.name_operands('Music',a,op);label=labels.get(i['address'],'');line=((label+':').ljust(16) if label else ' '*16)+op
   if right:assert len(line)<80;line=line.ljust(80)+'; '+right
   lines.append(line)
  following=next(x for x in functions if x['region']=='Music' and x['address']==0xDB00+f['end_offset']);lines+=['                endmodule','                endmodule'];pending[ROOT/f['path']]=format_function('\n'.join(lines)+'\n',following).encode('utf-8')
 sm=read('SourceMap');entry=next(x for x in sm if x['path']==old['path']);n=sm.index(entry);raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();sm[n:n+1]=[dict(slot=10,offset=f['offset'],length=f['end_offset']-f['offset'],kind='code',path=f['path'],origin=f['address'],sha256=hashlib.sha256(raw[f['offset']:f['end_offset']]).hexdigest()) for f in new]
 modified=read('ModifiedCode')
 for item in modified:
  if item['region']=='Music' and owner(item['writer']) is not None:item['path']=owner(item['writer'])['path']
 for stem,value in (('Functions',functions),('ControlFlow',flow),('SourceMap',sm),('Symbols',symbols),('ModifiedCode',modified)):pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encoded(value)
 inventory=read('Inventory');inventory['fragments']+=2;inventory['described']+=2;inventory['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 p=ROOT/'Source/Files/10_MUZ1.inc';t=pending.get(p,p.read_bytes()).decode('utf-8').replace('\r\n','\n');needle=next(l for l in t.splitlines() if l.startswith('                include "../Music/FinishChannelC.asm"'));block='                include "../Music/FinishChannelC.asm"\n                ent\n                assert $ == #07EB\n                disp #E2EB\n                include "../Music/OutputAyFrame.asm"\n                ent\n                assert $ == #087C\n                disp #E37C\n                include "../Music/UnknownE37C.asm"';t=t.replace(needle,block);following,order=continuity(functions,flow)
 for f in functions:
  if f['region']!='Music' or f['path'] not in order:continue
  needle='                include "../Music/'+Path(f['path']).name+'"';line=next(l for l in t.splitlines() if l.startswith(needle));t=t.replace(line,needle.ljust(80)+'; ('+str(order[f['path']])+') жёсткий порядок, последовательное исполнение')
 pending[p]=t.encode('utf-8')
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module MusicAyState' not in t;block='\n                ; Исходные операнды и буфер аппаратного вывода AY, память не выделяется\n                module MusicAyState\n'
 for name,(a,note) in facts.FIELDS.items():block+=name.ljust(16)+('equ #'+format(a,'04X')).ljust(64)+'; '+note+'\n'
 block+='                endmodule\n';assert t.count('                endif')==1;pending[p]=t.replace('                endif',block+'\n                endif').encode('utf-8')
 for filename,extra in (
  ('Knowledge.py',"\nfrom MusicAyOutputFacts import FUNCTIONS as MUSIC_AY_OUTPUT_FUNCTIONS\nFUNCTIONS['Music'].update(MUSIC_AY_OUTPUT_FUNCTIONS)\n"),
  ('Contracts.py','\nfrom MusicAyOutputFacts import CONTRACTS as MUSIC_AY_OUTPUT_CONTRACTS\nCONTRACTS.update(MUSIC_AY_OUTPUT_CONTRACTS)\n'),
  ('MusicNotes.py','\nfrom MusicAyOutputFacts import COMMENTS as MUSIC_AY_OUTPUT_COMMENTS\nCOMMENTS.update(MUSIC_AY_OUTPUT_COMMENTS)\n'),
  ('SemanticNames.py','\nfrom MusicAyOutputFacts import name_operands as music_ay_output_name_operands\nDOCUMENTS.update({("Music",a):("MusicAyOutput","огибающая и вывод AY") for a in (0xE2CB,0xE2EB,0xE37C)})\nLABELS.update('+repr({('Music',a):label for a,label in labels.items() if label!='Entry'})+')\n')):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from MusicAyOutputFacts import' not in t
  if filename=='SemanticNames.py':needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = music_ay_output_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 p=ROOT/'Docs/Functions.md';t=pending.get(p,p.read_bytes()).decode('utf-8');assert '| Music | 28 | 22 |' in t;t=t.replace('| Music | 28 | 22 |','| Music | 30 | 24 |');needle='| #E2CB | [Music.FinishChannelC](../Source/Music/FinishChannelC.asm) | Unknown, назначение этого фрагмента ещё не установлено |';assert t.count(needle)==1;t=t.replace(needle,needle.replace('Unknown, назначение этого фрагмента ещё не установлено',new[0]['description']))
 for f in new[1:]:t+='\n| #'+format(f['address'],'04X')+' | [Music.'+f['name']+'](../'+f['path']+') | '+f['description']+' |\n'
 pending[p]=t.encode('utf-8');p=ROOT/'Docs/FunctionDetails/Music.md';t=pending.get(p,p.read_bytes()).decode('utf-8').replace('\r\n','\n');a=t.index('## UnknownE2CB\n');b=t.find('\n## ',a+4);assert b>a;block=''
 for f in new:block+='## '+f['name']+'\n\n[Music.'+f['name']+'](../../'+f['path']+') — '+f['description']+'.\n\nВход #'+format(f['address'],'04X')+', физические смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')+'. [Алгоритм и границы проверки](../MusicAyOutput.md).\n\n'
 pending[p]=(t[:a]+block+t[b:]).encode('utf-8')
 plan=[]
 for p,data in pending.items():
  olddata=p.read_bytes() if p.exists() else None;plan.append((p,olddata,data));c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,olddata,data in plan:assert p.read_bytes()==olddata if olddata is not None else not p.exists()
 for p,olddata,data in plan:
  if olddata is not None:h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(olddata)
 h=history/oldpath.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(oldbytes)
 for p,olddata,data in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert oldpath.resolve().is_relative_to((ROOT/'Source/Music').resolve()) and oldpath.read_bytes()==oldbytes==h.read_bytes();oldpath.unlink()
 result=dict(passed=True,new_fragments=2,described_contracts=2,remaining_unknown_continuation=True,instructions_changed=0,physical_bytes_preserved=True,assembly_executed=False);(ROOT/'Tools/Disasm/Reports/MusicAyOutputClassification.json').write_bytes(encoded(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()

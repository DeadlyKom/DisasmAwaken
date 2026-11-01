"""Точечное применение двух доказанных музыкальных блоков, без массового экспорта."""
from pathlib import Path
import contextlib, io, json, re, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import MusicEnvelopeStagingFacts as facts


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('MusicEnvelopeStagingVerification')['passed']
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MusicEnvelopeStaging';history=ROOT/'Tools/Disasm/Research/History/BeforeMusicEnvelopeStaging';assert not candidate.exists() and not history.exists()
 pending={};removed={};functions=read('Functions');selected=[f for f in functions if f['region']=='Music' and f['address'] in facts.FUNCTIONS];assert len(selected)==2
 def rename(t):
  for old,new in facts.RENAMES.items():
   t=re.sub(r'\bMusic\.'+old+r'\b','Music.'+new,t).replace('/Music/'+old+'.asm','/Music/'+new+'.asm')
  for old,new in facts.LABEL_RENAMES.items():
   old=old.replace('UnknownDF47','StageEnvelopeAndNoise');t=t.replace('Music.'+old,'Music.'+new)
  return t
 # Поиск текущих ссылок, история и кандидаты намеренно не переписываются.
 for folder,glob in (('Source','*.asm'),('Source','*.inc'),('Includes','*.inc'),('Docs','*.md')):
  for p in (ROOT/folder).rglob(glob):
   old=p.read_text('utf-8');t=rename(old)
   if p==ROOT/'Docs/FunctionDetails/Music.md':
    for a,b in facts.RENAMES.items():t=t.replace('## '+a+'\n','## '+b+'\n')
   if t!=old:
    lines=t.splitlines()
    for n,(before,after) in enumerate(zip(old.splitlines(),lines)):
     code,sep,note=after.partition(';')
     if before!=after and sep and code.strip() and (code.lstrip().startswith('include ') or '@Music.' in code):
      assert len(code.rstrip())<80;lines[n]=code.rstrip().ljust(80)+';'+note
    pending[p]=('\n'.join(lines)+'\n').encode('utf-8')
 flow=read('ControlFlow');g=next(x for x in flow if x['name']=='Music');validate_notes([g],{'Music':facts.COMMENTS})
 for f in selected:
  a=f['address'];name,description=facts.FUNCTIONS[a];old=ROOT/f['path'];removed[old]=old.read_bytes();pending.pop(old,None);path='Source/Music/'+name+'.asm';assert not (ROOT/path).exists()
  lines=['                module Music','                module '+name,'                ; Документация [подготовка огибающей](../../Docs/MusicEnvelopeStaging.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 10, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')]
  for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Music',a]):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
  lines+=['                ; -----------------------------------------']
  rows=[i for i in g['instructions'] if f['offset']<=i['offset']<f['end_offset']]
  for n,i in enumerate(rows):
   before,right=facts.COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in before];label='Entry' if n==0 else facts.LABELS.get(('Music',i['address']),'');op=facts.name_operands('Music',a,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
   if right:assert len(line)<80;line=line.ljust(80)+'; '+right
   lines.append(line)
  target=dict(region='Music',name='CommitEnvelopeSlide' if a==0xDF47 else 'AdvancePatternA',path='Source/Music/'+('CommitEnvelopeSlide' if a==0xDF47 else 'AdvancePatternA')+'.asm')
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n',target).encode('utf-8');f.update(name=name,description=description,path=path,semantic_status='described')
 # Обновление только текущих реестров, остальные банковые пространства не переименовываются.
 for stem,v in (('Functions',functions),('SourceMap',read('SourceMap')),('Symbols',read('Symbols')),('ModifiedCode',read('ModifiedCode'))):pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=rename(encoded(v).decode('utf-8')).encode('utf-8')
 symbols=json.loads(pending[ROOT/'Tools/Disasm/Reports/Symbols.json'].decode('utf-8'))
 for a,target in facts.TARGETS.items():
  if target.startswith('Music.'):assert symbols[target]==a
 inventory=read('Inventory');inventory['described']+=2;inventory['unknown']-=2;pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module MusicEnvelopeState' not in t
 fields={**{v.rsplit('.',1)[1]:a for a,v in facts.TARGETS.items() if v.startswith('MusicEnvelopeState.')},'Base':0xDF50,'Noise':0xDF67,'Step':0xDF6E,'Delay':0xDF74}
 notes={'AyShape':'однократный буфер формы AY13, ноль пропускает аппаратную запись','AyNoise':'базовый шум в буфере AY6 до добавления вклада сэмплов','EnvelopeBase':'базовый период огибающей в изменяемом операнде','Shape':'ожидающая форма, ненулевой байт перезапускает период и скольжение','SlideOffset':'накопленное слово скольжения огибающей','SlideCounter':'текущий байтовый счётчик задержки скольжения','Phase':'числовая стадия распределённого разбора каналов B и C','SlideStep':'слово шага для прибавления к смещению огибающей','SlideReload':'задержка перезагрузки после применения шага','SlideGate':'код команды, 18 пропускает отложенную установку, 06 включает её','Base':'ожидающий базовый период для новой формы огибающей','Noise':'ожидающий базовый шум текущей строки паттерна','Step':'ожидающий шаг отложенной команды скольжения','Delay':'ожидающая задержка отложенной команды скольжения'}
 block='\n                ; Изменяемые операнды огибающей MUZ1 и исходный буфер AY, память не выделяется\n                module MusicEnvelopeState\n'
 for name,a in fields.items():block+=name.ljust(16)+('equ #'+format(a,'04X')).ljust(64)+'; '+notes[name]+'\n'
 block+='                endmodule\n';assert t.count('                endif')==1;t=t.replace('                endif',block+'\n                endif');pending[p]=t.encode('utf-8')
 for filename,extra in (
  ('Knowledge.py',"\nfrom MusicEnvelopeStagingFacts import FUNCTIONS as MUSIC_ENVELOPE_FUNCTIONS\nFUNCTIONS['Music'].update(MUSIC_ENVELOPE_FUNCTIONS)\n"),
  ('Contracts.py',"\nfrom MusicEnvelopeStagingFacts import CONTRACTS as MUSIC_ENVELOPE_CONTRACTS\nCONTRACTS.update(MUSIC_ENVELOPE_CONTRACTS)\n"),
  ('MusicNotes.py',"\nfrom MusicEnvelopeStagingFacts import COMMENTS as MUSIC_ENVELOPE_COMMENTS\nCOMMENTS.update(MUSIC_ENVELOPE_COMMENTS)\n"),
  ('SemanticNames.py',"\nfrom MusicEnvelopeStagingFacts import LABELS as MUSIC_ENVELOPE_LABELS, name_operands as music_envelope_name_operands\nLABELS.update(MUSIC_ENVELOPE_LABELS)\nDOCUMENTS.update({('Music',a):('MusicEnvelopeStaging','подготовка огибающей') for a in (0xDF47,0xDF70)})\n")):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from MusicEnvelopeStagingFacts import' not in t
  if filename=='SemanticNames.py':
   needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = music_envelope_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 for rel in ('Docs/Functions.md','Docs/FunctionDetails/Music.md'):
  p=ROOT/rel;t=pending.get(p,p.read_bytes()).decode('utf-8')
  if rel=='Docs/Functions.md':assert '| Music | 27 | 13 |' in t;t=t.replace('| Music | 27 | 13 |','| Music | 27 | 15 |')
  for a,(name,description) in facts.FUNCTIONS.items():t+='\n['+name+']('+('../../' if 'FunctionDetails' in rel else '../')+'Source/Music/'+name+'.asm) — '+description+'.\n'
  pending[p]=t.encode('utf-8')
 plan=[]
 for p,data in pending.items():
  old=p.read_bytes() if p.exists() else None;plan.append((p,old,data));c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,old,data in plan:assert p.read_bytes()==old if old is not None else not p.exists()
 for p,old,data in plan:
  if old is not None:h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(old)
 for p,data in removed.items():h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(data)
 for p,old,data in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 for p,data in removed.items():assert p.resolve().is_relative_to((ROOT/'Source/Music').resolve()) and p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
 report=dict(passed=True,functions_described=2,instructions_changed=0,physical_bytes_preserved=True,scoped_candidate_and_history=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MusicEnvelopeStagingClassification.json').write_bytes(encoded(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

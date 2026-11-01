"""Комментарии только к доказанным внутренним счётчикам, Unknown родителей сохраняется."""
from pathlib import Path
import contextlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from ValidateNotes import validate_notes
import MusicGateTickFacts as facts


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 reports=ROOT/'Tools/Disasm/Reports';read=lambda n:json.loads((reports/(n+'.json')).read_text('utf-8'));assert read('MusicGateTicksVerification')['passed'];functions=read('Functions');g=next(x for x in read('ControlFlow') if x['name']=='Music');validate_notes([g],{'Music':facts.COMMENTS});pending={}
 for name,start,stop,amplitude,counter,state,disabled,enabled,parent in facts.PROFILES:
  f=next(x for x in functions if x['region']=='Music' and x['address']==parent);assert f['semantic_status']=='unknown';p=ROOT/f['path'];text=p.read_text('utf-8');rows=[i for i in g['instructions'] if start<=i['address']<stop];first='Point'+format(start,'04X')+':';last='Point'+format(stop,'04X')+':';a=text.index(first);b=text.index(last,a);old=text[a:b];labels={line[16:].split(';',1)[0].strip():line[:16] for line in old.splitlines() if line[:16].strip() and not line.lstrip().startswith(';')};lines=[]
  # Сохранение всех исходных меток, меняются только комментарии и имена доказанных операндов.
  for i in rows:
   op=i['operation'].replace(',',', ');before,right=facts.COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in before]
   target=next((line for line in old.splitlines() if line[:16].strip() and line[:16].strip().rstrip(':')=='Point'+format(i['address'],'04X')),None);prefix=target[:16] if target else ' '*16
   # Переходы сохраняют прежние глобальные имена своих физических целей.
   if op.startswith(('JR ','JP ')):
    import re
    op=re.sub(r'#([0-9A-F]{4})',lambda m:'@Music.'+f['name']+'.Point'+m[1],op)
   op=facts.name_operands('Music',parent,op);line=prefix+op
   if right:assert len(line)<80;line=line.ljust(80)+'; '+right
   lines.append(line)
   if op.startswith(('JP ','JR ')):lines.append('')
  text=text[:a]+'\n'.join(lines)+'\n'+text[b:];needle='; Документация [Music](../../Docs/FunctionDetails/Music.md)';assert text.count(needle)==1;text=text.replace(needle,needle+'\n                ; Разобран внутренний [счётчик чередования](../../Docs/MusicGateTicks.md), общий синтез ещё требует разбора');pending[p]=text.encode('utf-8')
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module MusicGateState' not in t;block='\n                ; Исходные операнды счётчиков и байты буфера AY, память не выделяется\n                module MusicGateState\n'
 for name,(a,note) in facts.FIELDS.items():assert len(name)<16;block+=name.ljust(16)+('equ #'+format(a,'04X')).ljust(64)+'; '+note+'\n'
 block+='                endmodule\n';assert t.count('                endif')==1;pending[p]=t.replace('                endif',block+'\n                endif').encode('utf-8')
 for filename,extra in (
  ('MusicNotes.py','\nfrom MusicGateTickFacts import COMMENTS as MUSIC_GATE_TICK_COMMENTS\nCOMMENTS.update(MUSIC_GATE_TICK_COMMENTS)\n'),
  ('SemanticNames.py','\nfrom MusicGateTickFacts import name_operands as music_gate_tick_name_operands\n')):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from MusicGateTickFacts import' not in t
  if filename=='SemanticNames.py':needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = music_gate_tick_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MusicGateNotes';history=ROOT/'Tools/Disasm/Research/History/BeforeMusicGateNotes';assert not candidate.exists() and not history.exists();plan=[]
 for p,data in pending.items():
  old=p.read_bytes();plan.append((p,old,data));c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,old,data in plan:assert p.read_bytes()==old
 for p,old,data in plan:h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(old)
 for p,old,data in plan:p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 result=dict(passed=True,partial_internal_blocks=3,parent_unknown_status_preserved=True,instructions_changed=0,physical_bytes_preserved=True,assembly_executed=False);(reports/'MusicGateNotesVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()

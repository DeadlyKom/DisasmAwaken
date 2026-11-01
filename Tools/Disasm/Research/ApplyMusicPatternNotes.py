"""Только проверенная маршрутизация декодеров, Unknown полных обработчиков сохраняется."""
from pathlib import Path
import contextlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import operation
from ValidateNotes import validate_notes


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 assert read('MusicPatternDispatchVerification')['passed'];g=next(x for x in read('ControlFlow') if x['name']=='Music');functions=read('Functions');pending={};comments={}
 purposes={0xF0:'выбрать совместную команду сэмпла и орнамента',0xD0:'выбрать сэмпл либо завершение строки',0xC0:'выбрать громкость либо выключение ноты',0xB0:'выбрать подкоманду огибающей либо задержки',0x50:'выбрать ноту',0x40:'выбрать орнамент',0x20:'выбрать базовый шум',0x10:'выбрать совместную команду огибающей и сэмпла'}
 profiles=(('A',0xE439,0xE462),('B',0xE4E6,0xE511),('C',0xE583,0xE5B2))
 for name,start,end in profiles:
  thresholds=(0xF0,0xD0,0xC0,0xB0,0x50,0x40,0x20,0x10) if name=='B' else (0xF0,0xD0,0xC0,0xB0,0x50,0x40,0x10);rows=[i for i in g['instructions'] if start<=i['address']<end];branches=[i for i in rows if i['operation'].startswith('JR C,')];assert len(branches)==len(thresholds)
  high=255
  for i,low in zip(branches,thresholds):
   previous=rows[rows.index(i)-1];assert previous['operation'].startswith('ADD A,');span=format(low,'02X')+'..'+format(high,'02X');comments[previous['address']]=(['проверка исходного диапазона '+span+' добавлением с переносом'],None);comments[i['address']]=([],'переход, если исходный код '+span+', '+purposes[low]);high=low-1
  comments[start]=(['подготовка шагов порогового декодирования, B=10 и C=20'],None)
  for i in rows:
   if i['operation']=='PUSH HL':comments[i['address']]=(['помещение адреса отложенного обработчика в стек, он будет исполнен последующим RET после окончания строки'],None)
   if i['operation']=='LD A,(#E2B9)':comments[i['address']]=(['сохранение текущей ноты C для последующей отложенной команды скольжения'],None)
  f=next(f for f in functions if f['region']=='Music' and f['address']==start);assert f['semantic_status']=='unknown';p=ROOT/f['path'];t=p.read_text('utf-8');function_rows=[i for i in g['instructions'] if f['offset']<=i['offset']<f['end_offset']];out=[];index=0
  for line in t.splitlines():
   op=operation(line)
   if not op or op.lower().startswith(('module ','endmodule')):out.append(line);continue
   i=function_rows[index];index+=1;assert op.split()[0]==i['operation'].split()[0]
   if i['address'] in comments:
    before,right=comments[i['address']];out+=['                ; '+v for v in before]
    if right:line=line.partition(';')[0].rstrip().ljust(80)+'; '+right
   out.append(line)
  assert index==len(function_rows);text='\n'.join(out)+'\n';needle='; Документация [Music](../../Docs/FunctionDetails/Music.md)';assert text.count(needle)==1;text=text.replace(needle,needle+'\n                ; Проверена [маршрутизация команд](../../Docs/MusicPatternDispatch.md), полный алгоритм обработчиков ещё требует разбора');pending[p]=text.encode('utf-8')
 validate_notes([g],{'Music':comments});p=ROOT/'Tools/Disasm/Research/MusicPatternDispatchFacts.py';assert not p.exists();pending[p]=('"""Проверенные диапазоны команд, полные алгоритмы декодеров ещё не установлены."""\nCOMMENTS='+repr(comments)+'\n').encode('utf-8')
 p=ROOT/'Tools/Disasm/Research/MusicNotes.py';t=p.read_text('utf-8');assert 'from MusicPatternDispatchFacts import' not in t;pending[p]=(t+'\nfrom MusicPatternDispatchFacts import COMMENTS as MUSIC_PATTERN_DISPATCH_COMMENTS\nCOMMENTS.update(MUSIC_PATTERN_DISPATCH_COMMENTS)\n').encode('utf-8')
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MusicPatternNotes';history=ROOT/'Tools/Disasm/Research/History/BeforeMusicPatternNotes';assert not candidate.exists() and not history.exists();plan=[]
 for p,data in pending.items():
  old=p.read_bytes() if p.exists() else None;plan.append((p,old,data));c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,old,data in plan:assert p.read_bytes()==old if old is not None else not p.exists()
 for p,old,data in plan:
  if old is not None:h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(old)
 for p,old,data in plan:p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 result=dict(passed=True,partial_decoders=3,precise_range_conditions=len([x for x in comments.values() if x[1]]),parent_unknown_status_preserved=True,instructions_changed=0,physical_bytes_preserved=True,assembly_executed=False);(ROOT/'Tools/Disasm/Reports/MusicPatternNotesVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()

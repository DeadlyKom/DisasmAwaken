"""Точечное оформление доказанной части двух Unknown-фрагментов без повышения их статуса."""
from pathlib import Path
import json,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from ClipCaseFacts import COMMENTS,LABELS,name_operands
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify


def main(spec=None):
 spec=spec or {};comments=spec.get('comments',COMMENTS);labels=spec.get('labels',LABELS);operands=spec.get('operands',name_operands)
 verify();history=ROOT/'Tools/Disasm/Research/History'/spec.get('history','BeforeClipCaseNotes');assert not history.exists()
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));validate_notes(flow,{'Map':comments})
 functions=json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_text('utf-8'));symbols_path=ROOT/'Tools/Disasm/Reports/Symbols.json';symbols=json.loads(symbols_path.read_text('utf-8'))
 selected=[f for f in functions if f['region']=='Map' and f['address'] in spec.get('addresses',(0xD48B,0xD4DD))];replacements={}
 for f in selected:
  for (region,address),label in labels.items():
   if region=='Map' and f['address']<=address<f['address']+f['end_offset']-f['offset']:
    old='Map.'+f['name']+'.Point'+format(address,'04X');new='Map.'+f['name']+'.'+label
    assert symbols[old]==address;replacements[old]=new;symbols[new]=symbols.pop(old)
 def rename(text):
  for before,after in replacements.items():text=text.replace(before,after)
  return text
 pending={}
 for f in selected:
  path=ROOT/f['path'];text=path.read_text('utf-8');decoded=[i for g in flow if g['name']=='Map' for i in g['instructions'] if i['slot']==7 and f['offset']<=i['offset']<f['end_offset']]
  it=iter(decoded);lines=[]
  for line in text.splitlines():
   if line.strip() and not line.lstrip().startswith(';') and not line[16:].strip().lower().startswith(('module ','endmodule')):
    item=next(it);before,right=comments.get(item['address'],([],None));lines.extend(' '*16+'; '+comment for comment in before)
    old_label=line[:16].strip().removesuffix(':');label=labels.get(('Map',item['address']),old_label)
    operation,separator,previous_right=line[16:].partition(';')
    if right is None and separator:right=previous_right.strip()
    operation=operands('Map',f['address'],rename(operation.strip()))
    line=((label+':').ljust(16) if label else ' '*16)+operation
    if right:line=line.ljust(80)+'; '+right
   lines.append(rename(line))
  assert next(it,None) is None
  text='\n'.join(lines)+'\n';link='; Подробный разбор ['+spec.get('title','условия случаев и два возврата')+'](../../Docs/'+spec.get('document','ClipCases')+'.md)'
  marker='; -----------------------------------------';text=text.replace(marker,link+'\n'+marker,1);pending[path]=format_function(text,None)
 # Сравнение отдельного кандидата перед заменой двух файлов, внешние ссылки меняются только по точным именам.
 for path in (ROOT/'Source').rglob('*.asm'):
  if path in pending:continue
  text=path.read_text('utf-8');updated=rename(text)
  if updated!=text:pending[path]=updated
 candidate=ROOT/'Tools/Disasm/Research/Candidates'/spec.get('candidate','ClipCaseNotesScoped')
 for path,text in pending.items():
  target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,'utf-8')
 for path in [*pending,symbols_path]:
  target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 for path,text in pending.items():path.write_text(text,'utf-8')
 symbols_path.write_text(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n','utf-8');verify()
 print('Partial semantics documented, Unknown status preserved, '+str(len(replacements))+' proven table-entry names')


if __name__=='__main__':main()

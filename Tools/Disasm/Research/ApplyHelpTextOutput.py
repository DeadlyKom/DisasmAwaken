"""Одноразовое исправление имени HELP-входа, договоры печати и границы двух текстовых ресурсов."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
import HelpTextOutputFacts as facts
from SourcePresentation import format_function
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('HelpTextOutputVerification')['passed'];candidate=ROOT/'Tools/Disasm/Research/Candidates/HelpTextOutputScoped';history=ROOT/'Tools/Disasm/Research/History/BeforeHelpTextOutput'
 assert not candidate.exists() and not history.exists();pending={};removed={}
 def rename(t):return t.replace('Help.FormatNumber','Help.PrintCrRecordAndRows').replace('Help/FormatNumber.asm','Help/PrintCrRecordAndRows.asm').replace('## FormatNumber\n','## PrintCrRecordAndRows\n')
 for folder,pattern in (('Source','*.asm'),('Source','*.inc'),('Docs','*.md')):
  for p in (ROOT/folder).rglob(pattern):
   t=p.read_text('utf-8');u=rename(t)
   if t!=u:pending[p]=u.encode('utf-8')
 functions=read('Functions');group=next(g for g in read('ControlFlow') if g['name']=='Help')
 notes={0xDB42:'подготовка начальной позиции вывода строки независимо от прежнего курсора',0xDB49:'расчёт адреса двухбайтовой записи без проверки входного индекса',
  0xDB4E:'чтение рабочего указателя из физической таблицы строк',0xDB52:'проверка нулевого слова, оно обозначает неиспользованную запись',
  0xDB5B:'сохранение полного входного HL в DE, для выбора используется только L',0xDB66:'поиск L+1 разделителей CR от начала заголовков и печать оставшегося потока',
  0xDB69:'расчёт числа строк по изменению байтового Y, статус печати не проверяется',0xDB75:'сохранение счётчика и его флагов в альтернативном AF',
  0xDB76:'обновление Y для последующего вывода, X остаётся после печати'}
 for f in functions:
  if f['region']!='Help' or f['address'] not in facts.FUNCTIONS:continue
  a=f['address'];name,description=facts.FUNCTIONS[a];oldpath=ROOT/f['path'];path='Source/Help/'+name+'.asm'
  if oldpath!=ROOT/path:removed[oldpath]=oldpath.read_bytes();pending.pop(oldpath,None)
  lines=['                module Help','                module '+name,'                ; Документация [таблица строк и CR-заголовки](../../Docs/HelpTextOutput.md)','                ; -----------------------------------------','                ; '+description,'                ; запись 8, банк 7, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')]
  for title,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Help',a]):lines+=['                ; '+title+':']+['                ;   '+v for v in values]
  lines+=['                ; -----------------------------------------']
  for i in group['instructions']:
   if i['slot']!=8 or not f['offset']<=i['offset']<f['end_offset']:continue
   pc=i['address']
   if pc in notes:lines.append('                ; '+notes[pc])
   op=facts.name_operands('Help',a,i['operation'].replace(',',', '));line=('Entry:'.ljust(16) if pc==a else ' '*16)+op
   if op=='RET Z':line=line.ljust(80)+'; выход, если указатель строки равен нулю'
   lines.append(line)
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n').encode('utf-8');f.update(name=name,path=path,description=description)
 for name,value in (('Functions',functions),('Symbols',read('Symbols')),('ModifiedCode',read('ModifiedCode'))):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=rename(encode(value).decode('utf-8')).encode('utf-8')
 source_map=read('SourceMap');old=next(e for e in source_map if e['slot']==8 and e['offset']==0x87C);oldpath=ROOT/old['path'];raw=oldpath.read_bytes();assert len(raw)==3972;removed[oldpath]=raw
 parts=((0x87C,0x8E2,'SectionTitles.bin','binary_resource'),(0x8E2,5921,'SectionTexts.bin','binary_resource'),(5921,6144,'SectorTail.bin','unclassified'))
 entries=[]
 for start,end,name,kind in parts:
  data=raw[start-0x87C:end-0x87C];path='Source/Resources/08_HELP/'+name;pending[ROOT/path]=data
  entries.append(dict(slot=8,offset=start,length=end-start,kind=kind,path=path,origin=0xDB00+start if kind=='binary_resource' else None,sha256=hashlib.sha256(data).hexdigest()))
 index=source_map.index(old);source_map[index:index+1]=entries;pending[ROOT/'Tools/Disasm/Reports/SourceMap.json']=rename(encode(source_map).decode('utf-8')).encode('utf-8')
 p=ROOT/'Source/Files/08_HELP.inc';t=pending.get(p,p.read_bytes()).decode('utf-8');needle='                ; Unknown, область E37C..F2FF требует отдельного разбора потребителей\n                incbin "../Resources/08_HELP/UnclassifiedAfterLineCache.bin"';assert t.count(needle)==1
 pending[p]=t.replace(needle,'                ; CR-заголовки разделов, потребитель PrintCrRecordAndRows, адрес E37C\n                incbin "../Resources/08_HELP/SectionTitles.bin"\n                assert $ == #08E2\n                ; LF-записи справки, потребитель IndexTextLines, адрес E3E2\n                incbin "../Resources/08_HELP/SectionTexts.bin"\n                assert $ == #1721\n                ; Unknown, секторный хвост после логической длины, исходные байты сохранены\n                incbin "../Resources/08_HELP/SectorTail.bin"').encode('utf-8')
 inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(e['length'] for e in source_map if e['kind']==kind) for kind in inventory['physical_bytes_by_kind']};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encode(inventory)
 p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8');block='                module HelpTextConst\n'+('SectionTitles   equ #E37C').ljust(80)+'; банк 7, начало физического CR-потока заголовков разделов справки\n                endmodule\n\n';assert t.count('                endif\n')==1;pending[p]=t.replace('                endif\n',block+'                endif\n').encode('utf-8')
 for file,extra in (
  ('Knowledge.py',"\nfrom HelpTextOutputFacts import FUNCTIONS as HELP_TEXT_OUTPUT_FUNCTIONS\nFUNCTIONS['Help'].update(HELP_TEXT_OUTPUT_FUNCTIONS)\n"),
  ('Contracts.py','\nfrom HelpTextOutputFacts import CONTRACTS as HELP_TEXT_OUTPUT_CONTRACTS\nCONTRACTS.update(HELP_TEXT_OUTPUT_CONTRACTS)\n'),
  ('SemanticNames.py','\nfrom HelpTextOutputFacts import DOCUMENTS as HELP_TEXT_OUTPUT_DOCUMENTS, name_operands as help_text_output_name_operands\nDOCUMENTS.update(HELP_TEXT_OUTPUT_DOCUMENTS)\n')):
  p=ROOT/'Tools/Disasm/Research'/file;t=p.read_text('utf-8');assert 'from HelpTextOutputFacts import' not in t
  if file=='SemanticNames.py':
   needle='    operation = help_line_index_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = help_text_output_name_operands(region, function_address, operation)')
  if file=='Knowledge.py':t=t.replace('0xDB5B: ("FormatNumber", "Печать числа через общий форматировщик и расчёт длины в знакоместах")','0xDB5B: '+repr(facts.FUNCTIONS[0xDB5B]))
  pending[p]=(t+extra).encode('utf-8')
 p=ROOT/'Docs/Functions.md';t=pending.get(p,p.read_bytes()).decode('utf-8');t=t.replace('Печать числа через общий форматировщик и расчёт длины в знакоместах',facts.FUNCTIONS[0xDB5B][1]);pending[p]=t.encode('utf-8')
 p=ROOT/'Docs/FunctionDetails/Help.md';t=pending.get(p,p.read_bytes()).decode('utf-8');t+='\n[PrintIndexedLine](../../Source/Help/PrintIndexedLine.asm) и [PrintCrRecordAndRows](../../Source/Help/PrintCrRecordAndRows.asm) имеют [проверенные договоры](../HelpTextOutput.md). Прежнее имя FormatNumber исправлено, процедура выбирает CR-заголовок и возвращает число строк в A\', числового форматирования здесь нет.\n';pending[p]=t.encode('utf-8')
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);oldbytes=p.read_bytes() if p.exists() else None;plan.append((rel,oldbytes,data));target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,oldbytes,data in plan:assert (ROOT/rel).read_bytes()==oldbytes if oldbytes is not None else not (ROOT/rel).exists()
 for rel,oldbytes,data in plan:
  if oldbytes is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(oldbytes)
 for p,data in removed.items():target=history/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,oldbytes,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 for p,data in removed.items():assert p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
 report=dict(passed=True,previously_named_contracts_described=2,misleading_name_corrected=True,physical_resource_bytes=3749,instructions_changed=0,original_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpTextOutputClassification.json').write_bytes(encode(report));print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

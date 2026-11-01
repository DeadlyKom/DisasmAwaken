"""Одноразовая типизация исходного кэша HELP и документирование индексатора."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
import HelpLineIndexFacts as facts
from PreviewSceneTables import render,parse
from SourcePresentation import format_function
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('HelpLineIndexVerification')['passed'];candidate=ROOT/'Tools/Disasm/Research/Candidates/HelpLineIndexScoped';history=ROOT/'Tools/Disasm/Research/History/BeforeHelpLineIndex'
 assert not candidate.exists() and not history.exists();pending={}
 source_map=read('SourceMap');old=next(e for e in source_map if e['slot']==8 and e['offset']==0x7C)
 oldpath=ROOT/old['path'];raw=oldpath.read_bytes();assert len(raw)==6020
 original=bytes(0x7C)+raw;text,labels=render(original,facts.TABLE,0xDB00)
 text=text.replace('подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','физический кэш указателей HELP](../../../Docs/HelpLineIndex.md)')
 assert parse(text,facts.TABLE,0xDB00)[0]==raw[:2048];pending[ROOT/facts.TABLE[1]]=text.encode('utf-8')
 remain='Source/Resources/08_HELP/UnclassifiedAfterLineCache.bin';pending[ROOT/remain]=raw[2048:]
 index=source_map.index(old);source_map[index:index+1]=[
  dict(slot=8,offset=0x7C,length=2048,kind='typed_data',path=facts.TABLE[1],origin=0xDB7C,sha256=hashlib.sha256(raw[:2048]).hexdigest()),
  dict(slot=8,offset=0x87C,length=len(raw)-2048,kind='unclassified',path=remain,origin=None,sha256=hashlib.sha256(raw[2048:]).hexdigest())]
 pending[ROOT/'Tools/Disasm/Reports/SourceMap.json']=encode(source_map)
 p=ROOT/'Source/Files/08_HELP.inc';t=p.read_text('utf-8');needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/08_HELP/Unclassified000.bin"'
 assert t.count(needle)==1;pending[p]=t.replace(needle,'                disp #DB7C\n                include "../Help/Data/LinePointers.asm"\n                ent\n                assert $ == #087C\n                ; Unknown, область E37C..F2FF требует отдельного разбора потребителей\n                incbin "../Resources/08_HELP/UnclassifiedAfterLineCache.bin"').encode('utf-8')
 for file,block in (
  ('Includes/Structs/Include.inc','                ; Документация [кэш строк HELP](../../Docs/HelpLineIndex.md)\n                struct FHelpLinePointer\n'+('TextAddress     dw #0000').ljust(80)+'; начало строки в банке 7, ноль обозначает свободную запись\n                ends\n                assert FHelpLinePointer == #02\n\n'),
  ('Includes/Const/Include.inc','                module HelpLineConst\n'+('Capacity        equ #0400').ljust(80)+'; физические 1024 слова, безопасный завершающий LDIR требует N<1024\n                endmodule\n\n')):
  p=ROOT/file;t=p.read_text('utf-8');assert t.count('                endif\n')==1;pending[p]=t.replace('                endif\n',block+'                endif\n').encode('utf-8')
 symbols=read('Symbols');symbols.update(labels);assert symbols.pop('Help.IndexTextLines.PointDB13')==0xDB13;symbols['Help.IndexTextLines.StoreLine']=0xDB13
 pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=encode(symbols)
 p=ROOT/'Source/Help/IndexTextLines.asm';lines=['                module Help','                module IndexTextLines','                ; Документация [индексирование и предел исходного LDIR](../../Docs/HelpLineIndex.md)','                ; -----------------------------------------','                ; '+facts.FUNCTIONS[0xDB00][1],'                ; запись 8, банк 7, файловые смещения #0000..#0041']
 for title,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Help',0xDB00]):lines+=['                ; '+title+':']+['                ;   '+v for v in values]
 lines+=['                ; -----------------------------------------']
 notes={0xDB00:'поиск выбранной записи, SkipLfRecords пропускает номер плюс один байт LF',0xDB08:'создание списка начал строк, X сбрасывается один раз, Y перед каждой строкой',
  0xDB13:'запись рабочего адреса текущей строки в физическую двухбайтовую запись',0xDB23:'поиск конца визуальной строки без рисования, Carry завершает запись',
  0xDB2B:'обнуление остатка таблицы, исходный код требует от 1 до 1023 занятых слов',0xDB2E:'расчёт числа свободных слов и перевод его в байтовый счётчик',
  0xDB3A:'создание первого нулевого байта для перекрывающегося копирования всего остатка',0xDB3D:'расчёт числа копируемых байтов, при N=1024 получается FFFF'}
 group=next(g for g in read('ControlFlow') if g['name']=='Help')
 for item in group['instructions']:
  a=item['address']
  if item['slot']!=8 or not 0xDB00<=a<0xDB42:continue
  if a in notes:lines.append('                ; '+notes[a])
  op=item['operation'].replace(',',', ')
  if a==0xDB28:op='JP NC, @Help.IndexTextLines.PointDB13'
  op=facts.name_operands('Help',0xDB00,op);label='Entry' if a==0xDB00 else 'StoreLine' if a==0xDB13 else ''
  line=((label+':').ljust(16) if label else ' '*16)+op
  if a==0xDB28:line=line.ljust(80)+'; переход, если строка закончилась переносом, требуется следующая'
  lines.append(line)
 lines+=['                endmodule','                endmodule'];pending[p]=format_function('\n'.join(lines)+'\n').encode('utf-8')
 functions=read('Functions');f=next(f for f in functions if f['region']=='Help' and f['address']==0xDB00);f['description']=facts.FUNCTIONS[0xDB00][1];pending[ROOT/'Tools/Disasm/Reports/Functions.json']=encode(functions)
 inventory=read('Inventory');inventory['physical_bytes_by_kind']=dict(collections.Counter({kind:sum(e['length'] for e in source_map if e['kind']==kind) for kind in inventory['physical_bytes_by_kind']}));inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encode(inventory)
 for file,extra in (
  ('Knowledge.py',"\nfrom HelpLineIndexFacts import FUNCTIONS as HELP_LINE_INDEX_FUNCTIONS\nFUNCTIONS['Help'].update(HELP_LINE_INDEX_FUNCTIONS)\n"),
  ('Contracts.py','\nfrom HelpLineIndexFacts import CONTRACTS as HELP_LINE_INDEX_CONTRACTS\nCONTRACTS.update(HELP_LINE_INDEX_CONTRACTS)\n'),
  ('SemanticNames.py','\nfrom HelpLineIndexFacts import DOCUMENTS as HELP_LINE_INDEX_DOCUMENTS, name_operands as help_line_index_name_operands\nDOCUMENTS.update(HELP_LINE_INDEX_DOCUMENTS)\n')):
  p=ROOT/'Tools/Disasm/Research'/file;t=p.read_text('utf-8');assert 'from HelpLineIndexFacts import' not in t
  if file=='SemanticNames.py':
   needle='    operation = help_text_selector_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = help_line_index_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 p=ROOT/'Tools/Disasm/VerifySources.py';t=p.read_text('utf-8');needle='    # Проверка реальных структур, меток и каждого исходного байта префиксов моделей.';assert t.count(needle)==1
 check='''    # Проверка физической таблицы HELP с отдельным адресом загрузки банка 7.
    from HelpLineIndexFacts import TABLE as HELP_LINE_TABLE
    module,path,start,end,structure,fields,names = HELP_LINE_TABLE
    entries = [item for item in source_map if item['path'] == path]
    if len(entries) != 1 or (entries[0]['slot'],entries[0]['offset'],entries[0]['length'],entries[0]['origin']) != (8,start,end-start,0xDB00+start):
        raise ValueError('Изменилось размещение таблицы HELP')
    raw,labels = parse_preview_scene((ROOT/path).read_text('utf-8'), HELP_LINE_TABLE, 0xDB00)
    if raw != sources[8][start:end] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
        raise ValueError('Изменились указатели либо поля HELP')
    if symbols.get('FHELPLINEPOINTER') != 2 or symbols.get('FHELPLINEPOINTER.TEXTADDRESS') != 0:
        raise ValueError('Изменилась структура указателя HELP')

''';pending[p]=t.replace(needle,check+needle).encode('utf-8')
 p=ROOT/'Docs/FunctionDetails/Help.md';pending[p]=(p.read_text('utf-8')+'\n[IndexTextLines](../../Source/Help/IndexTextLines.asm) имеет [проверенный договор и физический кэш](../HelpLineIndex.md), безопасный завершающий LDIR требует 1..1023 строк, предел 1024 сохранён как ограничение исходного алгоритма.\n').encode('utf-8')
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);oldbytes=p.read_bytes() if p.exists() else None;plan.append((rel,oldbytes,data));target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,oldbytes,data in plan:assert (ROOT/rel).read_bytes()==oldbytes if oldbytes is not None else not (ROOT/rel).exists()
 for rel,oldbytes,data in plan:
  if oldbytes is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(oldbytes)
 target=history/oldpath.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 for rel,oldbytes,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert oldpath.read_bytes()==raw==(history/oldpath.relative_to(ROOT)).read_bytes();oldpath.unlink()
 report=dict(passed=True,previously_named_contract_described=1,physical_cache_bytes=2048,physical_records=1024,instructions_changed=0,bytes_preserved=True,candidate_and_history_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpLineIndexClassification.json').write_bytes(encode(report));print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

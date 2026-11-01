"""Точечный выпуск четырёх контрактов, имён и связей, инструкции и индекс Git не меняются."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
import ShipPreviewCallbackFacts as facts
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 report=json.loads((ROOT/'Tools/Disasm/Reports/ShipPreviewCallbacksVerification.json').read_text('utf-8'));assert report['passed']
 candidate=ROOT/'Tools/Disasm/Research/Candidates/ShipPreviewCallbacksScoped';history=ROOT/'Tools/Disasm/Research/History/BeforeShipPreviewCallbacks'
 assert not candidate.exists() and not history.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 def renamed(text):
  for old,new in facts.RENAMES.items():text=text.replace(old,new)
  return text.replace('DrawShipPreview.Point6891','DrawShipPreview.SetCallback').replace('DrawShipPreview.Point68C6','DrawShipPreview.ReturnBank0')
 functions=read('Functions');selected=[f for f in functions if f['region']=='Station' and f['address'] in facts.FUNCTIONS];assert len(selected)==4
 flow=read('ControlFlow');g=next(v for v in flow if v['name']=='Station');validate_notes([g],{'Station':facts.COMMENTS})
 pending={};old_paths={};symbols=read('Symbols')
 # Поиск всех текущих ссылок только на четыре конкретных имени, исследовательская история не переписывается.
 for folder,pattern in (('Source','*.asm'),('Source','*.inc'),('Includes','*.inc'),('Docs','*.md')):
  for p in (ROOT/folder).rglob(pattern):
   text=p.read_text('utf-8');updated=renamed(text)
   if updated!=text:pending[p]=updated.encode('utf-8')
 for f in selected:
  begin=f['address'];name,description=facts.FUNCTIONS[begin];old_path=ROOT/f['path'];old_paths[old_path]=old_path.read_bytes();new_path='Source/Station/'+name+'.asm'
  assert not (ROOT/new_path).exists();pending.pop(old_path,None)
  rows=[i for i in g['instructions'] if i['slot']==4 and f['offset']<=i['offset']<f['end_offset']]
  lines=['                module Station','                module '+name,'                ; Документация [станционная цепочка, геометрия и настоящее IM2-пробуждение](../../Docs/ShipPreviewCallbacks.md)',
   '                ; -----------------------------------------','                ; '+description,'                ; исходная запись 4, файловые смещения #'+format(f['offset'],'04X')+'..#'+format(f['end_offset']-1,'04X')]
  for title,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Station',begin]):lines+=['                ; '+title+':']+['                ;   '+v for v in values]
  lines+=['                ; -----------------------------------------']
  for index,i in enumerate(rows):
   before,right=facts.COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in before];label='Entry' if index==0 else facts.LABELS.get(('Station',i['address']),'')
   operation=facts.name_operands('Station',begin,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+operation
   if right:assert len(line)<80;line=line.ljust(80)+'; '+right
   lines.append(line)
  lines+=['                endmodule','                endmodule'];target=dict(region='Station',name='DrawShipPreview',path='Source/Station/DrawShipPreview.asm') if begin==0x6870 else None
  pending[ROOT/new_path]=format_function('\n'.join(lines)+'\n',target).encode('utf-8')
  f.update(name=name,description=description,path=new_path,semantic_status='described')
  if begin==0x6870:f.update(fallthrough_continuation=0x6877,fragment_scope='test_exact_draw_pointer_then_preview')
 symbols={renamed(k):v for k,v in symbols.items()};assert len(symbols)==len(read('Symbols'))
 pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=encoded(symbols)
 inventory=read('Inventory');inventory['described']=sum(f.get('semantic_status')=='described' for f in functions);inventory['unknown']=len(functions)-inventory['described']
 pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 for name,value in (('Functions',functions),('SourceMap',read('SourceMap')),('ModifiedCode',read('ModifiedCode'))):
  value=json.loads(renamed(json.dumps(value,ensure_ascii=False)))
  if name=='ModifiedCode':
   assert not any(v['region']=='Station' and v['writer']==0x68D1 for v in value)
   instruction=next(i for i in g['instructions'] if i['address']==0x68EA);assert instruction['hex']=='3e00'
   value.append(dict(region='Station',writer=0x68D1,target=0x68EB,target_instruction=0x68EA,size=1,target_operation=instruction['operation'],path='Source/Station/RefreshShipPanels.asm'))
  pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encoded(value)
 # Подключение новых фактов после прежних результатов без запуска общего экспортёра.
 for filename,extra in (
  ('Knowledge.py','\nfrom ShipPreviewCallbackFacts import FUNCTIONS as SHIP_PREVIEW_CALLBACK_FUNCTIONS\nFUNCTIONS[\'Station\'].update(SHIP_PREVIEW_CALLBACK_FUNCTIONS)\n'),
  ('Contracts.py','\nfrom ShipPreviewCallbackFacts import CONTRACTS as SHIP_PREVIEW_CALLBACK_CONTRACTS\nCONTRACTS.update(SHIP_PREVIEW_CALLBACK_CONTRACTS)\n'),
  ('SemanticNames.py','\nfrom ShipPreviewCallbackFacts import LABELS as SHIP_PREVIEW_CALLBACK_LABELS, DOCUMENTS as SHIP_PREVIEW_CALLBACK_DOCUMENTS, name_operands as ship_preview_callback_name_operands\nLABELS.update(SHIP_PREVIEW_CALLBACK_LABELS)\nDOCUMENTS.update(SHIP_PREVIEW_CALLBACK_DOCUMENTS)\n'),
  ('ShipPeriodicCodeFacts.py','\nfrom ShipPreviewCallbackFacts import COMMENTS as PREVIEW_COMMENTS\nCOMMENTS.update(PREVIEW_COMMENTS)\n')):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from ShipPreviewCallbackFacts import' not in t
  if filename=='SemanticNames.py':
   needle='    operation = ship_periodic_code_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = ship_preview_callback_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');needle='                module ShipPanelState\n';assert t.count(needle)==1
 t=t.replace(needle,needle+('PreviewIndex'.ljust(16)+'equ #6878').ljust(80)+'; изменяемое слово индекса FInterfaceItem в LD HL рисователя просмотра\n');pending[p]=t.encode('utf-8')
 p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8');assert 'module ShipPreviewConst' not in t
 block='                module ShipPreviewConst\n'
 for name,value,meaning in (('PreviewPage',0x14,'банк D3D 4 с установкой ROM 1'),('ColumnInset',13,'вычитаемое из пиксельной ширины текстового окна для верхней колонки'),('RowInset',14,'вычитаемое из пиксельной высоты текстового окна для верхней строки')):
  block+=(name.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+meaning+'\n'
 block+='                endmodule\n\n';assert t.count('                endif\n')==1;pending[p]=t.replace('                endif\n',block+'                endif\n').encode('utf-8')
 # Уточнение доказанного соответствия размеров, правится только комментарий, не исходный операнд.
 for name in ('Source/D3D/ConfigurePreviewClip.asm','Tools/Disasm/Research/D3DClipFacts.py'):
  p=ROOT/name;t=p.read_text('utf-8');old='верхний X берётся из ширины текстового окна минус 14, верхний Y из высоты минус 13';assert t.count(old)==1
  t=t.replace(old,'верхняя строка H берётся из TextWindow.Height минус 14, верхняя колонка L из TextWindow.Width минус 13');pending[p]=renamed(t).encode('utf-8')
 p=ROOT/'Docs/PreviewClipBounds.md';t=pending.get(p,p.read_bytes()).decode('utf-8');old='В исходном DrawShipPreview верхние пределы получают ширину текстового окна минус 14 и высоту минус 13';assert t.count(old)==1
 pending[p]=t.replace(old,'В исходном DrawShipPreview H получает высоту текстового окна минус 14, L ширину минус 13').encode('utf-8')
 p=ROOT/'Docs/Functions.md';t=pending.get(p,p.read_bytes()).decode('utf-8');assert '| Station | 422 | 368 |' in t;pending[p]=t.replace('| Station | 422 | 368 |','| Station | 422 | 371 |').encode('utf-8')
 p=ROOT/'Docs/FunctionDetails/Station.md';t=pending.get(p,p.read_bytes()).decode('utf-8')
 for address,(name,description) in facts.FUNCTIONS.items():t+='\n['+name+'](../../Source/Station/'+name+'.asm) — '+description+', [полный алгоритм и пределы проверки](../ShipPreviewCallbacks.md).\n'
 pending[p]=t.encode('utf-8')
 p=ROOT/'Docs/ModifiedCode.md';t=pending.get(p,p.read_bytes()).decode('utf-8');t+='\n| Station | #68D1 | #68EB | LD A,#00 | [RefreshShipPanels.asm](../Source/Station/RefreshShipPanels.asm) |\n';pending[p]=t.encode('utf-8')
 # Создание отдельного кандидата и точного списка прежних байтов только затронутых файлов.
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);old=p.read_bytes() if p.exists() else None;plan.append((rel,old,data));target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,old,data in plan:assert (ROOT/rel).read_bytes()==old if old is not None else not (ROOT/rel).exists()
 for rel,old,data in plan:
  if old is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old)
 for p,data in old_paths.items():target=history/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,old,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление только четырёх заменённых исходников после проверки новых и сохранённых копий.
 for p,data in old_paths.items():
  assert p.resolve().is_relative_to((ROOT/'Source/Station').resolve()) and p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
 result=dict(passed=True,functions_renamed=4,unknown_functions_described=3,previously_named_contract_described=1,instructions_changed=0,physical_bytes_preserved=True,
  additional_registered_operand_writer=0x68D1,source_documentation_axis_correction=True,scoped_candidate_and_history=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShipPreviewCallbacksClassification.json').write_bytes(encoded(result));print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

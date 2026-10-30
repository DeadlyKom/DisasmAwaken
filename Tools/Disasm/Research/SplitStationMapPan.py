"""Выделение прокрутки карты и выбора точки из диспетчера без изменения 310 исходных байтов."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from SourcePresentation import format_function,instructions
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/StationMapPanScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeStationMapPanSplit'


def main():
 verify();assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('MapPanVerification')['passed'];functions=read('Functions');source_map=read('SourceMap');symbols=read('Symbols');flow=read('ControlFlow')
 original=next(f for f in functions if f['region']=='Station' and f['address']==0x6C0D);assert original['end_offset']==0x0FEF
 rows=[i for g in flow if g['name']=='Station' for i in g['instructions'] if i['slot']==4 and 0x0EB9<=i['offset']<0x0FEF]
 source=(ROOT/original['path']).read_text('utf-8');code_lines=[l for l in source.splitlines() if l.strip() and not l.lstrip().startswith(';') and not l[16:].strip().lower().startswith(('module ','endmodule'))]
 assert len(rows)==len(code_lines) and sum(len(bytes.fromhex(i['hex'])) for i in rows)==310
 renames={'Station.Unknown6C0D.Point6C6E':'Station.Unknown6C6E.Entry','Station.Unknown6C0D.Point6D0D':'Station.Unknown6D0D.Entry'}
 assert all(symbols[k]==v for k,v in zip(renames,(0x6C6E,0x6D0D)))
 current_module=None
 def rewrite(text):
  result=[]
  for line in text.splitlines():
   before=line
   for old_name,new_name in renames.items():line=line.replace(old_name,new_name)
   if current_module=='Unknown6C6E':line=line.replace('Station.Unknown6C0D.Point','Station.Unknown6C6E.Point')
   if line!=before and not line.lstrip().startswith(';') and ';' in line:
    left,comment=line.split(';',1);assert len(left.rstrip())<80;line=left.rstrip().ljust(80)+';'+comment
   result.append(line)
  return '\n'.join(result)+('\n' if text.endswith('\n') else '')
 pending={};new_functions=[]
 for begin,end,name in ((0x6C0D,0x6C6E,'Unknown6C0D'),(0x6C6E,0x6D0D,'Unknown6C6E'),(0x6D0D,0x6D43,'Unknown6D0D')):
  current_module=name
  path='Source/Station/'+name+'.asm';selected=[(i,line) for i,line in zip(rows,code_lines) if begin<=i['address']<end]
  assert sum(len(bytes.fromhex(i['hex'])) for i,_ in selected)==end-begin
  lines=['                module Station','                module '+name,
   '; Документация [диспетчер карты, прокрутка и выбор точки](../../Docs/MapPan.md)',
   '; -----------------------------------------','; Unknown, независимый исходный вход, договор оформляется отдельно',
   '; исходная запись 4, файловые смещения #'+format(begin-0x5D54,'04X')+'..#'+format(end-0x5D55,'04X'),
   '; In:',';   Unknown, назначение и регистровый договор оформляются отдельно',
   '; Out:',';   все исходные инструкции и адреса сохранены',
   '; Corrupt:',';   Unknown, разделение файла не доказывает договор соседнего входа','; -----------------------------------------']
  for index,(i,line) in enumerate(selected):lines.append(('Entry:'.ljust(16) if index==0 else line[:16])+rewrite(line[16:]).rstrip('\n'))
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n')
  f=dict(original, name=name,address=begin,offset=begin-0x5D54,end_offset=end-0x5D54,path=path,description='Unknown, самостоятельный исходный вход, договор оформляется отдельно');new_functions.append(f)
 current_module=None
 def restore(op):
  for old_name,new_name in renames.items():op=op.replace(new_name,old_name)
  return op.replace('Station.Unknown6C6E.Point','Station.Unknown6C0D.Point')
 assert instructions(source)==[restore(op) for f in new_functions for op in instructions(pending[ROOT/f['path']])]
 for path in (ROOT/'Source').rglob('*'):
  if path.is_file() and path.suffix in ('.asm','.inc') and path not in pending:
   text=path.read_text('utf-8');changed=rewrite(text)
   if changed!=text:pending[path]=changed
 include=ROOT/'Source/Files/04_STATIONF.inc';content=pending.get(include,include.read_text('utf-8'))
 needle='                disp #6C0D\n                include "../Station/Unknown6C0D.asm"\n                ent';assert content.count(needle)==1
 replacement=[]
 for f in new_functions:
  replacement+=['                disp #'+format(f['address'],'04X'),'                include "../Station/'+f['name']+'.asm"','                ent','                assert $ == #'+format(f['end_offset'],'04X')]
 content=content.replace(needle,'\n'.join(replacement),1);pending[include]=content
 index=functions.index(original);functions[index:index+1]=new_functions
 index=next(i for i,e in enumerate(source_map) if e['path']==original['path']);old=source_map[index]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));raw=(ROOT/(next(e for e in manifest['entries'] if e['slot']==4)['path']+'.sectors.bin')).read_bytes()
 source_map[index:index+1]=[dict(old,offset=f['offset'],length=f['end_offset']-f['offset'],path=f['path'],origin=f['address'],sha256=hashlib.sha256(raw[f['offset']:f['end_offset']]).hexdigest()) for f in new_functions]
 for old_name,new_name in renames.items():symbols[new_name]=symbols.pop(old_name)
 for key in list(symbols):
  if key.startswith('Station.Unknown6C0D.Point') and 0x6C6E<=symbols[key]<0x6D0D:symbols[key.replace('Unknown6C0D','Unknown6C6E')]=symbols.pop(key)
 inventory=read('Inventory');inventory.update(fragments=len(functions),unknown=sum(f['semantic_status']=='unknown' for f in functions));inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map))
 for name,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');local=[f for f in functions if f['region']=='Station'];text=re.sub(r'^\| Station \| \d+ \| \d+ \|','| Station | '+str(len(local))+' | '+str(sum(f['semantic_status']=='described' for f in local))+' |',text,flags=re.M)
 pending[p]=text+''.join('\n| #'+format(f['address'],'04X')+' | [Station.'+f['name']+'](../'+f['path']+') | Unknown, самостоятельный исходный вход |\n' for f in new_functions[1:])
 p=ROOT/'Docs/FunctionDetails/Station.md';pending[p]=p.read_text('utf-8')+''.join('\n## '+f['name']+'\n\n[Station.'+f['name']+'](../../'+f['path']+') — самостоятельный вход, назначение и договор оформляются отдельно.\n' for f in new_functions[1:])
 pending[ROOT/'Docs/MapPan.md']="""# Перемещение мирового начала карты

[Диспетчер 6C0D](../Source/Station/Unknown6C0D.asm), [прокрутка 6C6E](../Source/Station/Unknown6C6E.asm) и [выбор точки 6D0D](../Source/Station/Unknown6D0D.asm) разделены по фактическим входам и завершающим RET. Сохранены все 310 байтов диапазона 6C0D..6D42. Байту 6D43 за пределами прежнего файла новое назначение не приписывается.

[Модель](../Tools/Disasm/Research/CheckMapPan.py) отдельно проверяет ветвь прокрутки, её арифметику и композицию экрана. Полный диспетчер 6C0D и информационная панель выбора точки этой моделью не объявлены разобранными. Сборка и нативный запуск не выполнялись.
"""
 plan=[]
 for path,text in pending.items():
  data=text.encode('utf-8');rel=path.relative_to(ROOT);target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  plan.append((rel,path.read_bytes() if path.exists() else None,data))
 # Проверка каждого кандидата и сохранности рабочей версии до применения всего точечного набора.
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists();assert (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:
   target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 for rel,before,data in plan:
  target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 verify()
 report=dict(passed=True,original_bytes=310,procedure_lengths=[97,159,54],original_instructions_preserved=True,original_targets_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StationMapPanSplitVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report))


if __name__=='__main__':main()

"""Выделение самостоятельного A7F5 из общего файла с независимым A806, без изменения инструкций."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from SourcePresentation import format_function,instructions
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/StationVariantCountScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeStationVariantCountSplit'


def main():
 verify();assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('VariantCountVerification')['passed'];functions=read('Functions');source_map=read('SourceMap');symbols=read('Symbols');flow=read('ControlFlow')
 original=next(f for f in functions if f['region']=='Station' and f['address']==0xA7F5);assert original['end_offset']==0x482D
 rows=[i for g in flow if g['name']=='Station' for i in g['instructions'] if i['slot']==4 and 0x47F5<=i['offset']<0x482D]
 source=(ROOT/original['path']).read_text('utf-8');code_lines=[l for l in source.splitlines() if l.strip() and not l.lstrip().startswith(';') and not l[16:].strip().lower().startswith(('module ','endmodule'))]
 assert len(rows)==len(code_lines) and sum(len(bytes.fromhex(i['hex'])) for i in rows)==56
 old_name='Station.UnknownA7F5.PointA806';new_name='Station.UnknownA806.Entry';assert symbols[old_name]==0xA806
 def rewrite(text):
  result=[]
  for line in text.splitlines():
   before=line;line=line.replace(old_name,new_name)
   if line!=before and not line.lstrip().startswith(';') and ';' in line:
    left,comment=line.split(';',1);assert len(left.rstrip())<80;line=left.rstrip().ljust(80)+';'+comment
   result.append(line)
  return '\n'.join(result)+('\n' if text.endswith('\n') else '')
 pending={};new_functions=[]
 for begin,end,name in ((0xA7F5,0xA806,'UnknownA7F5'),(0xA806,0xA82D,'UnknownA806')):
  path='Source/Station/'+name+'.asm';selected=[(i,line) for i,line in zip(rows,code_lines) if begin<=i['address']<end]
  assert sum(len(bytes.fromhex(i['hex'])) for i,_ in selected)==end-begin
  lines=['                module Station','                module '+name,
   '; Документация [самостоятельный вычислитель количества и соседний вход](../../Docs/VariantCount.md)',
   '; -----------------------------------------','; Unknown, независимый исходный вход, договор оформляется отдельно',
   '; исходная запись 4, файловые смещения #'+format(begin-0x6000,'04X')+'..#'+format(end-0x6001,'04X'),
   '; In:',';   Unknown, назначение и регистровый договор оформляются отдельно',
   '; Out:',';   все исходные инструкции и адреса сохранены',
   '; Corrupt:',';   Unknown, разделение файла не доказывает договор соседнего входа','; -----------------------------------------']
  for index,(i,line) in enumerate(selected):lines.append(('Entry:'.ljust(16) if index==0 else line[:16])+rewrite(line[16:]).rstrip('\n'))
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n')
  f=dict(original, name=name,address=begin,offset=begin-0x6000,end_offset=end-0x6000,path=path,description='Unknown, самостоятельный исходный вход, договор оформляется отдельно');new_functions.append(f)
 assert instructions(source)==[op.replace(new_name,old_name) for f in new_functions for op in instructions(pending[ROOT/f['path']])]
 for path in (ROOT/'Source').rglob('*'):
  if path.is_file() and path.suffix in ('.asm','.inc') and path not in pending:
   text=path.read_text('utf-8');changed=rewrite(text)
   if changed!=text:pending[path]=changed
 include=ROOT/'Source/Files/04_STATIONF.inc';content=pending.get(include,include.read_text('utf-8'))
 needle='                disp #A7F5\n                include "../Station/UnknownA7F5.asm"\n                ent';assert content.count(needle)==1
 content=content.replace(needle,'                disp #A7F5\n                include "../Station/UnknownA7F5.asm"\n                ent\n                assert $ == #4806\n                disp #A806\n                include "../Station/UnknownA806.asm"\n                ent',1);pending[include]=content
 index=functions.index(original);functions[index:index+1]=new_functions
 index=next(i for i,e in enumerate(source_map) if e['path']==original['path']);old=source_map[index]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));raw=(ROOT/(next(e for e in manifest['entries'] if e['slot']==4)['path']+'.sectors.bin')).read_bytes()
 source_map[index:index+1]=[dict(old,offset=f['offset'],length=f['end_offset']-f['offset'],path=f['path'],origin=f['address'],sha256=hashlib.sha256(raw[f['offset']:f['end_offset']]).hexdigest()) for f in new_functions]
 symbols.pop(old_name);symbols[new_name]=0xA806
 inventory=read('Inventory');inventory.update(fragments=len(functions),unknown=sum(f['semantic_status']=='unknown' for f in functions));inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map))
 for name,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');local=[f for f in functions if f['region']=='Station'];text=re.sub(r'^\| Station \| \d+ \| \d+ \|','| Station | '+str(len(local))+' | '+str(sum(f['semantic_status']=='described' for f in local))+' |',text,flags=re.M)
 pending[p]=text+'\n| #A806 | [Station.UnknownA806](../Source/Station/UnknownA806.asm) | Unknown, независимый соседний вход |\n'
 p=ROOT/'Docs/FunctionDetails/Station.md';pending[p]=p.read_text('utf-8')+'\n## UnknownA806\n\n[Station.UnknownA806](../../Source/Station/UnknownA806.asm) — независимый соседний вход, договор ещё разбирается.\n'
 pending[ROOT/'Docs/VariantCount.md']='''# Количество вариантов выбранного ключа

[Вычислитель A7F5](../Source/Station/UnknownA7F5.asm) и [независимый соседний вход A806](../Source/Station/UnknownA806.asm) раньше находились в одном физическом файле. Каждый заканчивается собственным RET, вызовы второго входа не являются продолжением вычислителя. Разделение сохраняет все 56 байтов и прежние цели четырёх внешних переходов.

Вычислитель читает MapSelection.FirstWord и SecondWord. Четыре байта объединяются через XOR, результат ограничивается младшими тремя разрядами. Возвращается max((XOR AND 7)-1,0), диапазон 0..6. Нулевыми являются два исходных кода, 0 и 1. Флаг Z установлен на обоих, но полный AF различается — 0044 и 0042 соответственно. DE получает второе слово, HL первое, BC и альтернативные и индексные регистры сохраняются.

[CheckVariantCount](../Tools/Disasm/Research/CheckVariantCount.py) проверил 131072 пары слов, точный AF, обе нулевые ветви, выходные регистры и стек. Назначение независимого A806 этой проверкой не объявлено установленным. Банковые потребители количества разобраны в [AnimatedVariants](AnimatedVariants.md), вызывающий периодический путь станции ещё оформляется. Сборка и нативный запуск не выполнялись.
'''
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
 report=dict(passed=True,original_bytes=56,first_procedure_bytes=17,independent_tail_bytes=39,original_instructions_preserved=True,external_targets_preserved=4,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StationVariantCountSplitVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report))


if __name__=='__main__':main()

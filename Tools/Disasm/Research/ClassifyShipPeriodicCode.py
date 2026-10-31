"""Точечное выделение 85 исходных байтов корабельных callback, без сборки и массового экспорта."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze,payload
from VerifySources import main as verify
from SourcePresentation import format_function
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/ShipPeriodicCodeScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeShipPeriodicCode'
PARTS=((0x6870,0x6877,'Unknown6870'),(0x68CC,0x68EA,'Unknown68CC'),(0x68EA,0x6913,'Unknown68EA'),(0x693E,0x6945,'Unknown693E'))


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 flow=read('ControlFlow');old=next(g for g in flow if g['name']=='Station');new=analyze('Station',extra_roots=(0x68CC,0x68EA),observed=[i['address'] for i in old['instructions']]);previous={i['address']:i for i in old['instructions']};added=[i for i in new['instructions'] if i['address'] not in previous]
 assert not new['overlaps'] and len(added)==36 and sum(len(bytes.fromhex(i['hex'])) for i in added)==85
 assert all(i in new['instructions'] for i in old['instructions'])
 raw=payload(4);functions=read('Functions');source_map=read('SourceMap');symbols=read('Symbols');pending={};originals=[]
 for begin,end,name in PARTS:
  symbol='Station.'+name+'.Entry';assert symbol not in symbols;symbols[symbol]=begin
 targets={v:k for k,v in symbols.items() if k.startswith('Station.')}
 aliases={0x9E78:'ActiveItemState.Active',0x68EB:'ShipPanelState.PendingRedraw',0x6906:'ShipPanelState.Selector'}
 for begin,end,name in PARTS:
  rows=[i for i in added if begin<=i['address']<end];assert sum(len(bytes.fromhex(i['hex'])) for i in rows)==end-begin
  path='Source/Station/'+name+'.asm';offset=rows[0]['offset'];description='Unknown, исходный корабельный callback, полный договор зависимых рисователей и банка 4 ещё не установлен'
  lines=['                module Station','                module '+name,'                ; Документация [корабельные периодические входы](../../Docs/ShipPeriodicCode.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 4, файловые смещения #'+format(offset,'04X')+'..#'+format(offset+end-begin-1,'04X'),'                ; In:','                ;   Unknown, полный договор зависимых рисователей ещё не установлен','                ; Out:','                ;   исходные инструкции и физические адреса сохранены, известные ветви описаны в документации','                ; Corrupt:',"                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная граница до разбора вызовов",'                ; Note:','                ;   выделение достижимого кода не доказывает полный смысловой разбор','                ; -----------------------------------------']
  for j,i in enumerate(rows):
   op=i['operation'];right=None
   for value,symbol in aliases.items():op=op.replace('(#'+format(value,'04X')+')','(@'+symbol+')')
   match=re.fullmatch(r'(CALL|JP|JR) (?:(NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]+)',op)
   if match:
    kind,cond,hexval=match.groups();value=int(hexval,16)
    if value in targets:op=kind+' '+((cond+', ') if cond else '')+'@'+targets[value]
   if i['address']==0x6876 or i['address']==0x6944:right='выход, если точного рисователя нет в текущем списке'
   elif i['address']==0x68D0:right='выход, если ActiveItemState.Active ненулевой, отложить обновление'
   elif i['address']==0x68ED:right='переход, если PendingRedraw ненулевой, обработать отложенное обновление'
   elif i['address']==0x68F8:right='выход, если последний рисователь не равен DrawItem26.Entry'
   if i['address'] in (0x68CF,0x68EC):lines.append('                ; проверка байтового состояния перед выбором ветви')
   if i['address']==0x68F6:lines.append('                ; сравнение последнего рисователя с исходным адресом DrawItem26')
   op=re.sub(r',(?=\S)',', ',op);line=('Entry:'.ljust(16) if j==0 else ' '*16)+op
   lines.append(line.ljust(80)+'; '+right if right else line)
  if begin in (0x6870,0x693E):
   next_name='DrawItem26' if begin==0x6870 else 'DrawItem27';lines+=['','                ; JP @Station.'+next_name+'.Entry, продолжение в '+next_name+'.asm']
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n')
  functions.append(dict(region='Station',name=name,address=begin,slot=4,offset=offset,description=description,semantic_status='unknown',end_offset=offset+end-begin,path=path))
 # Замена только трёх целиком подтверждённых бинарных областей, неизвестные хвосты не удаляются.
 for filename,starts in (('Unclassified009.bin',(0x6870,)),('Unclassified010.bin',(0x68CC,0x68EA)),('Unclassified012.bin',(0x693E,))):
  old_entry=next(e for e in source_map if e['slot']==4 and e['path'].endswith('/'+filename));old_path=ROOT/old_entry['path'];originals.append(old_path);assert old_path.read_bytes()==raw[old_entry['offset']:old_entry['offset']+old_entry['length']]
  replacements=[]
  for begin in starts:
   _,end,name=next(p for p in PARTS if p[0]==begin);f=next(f for f in functions if f['region']=='Station' and f['address']==begin);replacements.append(dict(old_entry,offset=f['offset'],length=end-begin,kind='code',path=f['path'],origin=begin,sha256=hashlib.sha256(raw[f['offset']:f['end_offset']]).hexdigest()))
  assert sum(e['length'] for e in replacements)==old_entry['length'];index=source_map.index(old_entry);source_map[index:index+1]=replacements
  include=ROOT/'Source/Files/04_STATIONF.inc';text=pending.get(include,include.read_text('utf-8'));needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/04_STATIONF/'+filename+'"';assert text.count(needle)==1;block=[]
  for e in replacements:
   prefix=''
   include_line='                include \"../Station/'+Path(e['path']).name+'\"'
   if e['origin'] in (0x6870,0x693E):include_line=include_line.ljust(80)+'; (0) жёсткий порядок, последовательное исполнение'
   block.append(prefix+'                disp #'+format(e['origin'],'04X')+'\n'+include_line+'\n                ent\n                assert $ == #'+format(e['offset']+e['length'],'04X'))
  text=text.replace(needle,'\n'.join(block),1)
  if len(starts)==1:
   target='DrawItem26.asm' if starts[0]==0x6870 else 'DrawItem27.asm';needle='                include "../Station/'+target+'"';assert text.count(needle)==1;text=text.replace(needle,needle.ljust(80)+'; (1) жёсткий порядок, последовательное исполнение',1)
  pending[include]=text
 flow[flow.index(old)]=new;functions.sort(key=lambda f:(f['slot'],f['offset'],f['region']));inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(g['instruction_count'] for g in flow));inventory['physical_bytes_by_kind']={kind:sum(e['length'] for e in source_map if e['kind']==kind) for kind in sorted({e['kind'] for e in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map))
 for filename,value in (('ControlFlow',flow),('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+filename+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 # Сначала сохраняется отдельный кандидат и проверяется отсутствие изменений относительно прочитанной рабочей копии.
 plan=[]
 for p,text in pending.items():
  rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;data=text.encode('utf-8');target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists();assert (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 for p in originals:target=HISTORY/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление бинарных дубликатов разрешено только после совпадения сохранённых копий и проверки новой разметки.
 for p in originals:assert p.resolve().is_relative_to(ROOT/'Source/Resources/04_STATIONF') and p.read_bytes()==(HISTORY/p.relative_to(ROOT)).read_bytes();p.unlink()
 report=dict(passed=True,added_instructions=36,added_code_bytes=85,new_unknown_fragments=4,old_instruction_records_preserved=True,conditional_fallthrough_order_explicit=True,scoped_candidate_and_history=True,full_semantic_analysis_complete=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShipPeriodicCodeClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

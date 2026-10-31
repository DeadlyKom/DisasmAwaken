"""Точечное выделение вставки D3D и физических узлов с кандидатом и проверкой байтов."""
from pathlib import Path
import collections,contextlib,copy,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from InspectZ80 import decoder
from PreviewQueueFacts import FUNCTIONS,CONTRACTS,COMMENTS,LABELS,name_operands,STATE
from PreviewQueueTable import PATH,START,END,FIELDS,render
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PreviewQueueScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePreviewQueue'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewQueueVerification')['passed']
 raw=payload(6);memory=bytearray(65536);memory[0xC000:0xC000+len(raw)]=raw
 added=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=6,offset=i.address-0xC000) for i in decoder(memory).disassemble(0xEE24,0xEEEE,'h')]
 assert b''.join(bytes.fromhex(i['hex']) for i in added)==raw[0x2E24:0x2EEE]
 flow=read('ControlFlow');previous=next(v for v in flow if v['name']=='D3D');g=copy.deepcopy(previous)
 old_bytes={i['address']+j for i in previous['instructions'] for j in range(len(bytes.fromhex(i['hex'])))}
 assert all(i['address']+j not in old_bytes for i in added for j in range(len(bytes.fromhex(i['hex']))))
 g['instructions']=sorted(g['instructions']+added,key=lambda i:i['address']);g['roots']=sorted(set(g['roots'])|{0xEE24})
 branches=set(g['branches']);known={i['address'] for i in g['instructions']}
 # Регистрация только доказанного физического диапазона, внешние продолжения не считаются уже разобранными.
 for i in added:
  match=re.fullmatch(r'(?:JP|JR) (?:[A-Z]+,)?#([0-9A-F]+)',i['operation'])
  if match:
   target=int(match[1],16);branches.add(target)
   if target not in known:g['unresolved'].append(dict(address=i['address'],operation=i['operation'],target=target,bank=4,reason='продолжение вне выделенного диапазона очереди'))
 g['branches']=sorted(branches);g['instruction_count']=len(g['instructions']);g['code_bytes']=sum(len(bytes.fromhex(i['hex'])) for i in g['instructions']);g['classified_fraction']=g['code_bytes']/g['total_bytes']
 validate_notes([g],{'D3D':COMMENTS})
 name,description=FUNCTIONS[0xEE24];path='Source/D3D/'+name+'.asm'
 lines=['                module D3D','                module '+name,'                ; Документация [двухключевая очередь объектов](../../Docs/PreviewQueue.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #2E24..#2EED']
 for title,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',0xEE24]):lines+=['                ; '+title+':']+['                ;   '+value for value in values]
 lines+=['                ; -----------------------------------------'];pending={};binaries={};symbols=read('Symbols');functions=read('Functions')
 for j,i in enumerate(added):
  above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];label='Entry' if j==0 else LABELS.get(('D3D',i['address']),'')
  if label:
   symbol='D3D.'+name+'.'+label;assert symbol not in symbols;symbols[symbol]=i['address']
  op=name_operands('D3D',0xEE24,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
  if right:assert len(line)<80;line=line.ljust(80)+'; '+right
  lines.append(line)
 lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n')
 functions.append(dict(region='D3D',name=name,address=0xEE24,slot=6,offset=0x2E24,end_offset=0x2EEE,path=path,description=description,semantic_status='described'))
 text,labels=render(raw);assert not symbols.keys()&labels.keys();symbols.update(labels);pending[ROOT/PATH]=text
 source_map=read('SourceMap');include=ROOT/'Source/Files/06_D3D.inc';include_text=include.read_text('utf-8');originals=[]
 replacements=(
 ('Source/Resources/06_D3D/AfterCoordinateTransform.bin',((0x2C28,0x2E24,'unclassified','Source/Resources/06_D3D/BeforeQueueInsert.bin',None),(0x2E24,0x2EEE,'code',path,0xEE24),(0x2EEE,0x3581,'unclassified','Source/Resources/06_D3D/AfterQueueInsert.bin',None))),
 ('Source/Resources/06_D3D/BeforePriceText.bin',((0,START,'unclassified','Source/Resources/06_D3D/BeforeQueueStorage.bin',None),(START,END,'typed_data',PATH,0xC700),(END,0xE40,'unclassified','Source/Resources/06_D3D/AfterQueueStorage.bin',None))))
 # Проверка полного смежного покрытия обеих заменяемых бинарных областей.
 for original_path,ranges in replacements:
  old_range=next(e for e in source_map if e['path']==original_path);original=ROOT/original_path;assert original.read_bytes()==raw[old_range['offset']:old_range['offset']+old_range['length']];originals.append(original);position=old_range['offset'];mapped=[];include_lines=[]
  for start,end,kind,target,origin in ranges:
   assert start==position and start<end;position=end;blob=raw[start:end];mapped.append(dict(old_range,offset=start,length=end-start,kind=kind,path=target,origin=origin,sha256=hashlib.sha256(blob).hexdigest()))
   if kind=='unclassified':binaries[ROOT/target]=blob;include_lines.append('                incbin "../Resources/06_D3D/'+Path(target).name+'"')
   else:include_lines+=['                disp #'+format(origin,'04X'),'                include "../D3D/'+('Data/' if kind=='typed_data' else '')+Path(target).name+'"','                ent']
   include_lines.append('                assert $ == #'+format(end,'04X'))
  assert position==old_range['offset']+old_range['length'];idx=source_map.index(old_range);source_map[idx:idx+1]=mapped
  needle='                incbin "../Resources/06_D3D/'+original.name+'"';assert include_text.count(needle)==1;include_text=include_text.replace(needle,'\n'.join(include_lines))
 pending[include]=include_text;flow[flow.index(previous)]=g;inventory=read('Inventory')
 inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow))
 inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for report,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+report+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');assert '| D3D | 8 | 8 |' in t;pending[p]=t.replace('| D3D | 8 | 8 |','| D3D | 9 | 9 |')+'\n| #EE24, банк 4 | [D3D.'+name+'](../'+path+') | '+description+' |\n'
 p=ROOT/'Docs/FunctionDetails/D3D.md';pending[p]=p.read_text('utf-8')+'\n['+name+'](../../'+path+') — см. [PreviewQueue](../PreviewQueue.md).\n'
 p=ROOT/'Includes/Structs/Include.inc';t=p.read_text('utf-8');assert 'struct FPreviewQueueNode' not in t;block='                ; физический узел очереди D3D, поля записываются от конца через рабочий SP\n                struct FPreviewQueueNode\n'
 for field,width,meaning in FIELDS:block+=(field.ljust(16)+('db #00' if width==1 else 'dw #0000')).ljust(80)+'; '+meaning+'\n'
 block+='                ends\n                assert FPreviewQueueNode == #0E\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module PreviewQueueState' not in t;block='                module PreviewQueueState\n'
 meanings={'Head':'младший индекс головы активной очереди, 1 обозначает пустую','NextFree':'свободный индекс с шагом 14, FC завершает обход объектов','Flags':'флаги подготавливаемого узла, бит 7 участвует в выборе ключа','ModelOffset':'рабочее смещение указателя модели подготавливаемого узла','AngleFirst':'первый параметр ориентации подготавливаемого узла','AngleSecond':'второй параметр ориентации подготавливаемого узла','AngleThird':'третий параметр ориентации подготавливаемого узла'}
 for address,label in STATE.items():block+=(label.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+meanings[label]+'\n'
 block+='                endmodule\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8');assert 'module PreviewQueueConst' not in t;block='                module PreviewQueueConst\n'
 for label,value,meaning in (('Page',0xC7,'старший байт адреса физических узлов очереди'),('EndMarker',1,'младший индекс конца активной цепочки, нулевой индекс допустим'),('FullIndex',252,'свободный индекс после 18 узлов, прекращение обхода объектов')):block+=(label.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+meaning+'\n'
 block+='                endmodule\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n')
 plan=[]
 # Создание отдельного кандидата и сверка текущих пользовательских файлов до замены.
 for p,value in {**pending,**binaries}.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 for original in originals:target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление только заменённых бинарных копий после точного сравнения с сохранённой историей.
 for original in originals:
  assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,instructions=len(added),code_bytes=202,bank=4,physical_nodes=18,node_size=14,typed_bytes=252,source_labels=len(labels),scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewQueueClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

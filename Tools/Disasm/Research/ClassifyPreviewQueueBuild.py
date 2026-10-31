"""Точечное выделение построения очереди и физических исходных структур с кандидатом и проверкой байтов."""
from pathlib import Path
import collections,contextlib,copy,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from InspectZ80 import decoder
from PreviewQueueBuildFacts import FUNCTIONS,CONTRACTS,COMMENTS,LABELS,name_operands
from PreviewSceneTables import TABLES,render
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PreviewQueueBuildScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePreviewQueueBuild'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewQueueBuildVerification')['passed']
 raw=payload(6);memory=bytearray(65536);memory[0xC000:0xC000+len(raw)]=raw
 added=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=6,offset=i.address-0xC000) for i in decoder(memory).disassemble(0xEC28,0xEDB0,'h')]
 assert b''.join(bytes.fromhex(i['hex']) for i in added)==raw[0x2C28:0x2DB0]
 flow=read('ControlFlow');previous=next(v for v in flow if v['name']=='D3D');g=copy.deepcopy(previous)
 old_bytes={i['address']+j for i in previous['instructions'] for j in range(len(bytes.fromhex(i['hex'])))}
 assert all(i['address']+j not in old_bytes for i in added for j in range(len(bytes.fromhex(i['hex']))))
 g['instructions']=sorted(g['instructions']+added,key=lambda i:i['address']);g['roots']=sorted(set(g['roots'])|{0xEC28})
 branches=set(g['branches']);known={i['address'] for i in g['instructions']}
 # Регистрация только доказанного физического диапазона, внешние продолжения не считаются уже разобранными.
 for i in added:
  match=re.fullmatch(r'(?:JP|JR) (?:[A-Z]+,)?#([0-9A-F]+)',i['operation'])
  if match:
   target=int(match[1],16);branches.add(target)
   if target not in known:g['unresolved'].append(dict(address=i['address'],operation=i['operation'],target=target,bank=4,reason='продолжение вне выделенного диапазона очереди'))
 g['unresolved']=[entry for entry in g['unresolved'] if entry.get('target') not in known]
 g['branches']=sorted(branches);g['instruction_count']=len(g['instructions']);g['code_bytes']=sum(len(bytes.fromhex(i['hex'])) for i in g['instructions']);g['classified_fraction']=g['code_bytes']/g['total_bytes']
 validate_notes([g],{'D3D':COMMENTS})
 name,description=FUNCTIONS[0xEC28];path='Source/D3D/'+name+'.asm'
 lines=['                module D3D','                module '+name,'                ; Документация [построение очереди объектов](../../Docs/PreviewQueueBuild.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #2C28..#2DAF']
 for title,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',0xEC28]):lines+=['                ; '+title+':']+['                ;   '+value for value in values]
 lines+=['                ; -----------------------------------------'];pending={};binaries={};symbols=read('Symbols');functions=read('Functions')
 for j,i in enumerate(added):
  above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];label='Entry' if j==0 else LABELS.get(('D3D',i['address']),'')
  if label:
   symbol='D3D.'+name+'.'+label;assert symbol not in symbols;symbols[symbol]=i['address']
  op=name_operands('D3D',0xEC28,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
  if right:assert len(line)<80;line=line.ljust(80)+'; '+right
  lines.append(line)
 lines+=['                endmodule','                endmodule'];child=next(f for f in functions if f['region']=='D3D' and f['address']==0xEDB0);pending[ROOT/path]=format_function('\n'.join(lines)+'\n',target=child)
 functions.append(dict(region='D3D',name=name,address=0xEC28,slot=6,offset=0x2C28,end_offset=0x2DB0,path=path,description=description,semantic_status='described',fragment_scope='queue_build_before_render',whole_ec28_rendering_contract_proved=False))
 all_labels={}
 for table in TABLES:
  text,labels=render(raw,table);assert not symbols.keys()&labels.keys();symbols.update(labels);all_labels.update(labels);pending[ROOT/table[1]]=text
 source_map=read('SourceMap');include=ROOT/'Source/Files/06_D3D.inc';include_text=include.read_text('utf-8');originals=[]
 def typed(table):return (table[2],table[3],'typed_data',table[1],0xC000+table[2])
 replacements=(
 ('Source/Resources/06_D3D/BeforePreviewBounds.bin',((0x2C28,0x2DB0,'code',path,0xEC28),)),
 ('Source/Resources/06_D3D/BeforeSquareTable.bin',((0,0x200,'unclassified','Source/Resources/06_D3D/BeforeSceneSeed.bin',None),typed(TABLES[0]),(0x203,0x20C,'unclassified','Source/Resources/06_D3D/BetweenSceneSeedMatrix.bin',None),typed(TABLES[1]),(0x21E,0x300,'unclassified','Source/Resources/06_D3D/AfterSceneMatrix.bin',None))),
 ('Source/Resources/06_D3D/BeforeLookupProducts.bin',((0xEFA,0x1000,'unclassified','Source/Resources/06_D3D/BeforeModelPointers.bin',None),typed(TABLES[2]),(0x102C,0x1518,'unclassified','Source/Resources/06_D3D/AfterModelPointers.bin',None))))
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
 for filename,number in (('BuildPreviewQueue',0),('CheckPreviewBounds',1),('InsertPreviewQueue',2)):
  literal='                include "../D3D/'+filename+'.asm"';pattern=re.compile(re.escape(literal)+r'(?:\s*;[^\n]*)?')
  assert len(pattern.findall(include_text))==1;include_text=pattern.sub(literal.ljust(80)+'; ('+str(number)+') жёсткий порядок, последовательное исполнение',include_text)
 pending[include]=include_text
 for filename in ('CheckPreviewBounds','InsertPreviewQueue'):
  p=ROOT/('Source/D3D/'+filename+'.asm');text=p.read_text('utf-8').replace('#ECAE','@D3D.BuildPreviewQueue.NextRecord')
  if filename=='CheckPreviewBounds':text=text.replace('порядок включений 0,1','порядок включений 1,2')
  aligned=[]
  for line in text.splitlines():
   if '@D3D.BuildPreviewQueue.NextRecord' in line and ';' in line:
    code,comment=line.split(';',1);assert len(code.rstrip())<80;line=code.rstrip().ljust(80)+';'+comment
   aligned.append(line)
  pending[p]=chr(10).join(aligned)+chr(10)
 flow[flow.index(previous)]=g;inventory=read('Inventory')
 inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow))
 inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for report,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+report+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');assert '| D3D | 14 | 14 |' in t;pending[p]=t.replace('| D3D | 14 | 14 |','| D3D | 15 | 15 |')+'\n| #EC28, банк 4 | [D3D.'+name+'](../'+path+') | '+description+' |\n'
 p=ROOT/'Docs/FunctionDetails/D3D.md';pending[p]=p.read_text('utf-8')+'\n['+name+'](../../'+path+') — см. [PreviewQueue](../PreviewQueueBuild.md).\n'
 p=ROOT/'Includes/Structs/Include.inc';t=p.read_text('utf-8');block=''
 for module,table_path,start,end,structure,fields,names in TABLES:
  assert 'struct '+structure not in t;block+='                ; физические исходные данные '+module+chr(10)+'                struct '+structure+chr(10)
  for field,width,meaning in fields:block+=(field.ljust(16)+('db #00' if width==1 else 'dw #0000')).ljust(80)+'; '+meaning+chr(10)
  block+='                ends'+chr(10)+'                assert '+structure+' == #'+format(sum(width for _,width,_ in fields),'02X')+chr(10)+chr(10)
 pending[p]=t.replace('                endif'+chr(10),block+'                endif'+chr(10))
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module PreviewQueueBuildState' not in t;block='                module PreviewQueueBuildState'+chr(10)
 for label,address,meaning in (('RawFirst',0xCEFC,'последняя прочитанная первая координата записи'),('RawSecond',0xCEFE,'последняя прочитанная вторая координата'),('RawThird',0xCF00,'последняя прочитанная третья координата'),('SavedSP',0xEEEF,'операнд LD SP восстановления настоящего CPU-стека'),('SizeSkip',0xED5C,'операнд первого JR масштаба, получает 6-b')):block+=(label.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+meaning+chr(10)
 block+='                endmodule'+chr(10)+chr(10);pending[p]=t.replace('                endif'+chr(10),block+'                endif'+chr(10))
 p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8')
 if 'SecondKeyBit' not in t:
  start=t.index('                module PreviewQueueConst');end=t.index('                endmodule',start);extra=''
  for label,value,meaning in (('SecondKeyBit',7,'разряд выбора второго ключа при сравнении узлов'),('SecondKeyMask',128,'маска заголовочного флага, передаваемого в Flags узла')):extra+=(label.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+meaning+chr(10)
  t=t[:end]+extra+t[end:]
 assert 'module PreviewQueueBuildConst' not in t;block='                module PreviewQueueBuildConst'+chr(10)
 constants=(('Objects',0xCDC0,'начало исходных записей объектов'),('RecordStep',64,'шаг записи объекта, первые десять байтов читает проход'),('MarkerHigh',128,'старший байт специальной записи конца либо отключения'),('CoeffMinBad',128,'неподдерживаемый модуль коэффициента минус 128'),('RawHighLimit',112,'исключённый модуль старшего байта исходной координаты'),('FirstHighEnd',96,'исключённый предел свёрнутого старшего байта первого результата'),('BaseIndexHigh',31,'порог старшего байта третьего результата для основного указателя'),('ModelPage',0xD0,'страница исходных пар указателей моделей'),('ScaleStart',6,'вычитаемое из показателя масштаба для смещения JR'),('ZeroPairFlag',1,'бит 0 при нулевых первом и третьем параметрах ориентации'))
 for label,value,meaning in constants:block+=(label.ljust(16)+'equ #'+format(value,'04X' if value>255 else '02X')).ljust(80)+'; '+meaning+chr(10)
 block+='                endmodule'+chr(10)+chr(10);pending[p]=t.replace('                endif'+chr(10),block+'                endif'+chr(10))
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
 report=dict(passed=True,instructions=len(added),code_bytes=392,bank=4,typed_bytes=65,scene_records=13,unknown_seed_fields=3,source_labels=len(all_labels),scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewQueueBuildClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

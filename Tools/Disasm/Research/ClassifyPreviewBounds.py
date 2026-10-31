"""Четыре знаковые границы D3D и последовательное включение очереди, точечный кандидат."""
from pathlib import Path
import collections,contextlib,copy,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from InspectZ80 import decoder
from PreviewBoundsFacts import FUNCTIONS,CONTRACTS,COMMENTS,LABELS,name_operands
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PreviewBoundsScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePreviewBounds'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewBoundsVerification')['passed']
 raw=payload(6);memory=bytearray(65536);memory[0xC000:0xC000+len(raw)]=raw
 added=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=6,offset=i.address-0xC000) for i in decoder(memory).disassemble(0xEDB0,0xEE24,'h')]
 assert b''.join(bytes.fromhex(i['hex']) for i in added)==raw[0x2DB0:0x2E24]
 flow=read('ControlFlow');previous=next(v for v in flow if v['name']=='D3D');g=copy.deepcopy(previous)
 old_bytes={i['address']+j for i in previous['instructions'] for j in range(len(bytes.fromhex(i['hex'])))}
 assert all(i['address']+j not in old_bytes for i in added for j in range(len(bytes.fromhex(i['hex']))))
 branches=set(g['branches']);known={i['address'] for i in g['instructions']+added}
 for i in added:
  import re
  match=re.fullmatch(r'(?:JP|JR) (?:[A-Z]+,)?#([0-9A-F]+)',i['operation'])
  if match:
   target=int(match[1],16);branches.add(target)
   if target not in known:g['unresolved'].append(dict(address=i['address'],operation=i['operation'],target=target,bank=4,reason='отказ проверки границ, продолжение вне выделенного диапазона'))
 g['branches']=sorted(branches)
 g['instructions']=sorted(g['instructions']+added,key=lambda i:i['address']);g['roots']=sorted(set(g['roots'])|set(FUNCTIONS));g['instruction_count']=len(g['instructions']);g['code_bytes']=sum(len(bytes.fromhex(i['hex'])) for i in g['instructions']);g['classified_fraction']=g['code_bytes']/g['total_bytes']
 validate_notes([g],{'D3D':COMMENTS});pending={};binaries={};symbols=read('Symbols');functions=read('Functions');code_ranges=[]
 for begin,(name,description) in FUNCTIONS.items():
  end=begin+116;path='Source/D3D/'+name+'.asm';rows=[i for i in added if begin<=i['address']<end]
  assert b''.join(bytes.fromhex(i['hex']) for i in rows)==raw[begin-0xC000:end-0xC000]
  lines=['                module D3D','                module '+name,'                ; Документация [четыре знаковые границы](../../Docs/PreviewBounds.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #'+format(begin-0xC000,'04X')+'..#'+format(end-0xC001,'04X')]
  for title,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',begin]):lines+=['                ; '+title+':']+['                ;   '+value for value in values]
  lines+=['                ; -----------------------------------------']
  for j,i in enumerate(rows):
   above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];label='Entry' if j==0 else LABELS.get(('D3D',i['address']),'')
   if label:
    symbol='D3D.'+name+'.'+label;assert symbol not in symbols;symbols[symbol]=i['address']
   op=name_operands('D3D',begin,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
   if right:assert len(line)<80;line=line.ljust(80)+'; '+right
   lines.append(line)
  lines+=['                endmodule','                endmodule'];child=next(f for f in functions if f['region']=='D3D' and f['address']==0xEE24);pending[ROOT/path]=format_function(chr(10).join(lines)+chr(10),target=child)
  functions.append(dict(region='D3D',name=name,address=begin,slot=6,offset=begin-0xC000,end_offset=end-0xC000,path=path,description=description,semantic_status='described'));code_ranges.append((begin-0xC000,end-0xC000,'code',path,begin))
 source_map=read('SourceMap');include=ROOT/'Source/Files/06_D3D.inc';include_text=include.read_text('utf-8');originals=[]
 replacements=(('Source/Resources/06_D3D/BeforeQueueInsert.bin',[(0x2C28,0x2DB0,'unclassified','Source/Resources/06_D3D/BeforePreviewBounds.bin',None),*code_ranges]),)
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
 bounds_include='                include "../D3D/CheckPreviewBounds.asm"';queue_include='                include "../D3D/InsertPreviewQueue.asm"'
 assert include_text.count(bounds_include)==1 and include_text.count(queue_include)==1
 include_text=include_text.replace(bounds_include,bounds_include.ljust(80)+'; (0) жёсткий порядок, последовательное исполнение').replace(queue_include,queue_include.ljust(80)+'; (1) жёсткий порядок, последовательное исполнение')
 pending[include]=include_text;flow[flow.index(previous)]=g;inventory=read('Inventory')
 inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow))
 inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for report,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+report+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');assert '| D3D | 13 | 13 |' in t;t=t.replace('| D3D | 13 | 13 |','| D3D | 14 | 14 |')
 for begin,(name,description) in FUNCTIONS.items():t+='\n| #'+format(begin,'04X')+', банк 4 | [D3D.'+name+'](../Source/D3D/'+name+'.asm) | '+description+' |\n'
 pending[p]=t;p=ROOT/'Docs/FunctionDetails/D3D.md';t=p.read_text('utf-8')
 for begin,(name,description) in FUNCTIONS.items():t+='\n['+name+'](../../Source/D3D/'+name+'.asm) — см. [PreviewLookupProducts](../PreviewBounds.md).\n'
 pending[p]=t
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module PreviewBoundsState' not in t
 block='                module PreviewBoundsState'+chr(10)
 for label,address,meaning in (('FirstSkip',0xEDC4,'операнд первого JR масштаба, заранее получает 6-b'),('SecondSkip',0xEDFD,'операнд второго JR масштаба, заранее получает 6-b')):block+=(label.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+meaning+chr(10)
 block+='                endmodule'+chr(10)+chr(10);pending[p]=t.replace('                endif'+chr(10),block+'                endif'+chr(10))
 p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8');assert 'module PreviewBoundsConst' not in t
 block='                module PreviewBoundsConst'+chr(10)
 for label,value,meaning in (('TablePage',0xC3,'исходная страница FoldedSquare127'),('FirstSeed',72,'затравка первой пары табличных граничных тестов'),('SecondSeed',66,'затравка второй пары табличных граничных тестов')):block+=(label.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+meaning+chr(10)
 block+='                endmodule'+chr(10)+chr(10);pending[p]=t.replace('                endif'+chr(10),block+'                endif'+chr(10));plan=[]
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
 report=dict(passed=True,instructions=len(added),code_bytes=116,bank=4,functions=1,hard_order_with_queue=True,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewBoundsClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

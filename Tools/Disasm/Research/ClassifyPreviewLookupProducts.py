"""Четыре табличных приближения D3D и исходная страница квадратов, точечный кандидат."""
from pathlib import Path
import collections,contextlib,copy,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from InspectZ80 import decoder
from PreviewLookupProductFacts import FUNCTIONS,CONTRACTS,COMMENTS
from PreviewSquareTable import PATH,START,END,render
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PreviewLookupProductsScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePreviewLookupProducts'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewLookupProductsVerification')['passed']
 raw=payload(6);memory=bytearray(65536);memory[0xC000:0xC000+len(raw)]=raw
 added=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=6,offset=i.address-0xC000) for i in decoder(memory).disassemble(0xD518,0xD54C,'h')]
 assert b''.join(bytes.fromhex(i['hex']) for i in added)==raw[0x1518:0x154C]
 flow=read('ControlFlow');previous=next(v for v in flow if v['name']=='D3D');g=copy.deepcopy(previous)
 old_bytes={i['address']+j for i in previous['instructions'] for j in range(len(bytes.fromhex(i['hex'])))}
 assert all(i['address']+j not in old_bytes for i in added for j in range(len(bytes.fromhex(i['hex']))))
 g['instructions']=sorted(g['instructions']+added,key=lambda i:i['address']);g['roots']=sorted(set(g['roots'])|set(FUNCTIONS));g['instruction_count']=len(g['instructions']);g['code_bytes']=sum(len(bytes.fromhex(i['hex'])) for i in g['instructions']);g['classified_fraction']=g['code_bytes']/g['total_bytes']
 validate_notes([g],{'D3D':COMMENTS});pending={};binaries={};symbols=read('Symbols');functions=read('Functions');code_ranges=[]
 for begin,(name,description) in FUNCTIONS.items():
  end=begin+13;path='Source/D3D/'+name+'.asm';rows=[i for i in added if begin<=i['address']<end]
  assert b''.join(bytes.fromhex(i['hex']) for i in rows)==raw[begin-0xC000:end-0xC000]
  lines=['                module D3D','                module '+name,'                ; Документация [табличные приближения произведения](../../Docs/PreviewLookupProducts.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #'+format(begin-0xC000,'04X')+'..#'+format(end-0xC001,'04X')]
  for title,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',begin]):lines+=['                ; '+title+':']+['                ;   '+value for value in values]
  lines+=['                ; -----------------------------------------']
  for j,i in enumerate(rows):
   above,right=COMMENTS.get(i['address'],([],None));assert right is None;lines+=['                ; '+v for v in above]
   lines.append(('Entry:'.ljust(16) if j==0 else ' '*16)+i['operation'].replace(',',', '))
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n');symbol='D3D.'+name+'.Entry';assert symbol not in symbols;symbols[symbol]=begin
  functions.append(dict(region='D3D',name=name,address=begin,slot=6,offset=begin-0xC000,end_offset=end-0xC000,path=path,description=description,semantic_status='described'));code_ranges.append((begin-0xC000,end-0xC000,'code',path,begin))
 text,labels=render(raw);assert not symbols.keys()&labels.keys();symbols.update(labels);pending[ROOT/PATH]=text
 source_map=read('SourceMap');include=ROOT/'Source/Files/06_D3D.inc';include_text=include.read_text('utf-8');originals=[]
 replacements=(
 ('Source/Resources/06_D3D/AfterPriceText.bin',[(0xEFA,0x1518,'unclassified','Source/Resources/06_D3D/BeforeLookupProducts.bin',None),*code_ranges,(0x154C,0x2011,'unclassified','Source/Resources/06_D3D/AfterLookupProducts.bin',None)]),
 ('Source/Resources/06_D3D/BeforeQueueStorage.bin',[(0,START,'unclassified','Source/Resources/06_D3D/BeforeSquareTable.bin',None),(START,END,'typed_data',PATH,0xC300),(END,0x700,'unclassified','Source/Resources/06_D3D/AfterSquareTable.bin',None)]))
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
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');assert '| D3D | 9 | 9 |' in t;t=t.replace('| D3D | 9 | 9 |','| D3D | 13 | 13 |')
 for begin,(name,description) in FUNCTIONS.items():t+='\n| #'+format(begin,'04X')+', банк 4 | [D3D.'+name+'](../Source/D3D/'+name+'.asm) | '+description+' |\n'
 pending[p]=t;p=ROOT/'Docs/FunctionDetails/D3D.md';t=p.read_text('utf-8')
 for begin,(name,description) in FUNCTIONS.items():t+='\n['+name+'](../../Source/D3D/'+name+'.asm) — см. [PreviewLookupProducts](../PreviewLookupProducts.md).\n'
 pending[p]=t;plan=[]
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
 report=dict(passed=True,instructions=len(added),code_bytes=52,bank=4,functions=4,typed_table_bytes=256,source_labels=len(labels),scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewLookupProductsClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

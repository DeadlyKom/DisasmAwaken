"""Исходный рисователь и три части ценового CP866-потока D3D, только точечный кандидат без сборки."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze,payload
from D3DPriceFacts import FUNCTIONS,CONTRACTS,COMMENTS,LABELS,name_operands
from PreviewPriceTable import PATH,START,END,render
from SourcePresentation import format_function
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/D3DPricesScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeD3DPrices'
RANGES=((0xE0C5,0xE124),)


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewPricesVerification')['passed'];raw=payload(6);g=analyze('D3D');flow=read('ControlFlow');previous=next(v for v in flow if v['name']=='D3D');old_addresses={i['address'] for i in previous['instructions']};added=[i for i in g['instructions'] if i['address'] not in old_addresses]
 assert not g['overlaps'] and sum(len(bytes.fromhex(i['hex'])) for i in added)==95 and all(i in g['instructions'] for i in previous['instructions'])
 pending={};binaries={};symbols=read('Symbols');functions=read('Functions');code_entries=[]
 for begin,end in RANGES:
  name,description=FUNCTIONS[begin];path='Source/D3D/'+name+'.asm';rows=[i for i in added if begin<=i['address']<end];assert b''.join(bytes.fromhex(i['hex']) for i in rows)==raw[begin-0xC000:end-0xC000]
  lines=['                module D3D','                module '+name,'                ; Документация [описания моделей](../../Docs/PreviewPrices.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #'+format(begin-0xC000,'04X')+'..#'+format(end-0xC001,'04X')]
  for title,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',begin]):lines+=['                ; '+title+':']+['                ;   '+value for value in values]
  lines+=['                ; -----------------------------------------']
  for j,i in enumerate(rows):
   above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];label='Entry' if j==0 else LABELS.get(('D3D',i['address']),'')
   if label:
    symbol='D3D.'+name+'.'+label;assert symbol not in symbols;symbols[symbol]=i['address']
   op=name_operands('D3D',begin,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
   if right:assert len(line.rstrip())<80;line=line.ljust(80)+'; '+right
   lines.append(line)
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n');functions.append(dict(region='D3D',name=name,address=begin,slot=6,offset=begin-0xC000,end_offset=end-0xC000,path=path,description=description,semantic_status='described'));code_entries.append((begin-0xC000,end-0xC000,'code',path,begin))
 text,labels=render(raw);assert not symbols.keys()&labels.keys();symbols.update(labels);pending[ROOT/PATH]=text;typed=(START,END,'typed_data',PATH,0xC000+START)
 source_map=read('SourceMap');replacements=(('Source/Resources/06_D3D/BeforeDescriptionCount.bin',[code_entries[0]]),('Source/Resources/06_D3D/BeforePreviewClip.bin',[(0,START,'unclassified','Source/Resources/06_D3D/BeforePriceText.bin',None),typed,(END,0x2011,'unclassified','Source/Resources/06_D3D/AfterPriceText.bin',None)]))
 include=ROOT/'Source/Files/06_D3D.inc';include_text=include.read_text('utf-8');originals=[]
 # Новые диапазоны обязаны точно и без промежутков покрывать заменяемые бинарные области.
 for old_path,entries in replacements:
  old=next(e for e in source_map if e['path']==old_path);p=ROOT/old_path;assert p.read_bytes()==raw[old['offset']:old['offset']+old['length']];originals.append(p);position=old['offset'];mapped=[];lines=[]
  for start,end,kind,path,origin in entries:
   assert start==position and start<end;position=end;blob=raw[start:end];mapped.append(dict(old,offset=start,length=end-start,kind=kind,path=path,origin=origin,sha256=hashlib.sha256(blob).hexdigest()))
   if kind=='unclassified':binaries[ROOT/path]=blob;lines.append('                incbin "../Resources/06_D3D/'+Path(path).name+'"')
   else:lines+=['                disp #'+format(origin,'04X'),'                include "../D3D/'+('Data/' if kind=='typed_data' else '')+Path(path).name+'"','                ent']
   lines.append('                assert $ == #'+format(end,'04X'))
  assert position==old['offset']+old['length'];index=source_map.index(old);source_map[index:index+1]=mapped;needle='                incbin "../Resources/06_D3D/'+Path(old_path).name+'"';assert include_text.count(needle)==1;include_text=include_text.replace(needle,'\n'.join(lines))
 pending[include]=include_text;flow[flow.index(previous)]=g;inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow));inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for name,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');assert '| D3D | 5 | 5 |' in text;text=text.replace('| D3D | 5 | 5 |','| D3D | 6 | 6 |')
 for begin,_ in RANGES:
  name,desc=FUNCTIONS[begin];text+='\n| #'+format(begin,'04X')+', банк 4 | [D3D.'+name+'](../Source/D3D/'+name+'.asm) | '+desc+' |\n'
 pending[p]=text;p=ROOT/'Docs/FunctionDetails/D3D.md';text=p.read_text('utf-8')
 for begin,_ in RANGES:
  name,_=FUNCTIONS[begin];text+='\n['+name+'](../../Source/D3D/'+name+'.asm) — см. [PreviewDescriptions](../PreviewPrices.md).\n'
 pending[p]=text
 for filename,address in (('DrawItem25',0x67E0),):
  p=ROOT/('Source/Station/'+filename+'.asm');text=p.read_text('utf-8');pending[p]=name_operands('Station',address,text)
 p=ROOT/'Includes/Const/Include.inc';text=p.read_text('utf-8');assert 'module PreviewPriceConst' not in text;block='                module PreviewPriceConst\n'
 for name,value,desc in (('HeadingCursor',0x0800,'упакованный курсор X=0, Y=8 для заголовка цен'),('BodyCursor',0x1800,'упакованный курсор X=0, Y=24 для ценовых строк'),('BodyY',0x18,'начальный пиксельный Y ценового тела'),('KarenIndex',6,'индекс собственного Карэна с особым разделителем')):block+=(name.ljust(16)+'equ #'+format(value,'04X' if value>255 else '02X')).ljust(80)+'; '+desc+'\n'
 pending[p]=text.replace('                endif\n',block+'                endmodule\n\n                endif\n')
 plan=[]
 # Отдельный кандидат и контроль отсутствия сторонних изменений перед применением.
 for p,value in {**pending,**binaries}.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists();assert (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 for p in originals:target=HISTORY/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление только заменённых бинарных дубликатов после проверки всех активных байтов и сохранённых копий.
 for p in originals:assert p.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and p.read_bytes()==(HISTORY/p.relative_to(ROOT)).read_bytes();p.unlink()
 report=dict(passed=True,instructions=len(added),code_bytes=95,typed_price_bytes=186,bank=4,source_labels_checked=12,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/D3DPricesClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

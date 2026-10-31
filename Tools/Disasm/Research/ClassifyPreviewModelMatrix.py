"""Точечный кандидат доказанной матрицы EF5E..F055, без сборки и массового экспорта."""
from pathlib import Path
import collections,contextlib,copy,hashlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from InspectZ80 import decoder
from PreviewModelMatrixFacts import FUNCTIONS,LABELS,CONTRACTS,COMMENTS,COEFFICIENTS,name_operands
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/PreviewModelMatrixScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforePreviewModelMatrix'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewModelMatrixVerification')['passed']
 begin=0xEF5E;end=0xF056;name,description=FUNCTIONS[begin];path='Source/D3D/'+name+'.asm'
 raw=payload(6);memory=bytearray(65536);memory[0xC000:0xC000+len(raw)]=raw;dis=decoder(memory)
 added=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=6,offset=i.address-0xC000) for i in dis.disassemble(begin,end,'h')]
 assert b''.join(bytes.fromhex(i['hex']) for i in added)==raw[begin-0xC000:end-0xC000]
 flow=read('ControlFlow');previous=next(v for v in flow if v['name']=='D3D');g=copy.deepcopy(previous)
 old_bytes={i['address']+j for i in previous['instructions'] for j in range(len(bytes.fromhex(i['hex'])))}
 assert all(i['address']+j not in old_bytes for i in added for j in range(len(bytes.fromhex(i['hex']))))
 g['instructions']=sorted(g['instructions']+added,key=lambda i:i['address']);g['roots']=sorted(set(g['roots'])|{begin})
 g['branches']=sorted(set(g['branches'])|{p for (_,p) in LABELS})
 g['instruction_count']=len(g['instructions']);g['code_bytes']=sum(len(bytes.fromhex(i['hex'])) for i in g['instructions']);g['classified_fraction']=g['code_bytes']/g['total_bytes']
 validate_notes([g],{'D3D':COMMENTS})
 symbols=read('Symbols');functions=read('Functions');pending={};binaries={}
 lines=['                module D3D','                module '+name,'                ; Документация [матрица ориентации модели](../../Docs/PreviewModelMatrix.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 6, банк 4, файловые смещения #2F5E..#3055']
 for title,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['D3D',begin]):lines+=['                ; '+title+':']+['                ;   '+v for v in values]
 lines+=['                ; -----------------------------------------']
 for index,i in enumerate(added):
  above,right=COMMENTS.get(i['address'],([],None));lines+=['                ; '+v for v in above];label='Entry' if index==0 else LABELS.get(('D3D',i['address']),'')
  if label:
   symbol='D3D.'+name+'.'+label;assert symbol not in symbols;symbols[symbol]=i['address']
  op=name_operands('D3D',begin,i['operation'].replace(',',', '));line=((label+':').ljust(16) if label else ' '*16)+op
  if right:assert len(line)<80,(i,line);line=line.ljust(80)+'; '+right
  lines.append(line)
 lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n')
 functions.append(dict(region='D3D',name=name,address=begin,slot=6,offset=begin-0xC000,end_offset=end-0xC000,path=path,description=description,semantic_status='described'))
 source_map=read('SourceMap');original_path='Source/Resources/06_D3D/AfterQueueInsert.bin';original=ROOT/original_path;old_range=next(e for e in source_map if e['path']==original_path)
 assert original.read_bytes()==raw[old_range['offset']:old_range['offset']+old_range['length']]
 ranges=((old_range['offset'],begin-0xC000,'unclassified','Source/Resources/06_D3D/BeforeModelMatrix.bin',None),(begin-0xC000,end-0xC000,'code',path,begin),(end-0xC000,old_range['offset']+old_range['length'],'unclassified','Source/Resources/06_D3D/AfterModelMatrix.bin',None))
 mapped=[];include_lines=[];position=old_range['offset']
 # Проверка полного смежного покрытия заменяемого физического диапазона.
 for start,finish,kind,target,origin in ranges:
  assert start==position and start<finish;position=finish;blob=raw[start:finish]
  mapped.append(dict(old_range,offset=start,length=finish-start,kind=kind,path=target,origin=origin,sha256=hashlib.sha256(blob).hexdigest()))
  if kind=='unclassified':binaries[ROOT/target]=blob;include_lines.append('                incbin "../Resources/06_D3D/'+Path(target).name+'"')
  else:include_lines+=['                disp #'+format(origin,'04X'),'                include "../D3D/'+name+'.asm"','                ent']
  include_lines.append('                assert $ == #'+format(finish,'04X'))
 assert position==old_range['offset']+old_range['length'];idx=source_map.index(old_range);source_map[idx:idx+1]=mapped
 p=ROOT/'Source/Files/06_D3D.inc';t=p.read_text('utf-8');needle='                incbin "../Resources/06_D3D/'+original.name+'"';assert t.count(needle)==1;pending[p]=t.replace(needle,'\n'.join(include_lines))
 flow[flow.index(previous)]=g;inventory=read('Inventory')
 inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(v['instruction_count'] for v in flow))
 inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for report,value in (('SourceMap',source_map),('Functions',functions),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+report+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module PreviewModelMatrixState' not in t;block='                module PreviewModelMatrixState\n'
 for pointer,label in COEFFICIENTS.items():block+=(label.ljust(16)+'equ #'+format(pointer,'04X')).ljust(80)+'; изменяемый байтовый операнд матрицы модели '+label[-2:]+'\n'
 block+='                endmodule\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Includes/Const/Include.inc';t=p.read_text('utf-8');assert 'module PreviewModelMatrixConst' not in t;block='                module PreviewModelMatrixConst\n'
 for label,value,meaning in (('OneAxisBit',0,'номер бита упрощённой ориентации по второму углу'),('QuarterTurn',64,'четверть оборота в байтовых угловых единицах'),('SinePage',0xC4,'старший байт адреса исходной синусоиды'),('ProductPage',0xC3,'старший байт адреса свёрнутых квадратов'),('Unit',127,'единичный коэффициент исходного масштаба')):block+=(label.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+meaning+'\n'
 block+='                endmodule\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');assert '| D3D | 15 | 15 |' in t;pending[p]=t.replace('| D3D | 15 | 15 |','| D3D | 16 | 16 |')+'\n| #EF5E, банк 4 | [D3D.'+name+'](../'+path+') | '+description+' |\n'
 p=ROOT/'Docs/FunctionDetails/D3D.md';pending[p]=p.read_text('utf-8')+'\n['+name+'](../../'+path+') — см. [PreviewModelMatrix](../PreviewModelMatrix.md).\n'
 # Регистрация всех фактических писателей девяти операндов, включая короткую ветвь.
 modified=read('ModifiedCode');p=ROOT/'Docs/ModifiedCode.md';t=p.read_text('utf-8');writers=0
 for i in added:
  match=re.fullmatch(r'LD \(#([0-9A-F]+)\),A',i['operation'])
  if not match or int(match[1],16) not in COEFFICIENTS:continue
  target=int(match[1],16);assert not any(v['region']=='D3D' and v['writer']==i['address'] and v['target']==target for v in modified)
  target_instruction=dis.disassemble(target-1,target,'h')[0]
  assert target_instruction.bytes==bytes((memory[target-1],0)) and target_instruction.operation.startswith('LD ')
  modified.append(dict(region='D3D',writer=i['address'],target=target,target_instruction=target-1,size=1,target_operation=target_instruction.operation,path=path));writers+=1
  t+='| D3D | #'+format(i['address'],'04X')+' | #'+format(target,'04X')+' | '+target_instruction.operation+' | ['+name+'.asm](../'+path+') |\n'
 assert writers==18;pending[p]=t;pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=json.dumps(modified,ensure_ascii=False,indent=2)+'\n'
 # Согласованное подключение фактов для будущих точечных исследовательских операций.
 for filename,extra in (('Knowledge.py',"\nfrom PreviewModelMatrixFacts import FUNCTIONS as PREVIEW_MODEL_MATRIX_FUNCTIONS\nFUNCTIONS['D3D'].update(PREVIEW_MODEL_MATRIX_FUNCTIONS)\n"),('Contracts.py',"\nfrom PreviewModelMatrixFacts import CONTRACTS as PREVIEW_MODEL_MATRIX_CONTRACTS\nCONTRACTS.update(PREVIEW_MODEL_MATRIX_CONTRACTS)\n"),('D3DClipFacts.py',"\nfrom PreviewModelMatrixFacts import COMMENTS as PREVIEW_MODEL_MATRIX_COMMENTS\nCOMMENTS.update(PREVIEW_MODEL_MATRIX_COMMENTS)\n"),('SemanticNames.py',"\nfrom PreviewModelMatrixFacts import LABELS as PREVIEW_MODEL_MATRIX_LABELS, DOCUMENTS as PREVIEW_MODEL_MATRIX_DOCUMENTS, name_operands as preview_model_matrix_name_operands\nLABELS.update(PREVIEW_MODEL_MATRIX_LABELS)\nDOCUMENTS.update(PREVIEW_MODEL_MATRIX_DOCUMENTS)\n")):
  p=ROOT/('Tools/Disasm/Research/'+filename);t=p.read_text('utf-8');assert 'from PreviewModelMatrixFacts' not in t
  if filename=='SemanticNames.py':
   needle='    operation = preview_queue_build_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = preview_model_matrix_name_operands(region, function_address, operation)')
  pending[p]=t+extra
 plan=[]
 # Создание кандидата, затем проверка отсутствия изменений рабочей копии перед применением.
 for p,value in {**pending,**binaries}.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление только заменённой копии после проверки байтов в сохранённой истории.
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,instructions=len(added),code_bytes=end-begin,bank=4,functions=1,registered_operand_writers=writers,scoped_candidate_and_history=True,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewModelMatrixClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Точечное разделение самостоятельных входов сценария и наведения торговой панели, без замены инструкций и адресов."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from SourcePresentation import instructions,format_function,continuity
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/TradePanelProceduresScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeTradePanelProceduresSplit'
SPLITS={0x7044:[(0x7044,'Unknown7044'),(0x7061,'Unknown7061')]}


def main():
 verify();assert not CANDIDATE.exists() and not HISTORY.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 functions=read('Functions');source_map=read('SourceMap');symbols=read('Symbols');flow=read('ControlFlow');manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));raw=(ROOT/(next(e for e in manifest['entries'] if e['slot']==4)['path']+'.sectors.bin')).read_bytes()
 originals=[next(f for f in functions if f['region']=='Station' and f['address']==a) for a in SPLITS];renames={};groups={}
 for f in originals:
  starts=SPLITS[f['address']];end=f['address']+f['end_offset']-f['offset'];parts=[]
  for i,(begin,name) in enumerate(starts):
   stop=starts[i+1][0] if i+1<len(starts) else end
   parts.append(dict(f,address=begin,name=name,offset=f['offset']+begin-f['address'],end_offset=f['offset']+stop-f['address'],path='Source/Station/'+name+'.asm',semantic_status=f['semantic_status'] if i==0 else 'unknown',description=f['description'] if i==0 else 'Unknown, самостоятельный исходный вход, договор оформляется отдельно'))
  groups[f['address']]=parts
  for key,value in symbols.items():
   if key.startswith('Station.'+f['name']+'.'):
    part=next(p for p in parts if p['address']<=value<p['address']+p['end_offset']-p['offset'])
    target='Station.'+part['name']+'.'+('Entry' if value==part['address'] else key.rsplit('.',1)[1])
    if target!=key:renames[key]=target
 def rewrite(text):
  for old,new in sorted(renames.items(),key=lambda item:-len(item[0])):text=text.replace(old,new)
  lines=[]
  for line in text.splitlines():
   if ';' in line and not line.lstrip().startswith(';'):
    code,comment=line.split(';',1);assert len(code.rstrip())<80;line=code.rstrip().ljust(80)+';'+comment
   lines.append(line)
  return '\n'.join(lines)+('\n' if text.endswith('\n') else '')
 def restore(op):
  for old,new in sorted(renames.items(),key=lambda item:-len(item[1])):op=op.replace(new,old)
  return op
 pending={};total_bytes=0;new_count=0
 for original in originals:
  source=(ROOT/original['path']).read_text('utf-8');code=[l for l in source.splitlines() if l.strip() and not l.lstrip().startswith(';') and not l[16:].strip().lower().startswith(('module ','endmodule'))]
  rows=[i for g in flow if g['name']=='Station' for i in g['instructions'] if i['slot']==4 and original['offset']<=i['offset']<original['end_offset']];assert len(rows)==len(code)
  parts=groups[original['address']]
  for part in parts:
   selected=[(i,line) for i,line in zip(rows,code) if part['offset']<=i['offset']<part['end_offset']]
   assert sum(len(bytes.fromhex(i['hex'])) for i,_ in selected)==part['end_offset']-part['offset']
   lines=['                module Station','                module '+part['name'],'; Документация [торговая панель](../../Docs/TradePanelEdits.md)','; -----------------------------------------','; '+part['description'],'; исходная запись 4, файловые смещения #'+format(part['offset'],'04X')+'..#'+format(part['end_offset']-1,'04X'),'; In:',';   Unknown, договор самостоятельного входа оформляется отдельно','; Out:',';   исходные инструкции и адреса сохранены','; Corrupt:',';   Unknown, разделение входов не доказывает полный регистровый договор','; -----------------------------------------']
   for index,(i,line) in enumerate(selected):lines.append(('Entry:'.ljust(16) if index==0 else line[:16])+rewrite(line).rstrip('\n')[16:])
   lines+=['                endmodule','                endmodule'];pending[ROOT/part['path']]=format_function('\n'.join(lines)+'\n')
  assert instructions(source)==[restore(op) for part in parts for op in instructions(pending[ROOT/part['path']])]
  index=functions.index(original);functions[index:index+1]=parts;index=next(i for i,e in enumerate(source_map) if e['path']==original['path']);old=source_map[index]
  source_map[index:index+1]=[dict(old,offset=f['offset'],length=f['end_offset']-f['offset'],origin=f['address'],path=f['path'],sha256=hashlib.sha256(raw[f['offset']:f['end_offset']]).hexdigest()) for f in parts]
  total_bytes+=original['end_offset']-original['offset'];new_count+=len(parts)-1
 for path in (ROOT/'Source').rglob('*'):
  if path.is_file() and path.suffix in ('.asm','.inc') and path not in pending:
   text=path.read_text('utf-8');changed=rewrite(text)
   if changed!=text:pending[path]=changed
 include=ROOT/'Source/Files/04_STATIONF.inc';s=pending.get(include,include.read_text('utf-8'))
 for original in originals:
  begin=s.index('                disp #'+format(original['address'],'04X')+'\n')
  stop=s.index('                ent',begin)+len('                ent')
  needle=s[begin:stop];assert s.count(needle)==1
  rows=[]
  for part in groups[original['address']]:rows+=['                disp #'+format(part['address'],'04X'),'                include "../Station/'+part['name']+'.asm"','                ent','                assert $ == #'+format(part['end_offset'],'04X')]
  s=s.replace(needle,'\n'.join(rows),1)
 following,order=continuity(functions,flow)
 for original in originals:
  for part in groups[original['address']]:
   path=ROOT/part['path'];pending[path]=format_function(pending[path],following.get(part['path']))
   if part['path'] in order:
    line='                include "../Station/'+part['name']+'.asm"'
    s=s.replace(line,line.ljust(80)+'; ('+str(order[part['path']])+') жёсткий порядок, последовательное исполнение',1)
 pending[include]=s
 for old,new in renames.items():assert new not in symbols;symbols[new]=symbols.pop(old)
 inventory=read('Inventory');inventory.update(fragments=len(functions),unknown=sum(f['semantic_status']=='unknown' for f in functions));inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map))
 for name,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 added=[part for original in originals for part in groups[original['address']][1:]]
 p=ROOT/'Docs/Functions.md';s=p.read_text('utf-8');import re
 local=[f for f in functions if f['region']=='Station'];s=re.sub(r'^\| Station \| \d+ \| \d+ \|','| Station | '+str(len(local))+' | '+str(sum(f['semantic_status']=='described' for f in local))+' |',s,flags=re.M)
 pending[p]=s+''.join('\n| #'+format(f['address'],'04X')+' | [Station.'+f['name']+'](../'+f['path']+') | Unknown, самостоятельный вход |\n' for f in added)
 p=ROOT/'Docs/FunctionDetails/Station.md';pending[p]=p.read_text('utf-8')+''.join('\n## '+f['name']+'\n\n[Station.'+f['name']+'](../../'+f['path']+') — самостоятельный вход, договор оформляется отдельно.\n' for f in added)
 p=ROOT/'Docs/TradePanelEdits.md';assert not p.exists();pending[p]='# Торговая панель\n\nСамостоятельные входы и общие хвосты отделены от обёрток рисования без изменения байтов. Назначение и договоры будут оформлены после исследования алгоритмов.\n\n'+''.join('- [Station.'+f['name']+'](../'+f['path']+')\n' for original in originals for f in groups[original['address']])
 plan=[]
 for path,text in pending.items():
  rel=path.relative_to(ROOT);data=text.encode('utf-8');target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,path.read_bytes() if path.exists() else None,data))
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists();assert (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 verify();report=dict(passed=True,original_bytes=total_bytes,added_procedure_boundaries=new_count,symbol_targets_renamed=len(renames),original_instructions_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/TradePanelSplitVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report))


if __name__=='__main__':main()

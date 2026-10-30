"""Проверка наложенного точечного кандидата без сборки, копирования проекта и изменения Source."""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from ClassifyEventActionCode import CANDIDATE,digest
from SourcePresentation import instructions


def main(candidate=None,documentation="Docs/StationEventActions.md",report_name="EventActionCandidateVerification"):
 candidate=candidate or CANDIDATE
 plan=json.loads((candidate/'Plan.json').read_text('utf-8'))
 def path_for(relative):
  candidate_path=candidate/relative
  return candidate_path if candidate_path.is_file() else ROOT/relative
 def read(name):return json.loads(path_for('Tools/Disasm/Reports/'+name+'.json').read_text('utf-8'))
 for item in plan['files']:
  assert digest((candidate/item['path']).read_bytes())==item['candidate_sha256'],item['path']
  current=ROOT/item['path'];assert (digest(current.read_bytes()) if current.exists() else None)==item['before_sha256'],item['path']
 functions=read('Functions');flow=read('ControlFlow');symbols=read('Symbols');source_map=read('SourceMap')
 previous=json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_text('utf-8'));known_paths={f['path'] for f in previous};new=[f for f in functions if f['path'] not in known_paths]
 def canonical(op):
  op=re.sub(r'@([A-Za-z_][A-Za-z_0-9.]*)',lambda m:'#'+format(symbols[m[1]],'X'),op)
  op=re.sub(r'#[0-9A-F]+',lambda m:'#'+format(int(m[0][1:],16),'X'),op)
  return re.sub(r'\s+','',op).upper()
 code_count=labels=unchanged=0
 # Проверка последовательности новых инструкций и адреса каждой новой метки по исходным длинам.
 for f in new:
  selected=[i for g in flow if g['name']==f['region'] for i in g['instructions'] if i['slot']==f['slot'] and f['offset']<=i['offset']<f['end_offset']]
  actual=instructions(path_for(f['path']).read_text('utf-8'));assert len(actual)==len(selected)
  assert all(canonical(a)==canonical(i['operation']) for a,i in zip(actual,selected)),f['path']
  lines=path_for(f['path']).read_text('utf-8').splitlines();iterator=iter(selected)
  for line in lines:
   if not line.strip() or line.lstrip().startswith(';') or line[16:].strip().lower().startswith(('module ','endmodule')):continue
   i=next(iterator);label=line[:16].strip().removesuffix(':')
   if label:assert symbols[f['region']+'.'+f['name']+'.'+label]==i['address'];labels+=1
  assert next(iterator,None) is None;code_count+=len(selected)
 # Проверка, что в двух прежних ручных исходниках меняются только метки и пояснения, а не их инструкции.
 for item in plan['files']:
  if item['before_sha256'] is not None and item['path'].startswith('Source/') and item['path'].endswith('.asm'):
   assert instructions(path_for(item['path']).read_text('utf-8'))==instructions((ROOT/item['path']).read_text('utf-8'));unchanged+=1
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entries={e['slot']:e for e in manifest['entries'] if not e['deleted']};coverage={slot:bytearray(e['allocated_length']) for slot,e in entries.items()};payloads={slot:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for slot,e in entries.items()}
 # Проверка непересекающегося покрытия всех исходных действующих областей и физических хешей диапазонов.
 for e in source_map:
  c=coverage[e['slot']];start,end=e['offset'],e['offset']+e['length'];assert not any(c[start:end]);c[start:end]=bytes([1])*e['length']
  assert digest(payloads[e['slot']][start:end])==e['sha256']
  if e['kind']=='unclassified' and e['path'] in {x['path'] for x in plan['files']}:assert path_for(e['path']).read_bytes()==payloads[e['slot']][start:end]
 assert all(all(c) for c in coverage.values())
 # Проверка относительного графа INCLUDE и INCBIN с наложением кандидата поверх текущего проекта.
 seen=set();bins=set()
 def walk(relative):
  if relative in seen:return
  p=path_for(relative);assert p.is_file(),relative;seen.add(relative)
  for kind,literal in re.findall(r'^\s*(?:\w+:\s*)?(include|incbin)\s+"([^"]+)"',p.read_text('utf-8'),re.M|re.I):
   target=((ROOT/relative).parent/literal).resolve();assert target.is_relative_to(ROOT);name=target.relative_to(ROOT).as_posix();assert name not in plan['deletes'],name
   if kind.lower()=='include':walk(name)
   else:assert path_for(name).is_file(),name;bins.add(name)
 walk('Builder/Main.asm');assert all(f['path'] in seen for f in functions)
 # Проверка двусторонних ссылок новых исходников и дополнительных входов.
 document=path_for(documentation).read_text('utf-8')
 for f in new:assert '../'+f['path'] in document and '../../'+documentation in path_for(f['path']).read_text('utf-8')
 for x in plan['extra_existing_labels']:assert '../'+x['path'] in document and '../../'+documentation in path_for(x['path']).read_text('utf-8')
 report=dict(passed=True,method='scoped_candidate_overlay_original_instructions_labels_physical_coverage_and_real_include_graph',
  plan_sha256=digest((candidate/'Plan.json').read_bytes()),
  candidate_files=len(plan['files']),new_fragments=len(new),new_instructions_checked=code_count,new_labels_checked=labels,
  existing_manual_sources_instruction_sequences_unchanged=unchanged,covered_bytes=sum(map(len,coverage.values())),
  include_text_files=len(seen),include_binary_files=len(bins),source_changed=False,semantic_completeness_proved=False,assembly_executed=False)
 (ROOT/('Tools/Disasm/Reports/'+report_name+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

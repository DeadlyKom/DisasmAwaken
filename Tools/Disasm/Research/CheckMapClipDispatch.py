"""Статический снимок таблицы и достижимость группы до и после обмена внутренней точки."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import BLOCKS,block,analyze


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 raw=(ROOT/(e['path']+'.sectors.bin')).read_bytes();codes=(0,1,2,4,5,6,8,9,10);pairs=[];roots={0xD4DD};effective={0xD4DD}
 # Поиск исходных целей только по девяти возможным кодам каждой точки.
 for first in codes:
  for second in codes:
   index=first*16+second;target=raw[0x1E00+index]|(raw[0x1F00+index]<<8);after_swap=first!=0 or second==0
   assert 0xD4DD<=target<0xDB63;roots.add(target)
   if after_swap:effective.add(target)
   pairs.append(dict(first=first,second=second,index=index,target=target,effective_after_inside_first_swap=after_swap))
 probes=[]
 for name,entries in (('ClipOriginalSnapshot',roots),('ClipAfterSwap',effective)):
  BLOCKS.append(block(7,0x14DD,0x686,0xD4DD,name,tuple(sorted(entries))))
  result=analyze(name);assert not result['overlaps'];probes.append(result)
 original,current=probes;assert (original['code_bytes'],original['instruction_count'])==(1670,685)
 assert (current['code_bytes'],current['instruction_count'])==(1658,681)
 effective_addresses={item['address'] for item in current['instructions']}
 only_initial=[item for item in original['instructions'] if item['address'] not in effective_addresses]
 assert len(only_initial)==4 and all(item['operation'].startswith('CALL ') for item in only_initial)
 # Проверка наличия реальных исходных меток всех корней, реестр символов сам по себе недостаточен.
 functions=json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_text('utf-8'))
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 region=next(group for group in flow if group['name']=='Map');actual_labels=set()
 for function in functions:
  if function['region']!='Map' or not 0x14DD<=function['offset']<0x1B63:continue
  source=(ROOT/function['path']).read_text('utf-8')
  code_lines=[line for line in source.splitlines() if line.strip() and not line.lstrip().startswith(';')
              and not line[16:].strip().lower().startswith(('module ','endmodule'))]
  selected=[item for item in region['instructions'] if function['offset']<=item['offset']<function['end_offset'] and item['slot']==7]
  assert len(code_lines)==len(selected)
  for line,item in zip(code_lines,selected):
   if re.fullmatch(r'\w+:',line[:16].strip()):actual_labels.add(item['address'])
 assert roots.issubset(actual_labels)
 report=dict(method='original_split_pointer_table_valid_outcode_pairs_and_direct_control_flow',passed=True,
  pairs=pairs,roots=sorted(roots),valid_outcodes=list(codes),code_bytes=1670,instructions=685,
  original_range_sha256=hashlib.sha256(raw[0x14DD:0x1B63]).hexdigest(),
  table_phase='original_disk_snapshot_before_workspace_writes',effective_pairs_after_swap=sum(pair['effective_after_inside_first_swap'] for pair in pairs),
  effective_roots=sorted(effective),effective_root_count_with_common_return=len(effective),effective_code_bytes=1658,effective_instructions=681,
  initial_table_only_call_entries=[item['address'] for item in only_initial],initial_table_only_instruction_count=4,initial_table_only_bytes=12,
  runtime_table_snapshot_verified=False,full_handler_semantics_proved=False,execution_model_run=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapClipDispatch.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({key:value for key,value in report.items() if key not in ('pairs','roots','effective_roots')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

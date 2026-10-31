"""Согласованность вызовов и переходов с уже выделенными инструкциями D3D, без расширения исходников."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[3]


def main():
 reports=ROOT/'Tools/Disasm/Reports';flow=json.loads((reports/'ControlFlow.json').read_text('utf-8'));g=next(v for v in flow if v['name']=='D3D')
 calls=set();branches=set();indirect=set()
 # Поиск целей только в зарегистрированных исходных инструкциях, наблюдения исполнения их не подменяют.
 for i in g['instructions']:
  match=re.fullmatch(r'(CALL|JP|JR|DJNZ) (?:[A-Z]+,)?#([0-9A-F]+)',i['operation'])
  if match:(calls if match[1]=='CALL' else branches).add(int(match[2],16))
  elif i['operation'] in ('JP (HL)','JP (IX)','JP (IY)'):indirect.add(i['address'])
 # Проверка, что все оформленные процедуры присутствуют в реестре корней и началах инструкций.
 functions=json.loads((reports/'Functions.json').read_text('utf-8'));entries={f['address'] for f in functions if f['region']=='D3D'};addresses={i['address'] for i in g['instructions']}
 assert entries<=set(g['roots']) and entries<=addresses
 assert calls==set(g['calls']) and branches==set(g['branches'])
 assert indirect<={v['address'] for v in g['unresolved']}
 assert all(v.get('target') not in addresses for v in g['unresolved'])
 report=dict(passed=True,region='D3D',instructions=g['instruction_count'],procedure_roots=len(entries),calls=len(calls),branches=len(branches),indirect_continuations=len(indirect),all_direct_target_sets_equal_registered_instructions=True,all_indirect_continuations_explicit=True,source_instructions_modified=False,assembly_executed=False,full_semantic_analysis_complete=False)
 (reports/'D3DRegisteredFlowVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

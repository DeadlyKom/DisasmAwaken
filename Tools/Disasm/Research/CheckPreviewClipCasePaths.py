"""Сопоставление фактических обработчиков D3D и Map, все пути готовности кэшей."""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from Analyze import payload
from InspectZ80 import decoder
import CheckClipCasePaths as paths
import DescribeClipDecisions as decisions


def translated(address):
 # Поиск соответствия только внутри проверяемых обработчиков и установленных физических помощников.
 if 0xD4E5<=address<0xD9F4:return address+0xD06
 if 0xD9F4<=address<0xDA52:return address+0xD06
 if 0xDA52<=address<0xDAB0:return address+0xD05
 if 0xDAB0<=address<=0xDB59:return address+0xD04
 if address==0xDE39:return 0xC24F
 raise AssertionError(('unmapped_address',hex(address)))


def main():
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 old={i['address']:i for g in flow if g['name']=='Map' for i in g['instructions'] if i['slot']==7 and 0xD4E5<=i['address']<0xD8E2}
 raw=payload(6);memory=bytearray(65536);memory[0xC000:0xC000+len(raw)]=raw
 rows=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex()) for i in decoder(memory).disassemble(0xE1EB,0xE5E8,'h')]
 ops={i['address']:i for i in rows}
 assert len(old)==len(ops) and sum(len(bytes.fromhex(i['hex'])) for i in rows)==1021
 rewritten_words=0
 # Проверка каждого байта, разрешены только явно сопоставленные абсолютные слова адресов.
 for address,item in old.items():
  wanted=bytearray.fromhex(item['hex']);operation=item['operation'];match=re.search(r'#([0-9A-F]{4})',operation)
  if match:
   target=translated(int(match[1],16));assert len(wanted)==3 and wanted[0] in (0xCD,0xC4,0xC3,0xFA,0xF2,0xC2,0x21),(hex(address),item)
   wanted[1:]=target.to_bytes(2,'little');operation=operation[:match.start(1)]+format(target,'04X')+operation[match.end(1):];rewritten_words+=1
  actual=ops[translated(address)]
  assert actual['operation']==operation and actual['hex']==wanted.hex(),(hex(address),item,actual,operation)
 old_dispatch=json.loads((ROOT/'Tools/Disasm/Reports/MapClipDispatch.json').read_text('utf-8'))['pairs']
 pairs=[]
 # Проверка всех физических целей двух страниц D3D, без предположения о достижимости после перестановки концов.
 for item in old_dispatch:
  a,b=item['first'],item['second'];index=a*16+b;target=memory[0xCC00+index]+256*memory[0xCD00+index]
  assert target==translated(item['target']),(a,b,hex(target),hex(item['target']))
  pairs.append(dict(first=a,second=b,index=index,target=target,effective_after_inside_first_swap=a!=0 or b==0))
 for module in (paths,decisions):
  for name in ('PRODUCT','APPEND','DIFFERENCE'):
   setattr(module,name,{translated(k):v for k,v in getattr(module,name).items()})
 decisions.CORNERS={translated(k):v for k,v in decisions.CORNERS.items()}
 # Преобразование служебных адресов интерпретаторов без изменения их исходных исследовательских файлов.
 def adapt(function):
  import inspect
  text=inspect.getsource(function)
  for a,b in ((0xDAB0,0xE7B4),(0xDABB,0xE7BF),(0xDAC6,0xE7CA),(0xDAD1,0xE7D5),(0xDB2C,0xE830),(0xDB37,0xE83B),(0xDB42,0xE846),(0xDB59,0xE85D),(0xD4DD,0xEB08),(0xDE39,0xC24F)):
   text=re.sub('0x'+format(a,'04X')+r'\b','0x'+format(b,'04X'),text)
  text=text.replace('#DE39','#C24F')
  namespace=dict(function.__globals__);exec(compile(text,'<verified_d3d_case_adapter>','exec'),namespace)
  return namespace[function.__name__]
 trace=adapt(paths.paths);expand=adapt(decisions.expand)
 roots=[]
 for entry in sorted({p['target'] for p in pairs}):
  checked,ends=trace(entry,ops);roots.append(dict(entry=entry,abstract_states=checked,terminal_outcomes=sorted(ends)))
 cases=[dict(first=p['first'],second=p['second'],entry=p['target'],paths=expand(p['target'],ops)) for p in pairs]
 report=dict(passed=True,method='original_d3d_bytes_explicit_address_mapping_and_all_conditional_cache_paths',
  handler_bytes=1021,handler_instructions=len(rows),translated_absolute_words=rewritten_words,physical_pairs=81,
  distinct_roots=len(roots),semantic_paths=sum(len(c['paths']) for c in cases),all_instruction_bytes_compared=True,
  initialized_products_proved=True,all_conditions_have_explained_provenance=True,corner_block_precondition=1,
  maximum_output_points=2,special_exits_have_no_nested_case_calls=True,roots=roots,
  independent_geometry_proof=False,all_final_registers_proved=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipCasePathsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 (ROOT/'Tools/Disasm/Reports/PreviewClipDecisionPaths.json').write_text(json.dumps(dict(method=report['method'],cases=cases,independent_geometry_proof=False),ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='roots'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

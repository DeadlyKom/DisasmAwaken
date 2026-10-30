"""Фактические адреса меток активных файлов по их месту среди исходных инструкций, без сборки."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[3]


def main():
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 source_map=read('SourceMap');flow=read('ControlFlow');symbols={name.upper():value for name,value in read('Symbols').items()}
 instructions={(item['slot'],item['offset']):item for group in flow for item in group['instructions']}
 missing=[];wrong=[];bad_labels=[];checked=0
 # Поиск реального адреса каждой кодовой метки по длинам подтверждённых инструкций текущего файла.
 for fragment in source_map:
  if fragment['kind']!='code':continue
  slot=fragment['slot'];position=fragment['offset'];end=position+fragment['length'];modules=[]
  for number,line in enumerate((ROOT/fragment['path']).read_text('utf-8').splitlines(),1):
   if not line.strip() or line.lstrip().startswith(';'):continue
   operation=line[16:].split(';',1)[0].strip();module=re.fullmatch(r'module\s+(.+)',operation,re.I)
   if module:modules.append(module[1]);continue
   if operation.lower()=='endmodule':modules.pop();continue
   prefix=line[:16].strip()
   if prefix:
    if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9.]*:',prefix):bad_labels.append(dict(path=fragment['path'],line=number,prefix=prefix))
    else:
     name='.'.join([*modules,prefix[:-1]]);address=instructions[slot,position]['address'] if position<end else fragment['origin']+fragment['length']
     if name.upper() not in symbols:missing.append(dict(path=fragment['path'],line=number,name=name,address=address))
     elif symbols[name.upper()]!=address:wrong.append(dict(path=fragment['path'],line=number,name=name,actual_address=address,registered_address=symbols[name.upper()]))
     checked+=1
   if operation:
    instruction=instructions[slot,position];position+=len(bytes.fromhex(instruction['hex']))
  assert position==end,(fragment['path'],position,end)
 report=dict(passed=not(missing or wrong or bad_labels),method='actual_source_label_positions_against_original_instruction_lengths_and_symbol_registry',
  labels_checked=checked,missing_symbol_bindings=missing,wrong_addresses=wrong,invalid_label_prefixes=bad_labels,
  assembler_executed=False,semantic_completeness_proved=False)
 (ROOT/'Tools/Disasm/Reports/SourceLabelsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

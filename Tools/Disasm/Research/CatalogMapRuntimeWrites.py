"""Фактические писатели изменяемых операндов карты, раздельно настройка окна и режим хвостовых масок."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[3]


def main():
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));instructions=[i for g in flow if g['name']=='Map' for i in g['instructions'] if i['slot']==7]
 symbols=json.loads((ROOT/'Tools/Disasm/Reports/Symbols.json').read_text('utf-8'));records=[]
 # Поиск только прямых фактических записей в двух доказанных областях исходного кода.
 for i in instructions:
  phase='window_setup' if 0xD0C3<=i['address']<0xD1AC else 'arc_tail_mode' if 0xDFC3<=i['address']<0xDFD8 else None
  if phase is None:continue
  m=re.fullmatch(r'LD \(#([0-9A-F]+)\),(A|HL|DE|BC|SP)',i['operation'])
  if not m:continue
  target=int(m[1],16);width=1 if m[2]=='A' else 2;owners=[]
  for address in range(target,target+width):
   owner=next((op for op in instructions if op['address']<=address<op['address']+len(bytes.fromhex(op['hex']))),None)
   owners.append(None if owner is None else dict(address=owner['address'],operation=owner['operation'],byte_offset=address-owner['address']))
  records.append(dict(phase=phase,writer=i['address'],register=m[2],target=target,width=width,instruction_owners=owners,
   existing_symbols=[name for name,value in symbols.items() if value==target and name.startswith(('Map','FProjected'))]))
 report=dict(passed=True,method='direct_original_map_writers_to_actual_instruction_bytes_and_data_addresses',
  writes=records,write_instructions=len(records),distinct_target_bytes=len({a for row in records for a in range(row['target'],row['target']+row['width'])}),
  setup_execution_proved=False,all_game_writers_proved=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapRuntimeWrites.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='writes'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Отдельная статическая разведка D3D банка 4 по исходным внешним вызовам, без экспорта исходников и сборки."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
import Analyze


def main():
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));station=next(g for g in flow if g['name']=='Station');calls=[c for c in station['unresolved'] if c.get('bank')==4 and c.get('target',0)>=0xC000];roots=sorted({c['target'] for c in calls})
 assert roots==[0xE07F,0xE0B5,0xE0C5,0xE124,0xE13C,0xE154]
 # Разведка по дополнительным исходным корням не заменяет карту уже выделенных исходников проекта.
 result=Analyze.analyze('D3D',extra_roots=roots,initial_bank=4);raw=Analyze.payload(6)
 assert not result['overlaps'] and all(raw[i['offset']:i['offset']+len(bytes.fromhex(i['hex']))]==bytes.fromhex(i['hex']) for i in result['instructions'])
 code={i['address']:i for i in result['instructions']}
 assert code[0xE0AD]['operation']=='CALL #EC28' and code[0xE0B0]['operation']=='EI' and code[0xE0B1]['operation']=='CALL #6364' and code[0xE0B4]['operation']=='RET'
 # Фиксация исходных байтов заголовков по назначениям двух опорных групп помощника 6364.
 import re
 helper=[i for i in station['instructions'] if 0x6364<=i['address']<0x6396]
 helper_targets=[]
 for i in helper:
  match=re.fullmatch(r'LD \(#([0-9A-F]+)\),A',i['operation'])
  if match:
   address=int(match[1],16);helper_targets.append(dict(address=address,disk_byte_bank4=raw[address-0xC000]))
 assert len(helper_targets)==13
 report=dict(method='static_original_bank4_trace_from_station_calls_without_source_export',passed=True,slot=6,bank=4,load_address=0xC000,logical_bytes=15978,sector_bytes=len(raw),sector_sha256=hashlib.sha256(raw).hexdigest(),external_entries=roots,external_calls=calls,instruction_count=result['instruction_count'],code_bytes=result['code_bytes'],overlaps=result['overlaps'],unresolved=result['unresolved'],decoded_sequence_sha256=hashlib.sha256('\n'.join(format(i['address'],'04X')+':'+i['hex'] for i in result['instructions']).encode('ascii')).hexdigest(),preview_tail=[code[a] for a in (0xE0AD,0xE0B0,0xE0B1,0xE0B4)],source_map_modified=False,source_export_executed=False,contracts_proved=False,fixed_helper_6364_bank4_disk_targets=helper_targets,helper_6364_observed_positive_face_header_roles_proved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/D3DPreviewDiscovery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ('external_calls','unresolved','preview_tail','fixed_helper_6364_bank4_disk_targets')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

"""Проверка фактических ресурсов, строк и фаз, без ассемблера и без переупаковки образа."""
from pathlib import Path
import hashlib,json
from MarkerSpriteTables import RESOURCES
ROOT=Path(__file__).resolve().parents[3]


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();rows=0;records=[]
 for name,address in RESOURCES:
  data=source[address-0xC000:address-0xC000+128];assert len(data)==128
  # Проверка каждой двухбайтовой строки относительно нулевой фазы, включая сохранённый конец.
  for phase in range(8):
   for row in range(8):
    base=int.from_bytes(data[2*row:2*row+2],'big');actual=int.from_bytes(data[phase*16+2*row:phase*16+2*row+2],'big')
    assert actual==base>>phase,(name,phase,row);rows+=1
   assert data[phase*16+14:phase*16+16]==bytes(2)
  records.append(dict(name=name,address=address,sha256=hashlib.sha256(data).hexdigest()))
 report=dict(passed=True,resources=records,bytes_checked=768,phase_records=48,row_words_checked=rows,
  method='all_original_marker_phase_words_against_independent_16_bit_right_shifts',
  renderer_reads_seven_rows=True,preserved_unknown_tail_bytes=96,global_tail_purpose_proved=False,
  native_execution=False,assembly_executed=False,semantic_completeness_proved=False)
 (ROOT/'Tools/Disasm/Reports/MarkerSpriteResourcesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='resources'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

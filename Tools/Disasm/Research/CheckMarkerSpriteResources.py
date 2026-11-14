"""Проверка фактических ресурсов, строк и фаз, без ассемблера и без переупаковки образа."""
from pathlib import Path
import hashlib,json
import re
from zipfile import ZipFile
from MarkerSpriteTables import RESOURCES
from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256, load_sources
from CheckControlsArchivedHyperEffect import read_entry
ROOT=Path(__file__).resolve().parents[3]


def archived_markers():
 sources,_,_=load_sources()
 source=next(row for row in sources if row['member']=='awk6.trd' and row['name']=='KARTA   a')
 lines=source['content'].split(b'\r')
 with ZipFile(ARCHIVE) as archive:
  origin,compiled,_=read_entry(archive.read('awk6.trd'),b'KARTA   C')
 assert origin==0xC000
 result={}
 pattern=re.compile(rb'\x06[\x80-\x8f]\x05g\x06\x83(%[01]{8}|0),(%[01]{8}|0)')
 for (name,address),identifier in zip(RESOURCES,(b'SPLUS',b'SMINI',b'STREUG',b'SNULL',b'SKREST',b'SQUADR')):
  index=lines.index(identifier);data=bytearray()
  # Сверка каждой авторской пары DB, включая нулевые конечные пары всех фаз.
  for line in lines[index+1:index+65]:
   match=pattern.fullmatch(line);assert match,(identifier,line)
   data.extend(int(value[1:],2) if value.startswith(b'%') else 0 for value in match.groups())
  assert len(data)==128 and compiled[address-origin:address-origin+128]==data
  result[name]=(bytes(data),dict(archived_identifier=identifier.decode('ascii'),
   source='awk6.trd:KARTA.a',label_line=index+1,first_DB_line=index+2,last_DB_line=index+65,
   authored_pair_lines=64,compiled_source='awk6.trd:KARTA.C'))
 return result


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();rows=0;records=[]
 archived=archived_markers()
 for name,address in RESOURCES:
  data=source[address-0xC000:address-0xC000+128];assert len(data)==128
  archived_data,provenance=archived[name];assert data==archived_data
  # Проверка каждой двухбайтовой строки относительно нулевой фазы, включая сохранённый конец.
  for phase in range(8):
   for row in range(8):
    base=int.from_bytes(data[2*row:2*row+2],'big');actual=int.from_bytes(data[phase*16+2*row:phase*16+2*row+2],'big')
    assert actual==base>>phase,(name,phase,row);rows+=1
   assert data[phase*16+14:phase*16+16]==bytes(2)
  records.append(dict(name=name,address=address,sha256=hashlib.sha256(data).hexdigest(),archived_provenance=provenance))
 report=dict(passed=True,resources=records,bytes_checked=768,phase_records=48,row_words_checked=rows,
  method='all_original_marker_phase_words_against_independent_16_bit_right_shifts',
  renderer_reads_seven_rows=True,preserved_unknown_tail_bytes=96,global_tail_purpose_proved=False,
  source_archive_sha256=ARCHIVE_SHA256,all_authored_DB_bytes_matched=True,
  exact_archived_compiled_marker_block_matched=True,
  native_execution=False,assembly_executed=False,semantic_completeness_proved=False)
 (ROOT/'Tools/Disasm/Reports/MarkerSpriteResourcesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='resources'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

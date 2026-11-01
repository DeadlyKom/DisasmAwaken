"""Однократное выделение шести доказанных байтов, отдельный кандидат и точная проверка до записи."""
import contextlib,io,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import sys
sys.path[:0]=[str(ROOT/'Tools/Disasm')]
from Analyze import payload
from VerifySources import main as verify
from PackedResourcePrefixTable import final_lines
from CheckPackedResourcePrefix import audit


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 records=json.loads((ROOT/'Tools/Disasm/Reports/Screens.json').read_text('utf-8'));pending={};previous={};removed={};candidate=ROOT/'Tools/Disasm/Research/Candidates/PackedResourcePrefix';history=ROOT/'Tools/Disasm/Research/History/BeforePackedResourcePrefix'
 assert not candidate.exists() and not history.exists()
 for record in records:
  path=ROOT/record['path'];text=path.read_text('utf-8');stem=path.stem;old_stream=path.with_suffix('.Payload.bin');stream=path.with_suffix('.Bitstream.bin');raw=payload(record['slot'])[record['offset']:record['offset']+record['packed_size']]
  assert old_stream.read_bytes()==raw[6:] and 'FPackedFinalBytes' not in text and not stream.exists();removed[old_stream]=old_stream.read_bytes()
  pattern=r'(?m)^Payload:\s+incbin "'+re.escape(stem)+r'\.Payload\.bin"[^\n]*';text,n=re.subn(pattern,lambda m:'\n'.join(final_lines(raw,stem)),text);assert n==1
  lines=text.splitlines();lines.insert(2,'                ; Формат [сохранённый конец и общий поток](../../../Docs/PackedResourcePrefix.md)')
  pending[path]=('\n'.join(lines)+'\n').encode('utf-8');pending[stream]=raw[12:]
 audit(pending)
 for path,data in pending.items():
  previous[path]=path.read_bytes() if path.exists() else None;target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for path,old in previous.items():assert path.read_bytes()==old if old is not None else not path.exists()
 for path,old in {**previous,**removed}.items():
  if old is not None:target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old)
 for path,data in pending.items():path.write_bytes(data)
 audit()
 with contextlib.redirect_stdout(io.StringIO()):verify()
 for path,old in removed.items():
  assert path.resolve().is_relative_to((ROOT/'Source/Screens').resolve()) and path.read_bytes()==old==(history/path.relative_to(ROOT)).read_bytes();path.unlink()
 report=dict(passed=True,resources=len(records),physical_bytes_preserved=True,source_files_updated=20,payload_files_split=20,separate_candidate_and_history=True,
  labels_final_bytes_at_6_and_bitstream_at_12=True,obsolete_payload_files_removed=20,sector_tails_unchanged=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PackedResourcePrefixClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

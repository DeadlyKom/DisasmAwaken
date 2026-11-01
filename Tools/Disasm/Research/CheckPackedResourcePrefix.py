"""Физические экземпляры финальных слов, их метки и весь секторный хвост двадцати ресурсов."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
from Analyze import payload


def audit(overrides=None):
 overrides=overrides or {};records=json.loads((ROOT/'Tools/Disasm/Reports/Screens.json').read_text('utf-8'));checked=[]
 def read(path):return overrides[path] if path in overrides else path.read_bytes()
 for record in records:
  path=ROOT/record['path'];text=read(path).decode('utf-8');code='\n'.join(line.split(';',1)[0] for line in text.splitlines())
  parts=[];residual=code
  for typename,label in (('FPackedHeader','Header'),('FPackedFinalBytes','FinalBytes')):
   match=re.search(r'(?m)^'+label+r':\s+'+typename+r'\s*\{([^}]+)\}',code);assert match,(path,label)
   words=[int(value.strip().removeprefix('#'),16) for value in match[1].split(',')];assert len(words)==3
   parts.append(b''.join(word.to_bytes(2,'little') for word in words))
   residual=residual.replace(match[0],'',1)
  binaries=re.findall(r'(?m)^(Bitstream|Tail):\s+incbin "([^"\n]+)"',code);assert [label for label,_ in binaries]==['Bitstream','Tail']
  stream,tail=(read(path.parent/name) for _,name in binaries);raw=parts[0]+parts[1]+stream+tail;offset=record['offset'];original=payload(record['slot'])[offset:offset+record['allocated_size']]
  assert raw==original and len(stream)==record['packed_size']-12 and len(tail)==record['allocated_size']-record['packed_size']
  assert parts[1]==original[6:12] and code.index('Header:')<code.index('FinalBytes:')<code.index('Bitstream:')<code.index('Tail:')
  for line in residual.splitlines():
   stripped=line.strip()
   if not stripped:continue
   assert re.fullmatch(r'(module [A-Za-z0-9_]+|endmodule|assert \$ - Header == #[0-9A-F]{4}|(?:Bitstream|Tail):\s+incbin "Screen\d{2}\.(?:Bitstream|Tail)\.bin")',stripped),(path,stripped)
  checked.append(dict(path=record['path'],slot=record['slot'],index=record['index'],final_bytes_offset=6,bitstream_offset=12,tail_offset=record['packed_size'],allocated_size=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 return dict(passed=True,resources=len(checked),final_word_instances=len(checked),typed_final_bytes=6*len(checked),records=checked,
  whole_allocations_and_sector_tails_equal_original=True,label_offsets_checked=True,ordinary_build_requires_python=False,assembly_executed=False)


def main():
 report=audit();(ROOT/'Tools/Disasm/Reports/PackedResourcePrefixVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()

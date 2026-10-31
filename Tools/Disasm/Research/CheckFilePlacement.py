"""Сверка реальных DISP, ENT и физических смещений файловых включений с SourceMap без сборки."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[3]


def audit(overrides=None):
 source_map=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'));errors=[];checked=0;assertions=0;files=0
 for path in sorted((ROOT/'Source/Files').glob('*.inc')):
  match=re.match(r'(\d+)_',path.name)
  if not match:continue
  slot=int(match[1]);entries=[e for e in source_map if e['slot']==slot];position=0;origin=None;seen=[];files+=1
  text=(overrides or {}).get(path.name,path.read_text('utf-8'))
  for number,line in enumerate(text.splitlines(),1):
   code=line.split(';',1)[0].strip()
   if not code:continue
   item=re.fullmatch(r'assert \$ == #([0-9A-Fa-f]+)',code,re.I)
   if item:
    assertions+=1
    if position!=int(item[1],16):errors.append(dict(file=path.name,line=number,kind='physical_assertion',expected=int(item[1],16),actual=position))
    continue
   item=re.fullmatch(r'disp #([0-9A-Fa-f]+)',code,re.I)
   if item:
    if origin is not None:errors.append(dict(file=path.name,line=number,kind='nested_disp'))
    origin=int(item[1],16);continue
   if code.lower()=='ent':
    if origin is None:errors.append(dict(file=path.name,line=number,kind='ent_without_disp'))
    origin=None;continue
   item=re.fullmatch(r'(include|incbin) "([^"]+)"',code,re.I)
   if item:
    target=(path.parent/item[2]).resolve();relative=target.relative_to(ROOT).as_posix();matches=[e for e in entries if e['path']==relative]
    if len(matches)!=1:errors.append(dict(file=path.name,line=number,kind='ambiguous_map_entry',target=relative,matches=len(matches)));continue
    entry=matches[0];checked+=1;seen.append(relative)
    if position!=entry['offset']:errors.append(dict(file=path.name,line=number,kind='physical_offset',target=relative,expected=entry['offset'],actual=position))
    # INC BIN не содержит собственных меток, логический адрес ресурса в реестре не требует DISP.
    if item[1].lower()=='include' and origin!=entry['origin']:errors.append(dict(file=path.name,line=number,kind='logical_origin',target=relative,expected=entry['origin'],actual=origin))
    position+=entry['length']
    if origin is not None:origin+=entry['length']
    continue
   errors.append(dict(file=path.name,line=number,kind='unsupported_directive',text=code))
  if origin is not None:errors.append(dict(file=path.name,kind='unterminated_disp'))
  missing=[e['path'] for e in entries if e['path'] not in seen]
  if missing:errors.append(dict(file=path.name,kind='missing_ranges',paths=missing))
 return dict(method='actual_file_include_order_physical_offsets_and_disp_origins_against_source_map',passed=not errors,files=files,ranges_checked=checked,physical_assertions_checked=assertions,errors=errors,assembly_executed=False)


def main():
 report=audit()
 # Контроль чувствительности выполняется только над строкой в памяти, файлы проекта не меняются.
 text=(ROOT/'Source/Files/06_D3D.inc').read_text('utf-8');needle='disp #E13C\n                include \"../D3D/SetupPreviewModel.asm\"';assert text.count(needle)==1
 probe=audit({'06_D3D.inc':text.replace(needle,needle.replace('#E13C','#E0B5'))})
 assert not probe['passed'] and any(e['kind']=='logical_origin' and e.get('target')=='Source/D3D/SetupPreviewModel.asm' and e['actual']==0xE0B5 and e['expected']==0xE13C for e in probe['errors'])
 report['misplaced_code_probe_rejected']=True
 (ROOT/'Tools/Disasm/Reports/FilePlacementVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()

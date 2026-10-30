"""Однократное точечное оформление двух существующих байтов состояния углов."""
from pathlib import Path
import collections,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from ClipWorkTables import CORNERS,render
from VerifySources import main as verify


def main():
 verify();history=ROOT/'Tools/Disasm/Research/History/BeforeClipCornerState';assert not history.exists()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def write(n,v):(ROOT/('Tools/Disasm/Reports/'+n+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
 assert read('ClipSegmentVerification')['passed'] and read('ClipTailVerification')['passed']
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==7)
 raw=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();texts,symbols=render(raw);text=texts[CORNERS]
 old=ROOT/'Source/Resources/07_KARTA/BeforeClipOutputSize.bin';assert old.read_bytes()==raw[0x1E39:0x1E3B]==bytes(2)
 candidate=ROOT/'Tools/Disasm/Research/Candidates/ClipCornerStateScoped'/CORNERS;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_text(text,'utf-8')
 include=ROOT/'Source/Files/07_KARTA.inc';before=include.read_text('utf-8');needle='                incbin "../Resources/07_KARTA/BeforeClipOutputSize.bin"';assert needle in before
 after=before.replace(needle,'                disp #DE39\n                include "../Map/Data/ClipCornerState.asm"\n                ent',1)
 for p in (old,include,*[ROOT/('Tools/Disasm/Reports/'+n+'.json') for n in ('SourceMap','Symbols','Inventory')]):
  backup=history/p.relative_to(ROOT);backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
 (ROOT/CORNERS).write_text(text,'utf-8');include.write_text(after,'utf-8')
 sm=read('SourceMap');item=next(x for x in sm if x['path']==old.relative_to(ROOT).as_posix());item.update(kind='typed_data',path=CORNERS,origin=0xDE39);write('SourceMap',sm)
 sy=read('Symbols');sy.update(symbols);write('Symbols',sy)
 inv=read('Inventory');inv['physical_bytes_by_kind']={k:sum(x['length'] for x in sm if x['kind']==k) for k in sorted({x['kind'] for x in sm})};inv['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));write('Inventory',inv)
 verify();assert old.resolve().is_relative_to(ROOT/'Source/Resources/07_KARTA') and old.read_bytes()==(history/old.relative_to(ROOT)).read_bytes();old.unlink()
 print('Two original bytes, physical FClipCornerState instance, no new allocation')


if __name__=='__main__':main()

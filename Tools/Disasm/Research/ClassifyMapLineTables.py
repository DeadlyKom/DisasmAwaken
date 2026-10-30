"""Однократное оформление 22 исходных байтов состояния и масок без изменения физического порядка."""
from pathlib import Path
import collections,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from MapLineTables import POINTS,MODE,MASKS,render
from VerifySources import main as verify


def main(spec=None):
 spec=spec or {};verify();history=ROOT/'Tools/Disasm/Research/History'/spec.get('history','BeforeMapLineTables');assert not history.exists()
 slot=spec.get('slot',7);origin=spec.get('origin',0xC000);resource_dir=spec.get('resource_dir','07_KARTA')
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def write(n,v):(ROOT/('Tools/Disasm/Reports/'+n+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
 assert read(spec.get('model','MapLineVerification'))['passed']
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==slot)
 raw=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();texts,symbols=spec.get('render',render)(raw)
 specs=spec.get('parts',(('BeforeClipEndpoints.bin',((0x1DB0,0x1E2B,'unclassified','Source/Resources/07_KARTA/BeforeMapLinePoints.bin'),(0x1E2B,0x1E2F,'typed_data',POINTS))),
  ('AfterClipOutputSize.bin',((0x1E3C,0x1E3E,'typed_data',MODE),(0x1E3E,0x1E6B,'unclassified','Source/Resources/07_KARTA/AfterMapLineMode.bin'))),
  ('Unclassified005.bin',((0x1418,0x1420,'unclassified','Source/Resources/07_KARTA/BeforeMapLineMasks.bin'),(0x1420,0x1430,'typed_data',MASKS)))))
 pending={ROOT/path:text.encode('utf-8') for path,text in texts.items()};sm=read('SourceMap');old_files=[];include=ROOT/('Source/Files/'+resource_dir+'.inc');content=include.read_text('utf-8')
 for old_name,parts in specs:
  old=ROOT/'Source/Resources'/resource_dir/old_name;item=next(x for x in sm if x['path']==old.relative_to(ROOT).as_posix())
  assert old.read_bytes()==raw[item['offset']:item['offset']+item['length']] and parts[0][0]==item['offset'] and parts[-1][1]==item['offset']+item['length'];old_files.append(old)
  position=sm.index(item);new=[];lines=[]
  for begin,end,kind,path in parts:
   new.append(dict(slot=slot,offset=begin,length=end-begin,kind=kind,path=path,origin=begin+origin if kind=='typed_data' else None,sha256=hashlib.sha256(raw[begin:end]).hexdigest()))
   if kind=='typed_data':lines+=['                disp #'+format(begin+origin,'04X'),'                include "../'+path.removeprefix('Source/')+'"','                ent']
   else:pending[ROOT/path]=raw[begin:end];lines+=['                incbin "../'+path.removeprefix('Source/')+'"']
   lines+=['                assert $ == #'+format(end,'04X')]
  sm[position:position+1]=new;needle='                incbin "../Resources/'+resource_dir+'/'+old_name+'"';assert needle in content
  content=content.replace(needle,'\n'.join(lines),1)
 pending[include]=content.encode('utf-8');candidate=ROOT/'Tools/Disasm/Research/Candidates'/spec.get('candidate','MapLineTablesScoped')
 for path,data in pending.items():
  target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for path in [*old_files,include,*[ROOT/('Tools/Disasm/Reports/'+n+'.json') for n in ('SourceMap','Symbols','Inventory')]]:
  target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 for path,data in pending.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 write('SourceMap',sm);sy=read('Symbols');sy.update(symbols);write('Symbols',sy)
 inv=read('Inventory');inv['physical_bytes_by_kind']={k:sum(x['length'] for x in sm if x['kind']==k) for k in sorted({x['kind'] for x in sm})};inv['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));write('Inventory',inv);verify()
 for old in old_files:
  assert old.resolve().is_relative_to(ROOT/'Source/Resources'/resource_dir) and old.read_bytes()==(history/old.relative_to(ROOT)).read_bytes();old.unlink()
 print(str(sum(end-begin for _,parts in specs for begin,end,kind,_ in parts if kind=='typed_data'))+' original bytes typed, all other original bytes preserved, no new allocation')


if __name__=='__main__':main()

"""Однократное выделение 81 исходного байта построителей таблиц, без сборки и массового экспорта."""
from pathlib import Path
import collections,hashlib,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import BLOCKS,block,analyze
from SourcePresentation import format_function
from VerifySources import main as verify


def main():
 verify();history=ROOT/'Tools/Disasm/Research/History/BeforeMapSectorCode';assert not history.exists()
 BLOCKS.append(block(7,0x44A,0x51,0xC44A,'MapSectorProbe',(0xC44A,0xC474)))
 probe=analyze('MapSectorProbe');assert probe['code_bytes']==81
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def write(name,value):(ROOT/('Tools/Disasm/Reports/'+name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 raw=(ROOT/(e['path']+'.sectors.bin')).read_bytes();functions=read('Functions');flow=read('ControlFlow');region=next(g for g in flow if g['name']=='Map')
 keys={(x['slot'],x['offset']) for x in region['instructions']};assert all((x['slot'],x['offset']) not in keys for x in probe['instructions'])
 symbols={};pending={};parts=((0xC44A,0xC474),(0xC474,0xC49B))
 for begin,end in parts:
  name='Unknown'+format(begin,'04X');path='Source/Map/'+name+'.asm'
  labels={x['target']:'Point'+format(x['target'],'04X') for x in probe['unresolved'] if x.get('target') is not None and begin<x['target']<end}
  # Поиск прямых локальных целей из фактических декодированных инструкций.
  for x in probe['instructions']:
   target=re.search(r'(?:JP|JR|DJNZ)\s+(?:[A-Z]+,)?#([0-9A-F]+)$',x['operation'])
   if target and begin<int(target[1],16)<end:labels[int(target[1],16)]='Point'+target[1]
  lines=['                module Map','                module '+name,
   '; Документация [таблицы секторов карты](../../Docs/MapSectorTables.md)',
   '; -----------------------------------------','; Unknown, исходный код построения таблиц, контракт оформляется после проверки модели',
   '; In:',';   Unknown, договор общего набора регистров оформляется отдельно',
   '; Out:',';   исходные записи таблиц и обмены EXX сохранены',
   '; Corrupt:',';   Unknown, граница выделения не является полным регистровым договором','; -----------------------------------------']
  for item in probe['instructions']:
   address=item['address']
   if not begin<=address<end:continue
   label='Entry' if address==begin else labels.get(address,'');op=item['operation'].replace(',',', ')
   control=re.fullmatch(r'(CALL|JR|JP|DJNZ)\s+(?:([A-Z]+),\s*)?#([0-9A-F]+)',op)
   if control:
    target=int(control[3],16);target_name=None
    if begin<=target<end:target_name='Map.'+name+'.'+('Entry' if target==begin else labels.get(target,'Point'+format(target,'04X')))
    elif target==0xC474:target_name='Map.UnknownC474.Entry'
    if target_name:op=control[1]+' '+(control[2]+', ' if control[2] else '')+'@'+target_name
   if label:symbols['Map.'+name+'.'+label]=address
   lines.append(((label+':').ljust(16) if label else ' '*16)+op)
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n',None)
  functions.append(dict(region='Map',name=name,address=begin,slot=7,offset=begin-0xC000,end_offset=end-0xC000,
   description='Unknown, договор построения таблиц оформляется после модели',semantic_status='unknown',path=path))
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MapSectorScoped'
 for path,text in pending.items():
  target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,'utf-8')
 old=ROOT/'Source/Resources/07_KARTA/Unclassified001.bin';assert old.read_bytes()==raw[0x44A:0x49B]
 for path in [old,ROOT/'Source/Files/07_KARTA.inc',*[ROOT/('Tools/Disasm/Reports/'+name+'.json') for name in ('Functions','ControlFlow','SourceMap','Symbols','Inventory')]]:
  target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 for path,text in pending.items():path.write_text(text,'utf-8')
 write('Functions',functions);region['instructions']=sorted(region['instructions']+probe['instructions'],key=lambda x:(x['slot'],x['offset']))
 for name in ('roots','calls','branches'):region[name]=sorted(set(region[name])|set(probe[name]))
 addresses={x['address'] for x in region['instructions']}
 region['unresolved'] += [x for x in probe['unresolved'] if x.get('target') not in addresses]
 region['instruction_count']+=probe['instruction_count'];region['code_bytes']+=81;region['classified_fraction']=region['code_bytes']/region['total_bytes'];write('ControlFlow',flow)
 sm=read('SourceMap');index=next(i for i,x in enumerate(sm) if x['path']==old.relative_to(ROOT).as_posix())
 sm[index:index+1]=[dict(slot=7,offset=a-0xC000,length=b-a,kind='code',path='Source/Map/Unknown'+format(a,'04X')+'.asm',origin=a,sha256=hashlib.sha256(raw[a-0xC000:b-0xC000]).hexdigest()) for a,b in parts];write('SourceMap',sm)
 sy=read('Symbols');sy.update(symbols);write('Symbols',sy)
 inv=read('Inventory');inv.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(g['instruction_count'] for g in flow))
 inv['physical_bytes_by_kind']={k:sum(x['length'] for x in sm if x['kind']==k) for k in sorted({x['kind'] for x in sm})};inv['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));write('Inventory',inv)
 path=ROOT/'Source/Files/07_KARTA.inc';text=path.read_text('utf-8');needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/07_KARTA/Unclassified001.bin"';assert needle in text
 replacement='\n'.join('                disp #'+format(a,'04X')+'\n                include "../Map/Unknown'+format(a,'04X')+'.asm"\n                ent\n                assert $ == #'+format(b-0xC000,'04X') for a,b in parts)
 path.write_text(text.replace(needle,replacement,1),'utf-8');verify()
 assert old.resolve().is_relative_to(ROOT/'Source/Resources/07_KARTA') and old.read_bytes()==(history/old.relative_to(ROOT)).read_bytes();old.unlink()
 print('81 original bytes classified, instructions '+str(probe['instruction_count']))


if __name__=='__main__':main()

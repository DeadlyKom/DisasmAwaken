"""Выделение исходной группы косвенных обработчиков по 81 допустимой паре кодов границ."""
from pathlib import Path
import collections,hashlib,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import BLOCKS,block,analyze
from SourcePresentation import format_function
from VerifySources import main as verify


def main():
 verify();history=ROOT/'Tools/Disasm/Research/History/BeforeMapClipHandlersCode';assert not history.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def write(name,value):(ROOT/('Tools/Disasm/Reports/'+name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 raw=(ROOT/(e['path']+'.sectors.bin')).read_bytes();codes=(0,1,2,4,5,6,8,9,10);pairs=[];roots={0xD4DD}
 # Поиск корней только для кодов, реально формируемых классификатором четырёх сторон.
 for first in codes:
  for second in codes:
   index=first*16+second;target=raw[0x1E00+index]|(raw[0x1F00+index]<<8)
   assert 0xD4DD<=target<0xDB63;roots.add(target);pairs.append(dict(first=first,second=second,index=index,target=target,effective_after_inside_first_swap=first!=0 or second==0))
 BLOCKS.append(block(7,0x14DD,0x686,0xD4DD,'MapClipProbe',tuple(sorted(roots))))
 probe=analyze('MapClipProbe');assert probe['code_bytes']==1670 and probe['instruction_count']==685 and not probe['overlaps']
 functions=read('Functions');flow=read('ControlFlow');region=next(g for g in flow if g['name']=='Map')
 keys={(x['slot'],x['offset']) for x in region['instructions']};assert all((x['slot'],x['offset']) not in keys for x in probe['instructions'])
 labels={address:'Point'+format(address,'04X') for address in roots if address!=0xD4DD}
 # Поиск всех прямых внутренних целей без попытки выдать адресное имя за семантический разбор.
 for item in probe['instructions']:
  match=re.fullmatch(r'(?:CALL|JP|JR|DJNZ)\s+(?:[A-Z]+,)?#([0-9A-F]+)',item['operation'])
  if match and 0xD4DD<int(match[1],16)<0xDB63:labels[int(match[1],16)]='Point'+match[1]
 path='Source/Map/UnknownD4DD.asm';symbols={}
 lines=['                module Map','                module UnknownD4DD',
  '; Документация [группа косвенного отсечения](../../Docs/MapClipHandlers.md)',
  '; -----------------------------------------','; Unknown, группа общих хвостов и косвенных обработчиков, алгоритмы каждого входа ещё разбираются',
  '; исходная запись 7, файловые смещения #14DD..#1B62',
  '; In:',';   Unknown, регистровый контракт ещё не доказан',
  '; Out:',';   сохранены все исходные инструкции, точки входа, вызовы и последовательные хвосты',
  '; Corrupt:',';   Unknown, наличие известной таблицы вызовов не доказывает регистровый договор обработчиков',
  '; Note:',';   81 допустимая пара кодов границ дала 71 отдельную цель плюс общий возврат D4DD',
  ';   группа содержит 685 инструкций, её выделение не означает полного смыслового разбора',
  ';   часть входов использует три заранее помещённых возврата D4DD, обычный CALL к ним недопустим',
  '; -----------------------------------------']
 for item in probe['instructions']:
  address=item['address'];label='Entry' if address==0xD4DD else labels.get(address,'');operation=item['operation'].replace(',',', ')
  control=re.fullmatch(r'(CALL|JP|JR|DJNZ)\s+(?:([A-Z]+),\s*)?#([0-9A-F]+)',operation)
  if control:
   target=int(control[3],16);name=None
   if 0xD4DD<=target<0xDB63:name='Map.UnknownD4DD.'+('Entry' if target==0xD4DD else labels[target])
   elif target==0xDB63:name='Map.MultiplySigned16.Entry'
   elif target==0xDCFB:name='Map.DivideSigned32To16.Entry'
   if name:operation=control[1]+' '+(control[2]+', ' if control[2] else '')+'@'+name
  if label:symbols['Map.UnknownD4DD.'+label]=address
  lines.append(((label+':').ljust(16) if label else ' '*16)+operation)
 lines+=['                endmodule','                endmodule'];text=format_function('\n'.join(lines)+'\n',None)
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MapClipHandlersScoped'/path;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_text(text,'utf-8')
 old=ROOT/'Source/Resources/07_KARTA/Unclassified006.bin';assert old.read_bytes()==raw[0x14DD:0x1B63]
 for file in [old,ROOT/'Source/Files/07_KARTA.inc',*[ROOT/('Tools/Disasm/Reports/'+name+'.json') for name in ('Functions','ControlFlow','SourceMap','Symbols','Inventory')]]:
  target=history/file.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target)
 (ROOT/path).write_text(text,'utf-8');functions.append(dict(region='Map',name='UnknownD4DD',address=0xD4DD,slot=7,offset=0x14DD,end_offset=0x1B63,
  description='Unknown, 685 инструкций группы косвенного отсечения, договоры отдельных входов ещё разбираются',semantic_status='unknown',path=path));write('Functions',functions)
 region['instructions']=sorted(region['instructions']+probe['instructions'],key=lambda x:(x['slot'],x['offset']))
 for name in ('roots','calls','branches'):region[name]=sorted(set(region[name])|set(probe[name]))
 addresses={x['address'] for x in region['instructions']}
 region['unresolved'] += [x for x in probe['unresolved'] if x.get('target') not in addresses]
 region['instruction_count']+=685;region['code_bytes']+=1670;region['classified_fraction']=region['code_bytes']/region['total_bytes'];write('ControlFlow',flow)
 sm=read('SourceMap');item=next(x for x in sm if x['path']==old.relative_to(ROOT).as_posix());item.update(kind='code',path=path,origin=0xD4DD);write('SourceMap',sm)
 sy=read('Symbols');sy.update(symbols);write('Symbols',sy)
 inv=read('Inventory');inv.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions),instructions=sum(g['instruction_count'] for g in flow))
 inv['physical_bytes_by_kind']={k:sum(x['length'] for x in sm if x['kind']==k) for k in sorted({x['kind'] for x in sm})};inv['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));write('Inventory',inv)
 file=ROOT/'Source/Files/07_KARTA.inc';content=file.read_text('utf-8');needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/07_KARTA/Unclassified006.bin"';assert needle in content
 content=content.replace(needle,'                ; доказанные корни косвенной таблицы, семантический разбор входов продолжается\n                disp #D4DD\n                include "../Map/UnknownD4DD.asm"\n                ent',1);file.write_text(content,'utf-8');verify()
 assert old.resolve().is_relative_to(ROOT/'Source/Resources/07_KARTA') and old.read_bytes()==(history/old.relative_to(ROOT)).read_bytes();old.unlink()
 write('MapClipDispatch',dict(method='original_split_pointer_table_valid_outcode_pairs_and_direct_control_flow',
  passed=True,pairs=pairs,roots=sorted(roots),valid_outcodes=list(codes),code_bytes=1670,instructions=685,
  original_range_sha256=hashlib.sha256(raw[0x14DD:0x1B63]).hexdigest(),
  full_handler_semantics_proved=False,execution_model_run=False,assembly_executed=False))
 print('685 instructions, 1670 bytes and 72 roots preserved, semantic status remains Unknown')


if __name__=='__main__':main()

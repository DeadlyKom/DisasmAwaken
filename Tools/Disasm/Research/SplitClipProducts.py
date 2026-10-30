"""Однократное выделение четырёх самостоятельных произведений из группы косвенного отсечения."""
from pathlib import Path
import collections,hashlib,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from SourcePresentation import format_function
from VerifySources import main as verify


def main(spec=None):
 spec=spec or dict(history='BeforeClipProductSplit',candidate='ClipProductsScoped',model='ClipProductsVerification',address=0xD4DD,end=0xDB63,
  parts=((0xD4DD,0xD8E2,'UnknownD4DD'),(0xD8E2,0xD901,'UnknownD8E2'),(0xD901,0xD920,'UnknownD901'),
         (0xD920,0xD93F,'UnknownD920'),(0xD93F,0xD95E,'UnknownD93F'),(0xD95E,0xDB63,'UnknownD95E')))
 verify();history=ROOT/'Tools/Disasm/Research/History'/spec['history'];assert not history.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def write(name,value):(ROOT/('Tools/Disasm/Reports/'+name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
 assert read(spec['model'])['passed'];functions=read('Functions');symbols=read('Symbols');flow=read('ControlFlow')
 original=next(f for f in functions if f['region']=='Map' and f['address']==spec['address']);assert original['end_offset']==spec['end']-0xC000
 decoded=[i for g in flow if g['name']=='Map' for i in g['instructions'] if original['offset']<=i['offset']<original['end_offset'] and i['slot']==7]
 code_lines=[line for line in (ROOT/original['path']).read_text('utf-8').splitlines() if line.strip() and not line.lstrip().startswith(';') and not line[16:].strip().lower().startswith(('module ','endmodule'))]
 assert len(decoded)==len(code_lines)
 parts=spec['parts'];assert parts[0][0]==original['address'] and parts[-1][1]==spec['end']
 assert all(left[1]==right[0] for left,right in zip(parts,parts[1:]));old_prefix='Map.'+original['name']+'.'
 # Поиск новых областей имён по прежним доказанным адресам, без изменения инструкций.
 replacements={};new_symbols={}
 for key,value in symbols.items():
  if key.startswith(old_prefix) and spec['address']<=value<spec['end']:
   begin,end,name=next(part for part in parts if part[0]<=value<part[1]);label='Entry' if value==begin else key.rsplit('.',1)[1]
   full='Map.'+name+'.'+label;replacements[key]=full;new_symbols[full]=value
 def rewrite(text):
  lines=[]
  for line in text.splitlines():
   before=line
   for old,new in sorted(replacements.items(),key=lambda item:-len(item[0])):line=line.replace(old,new)
   # Сохранение правой линейки при изменении длины имени цели в машинной инструкции.
   if line!=before and not line.lstrip().startswith(';') and ';' in line:
    operation,comment=line.split(';',1);line=operation.rstrip().ljust(80)+';'+comment
   lines.append(line)
  return '\n'.join(lines)+('\n' if text.endswith('\n') else '')
 pending={};new_functions=[]
 for begin,end,name in parts:
  path='Source/Map/'+name+'.asm';selected=[(item,line) for item,line in zip(decoded,code_lines) if begin<=item['address']<end]
  assert sum(len(bytes.fromhex(item['hex'])) for item,_ in selected)==end-begin
  lines=['                module Map','                module '+name,'; Документация [разбор независимых входов](../../Docs/'+spec.get('document','MapClipHandlers')+'.md)',
   '; -----------------------------------------','; '+spec.get('description','Unknown, фрагмент группы отсечения, независимые договоры оформляются по проверенным входам'),
   '; исходная запись 7, файловые смещения #'+format(begin-0xC000,'04X')+'..#'+format(end-0xC001,'04X'),
   '; In:',';   Unknown, регистровый контракт ещё не доказан',
   '; Out:',';   все исходные инструкции, данные и адреса сохранены',
   '; Corrupt:',';   Unknown, выделение физического фрагмента не считается полным смысловым разбором','; -----------------------------------------']
  for index,(item,line) in enumerate(selected):
   label='Entry' if index==0 else line[:16].strip().removesuffix(':')
   if label:new_symbols['Map.'+name+'.'+label]=item['address']
   lines.append(((label+':').ljust(16) if label else ' '*16)+rewrite(line[16:]))
  lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n',None)
  new_functions.append(dict(region='Map',name=name,address=begin,slot=7,offset=begin-0xC000,end_offset=end-0xC000,
   description=spec.get('description','Unknown, фрагмент группы косвенного отсечения'),semantic_status='unknown',path=path))
 # Сравнение отдельного кандидата с исходным потоком и сохранение только затронутых файлов.
 candidate=ROOT/'Tools/Disasm/Research/Candidates'/spec['candidate']
 for path,text in pending.items():
  target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,'utf-8')
 for path in (ROOT/'Source').rglob('*'):
  if not path.is_file() or path.suffix not in ('.asm','.inc') or path in pending:continue
  text=path.read_text('utf-8');updated=rewrite(text)
  if updated!=text:pending[path]=updated
 affected=[*[path for path in pending if path.exists()],ROOT/'Source/Files/07_KARTA.inc',*[ROOT/('Tools/Disasm/Reports/'+name+'.json') for name in ('Functions','SourceMap','Symbols','Inventory')]]
 for path in set(affected):
  target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 for path,text in pending.items():path.write_text(text,'utf-8')
 position=functions.index(original);functions[position:position+1]=new_functions;write('Functions',functions)
 symbols={key:value for key,value in symbols.items() if not key.startswith(old_prefix)};symbols.update(new_symbols);write('Symbols',symbols)
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7);raw=(ROOT/(e['path']+'.sectors.bin')).read_bytes()
 sm=read('SourceMap');position=next(i for i,x in enumerate(sm) if x['path']==original['path'])
 sm[position:position+1]=[dict(slot=7,offset=begin-0xC000,length=end-begin,kind='code',path='Source/Map/'+name+'.asm',origin=begin,sha256=hashlib.sha256(raw[begin-0xC000:end-0xC000]).hexdigest()) for begin,end,name in parts];write('SourceMap',sm)
 inv=read('Inventory');inv.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']=='unknown' for f in functions))
 inv['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));write('Inventory',inv)
 path=ROOT/'Source/Files/07_KARTA.inc';text=path.read_text('utf-8');needle='                disp #'+format(original['address'],'04X')+'\n                include "../Map/'+original['name']+'.asm"\n                ent';assert needle in text
 replacement='\n'.join('                disp #'+format(begin,'04X')+'\n                include "../Map/'+name+'.asm"\n                ent\n                assert $ == #'+format(end-0xC000,'04X') for begin,end,name in parts)
 path.write_text(text.replace(needle,replacement,1),'utf-8');verify()
 print(str(len(parts))+' physical fragments, '+str(len(decoded))+' original instructions unchanged')


if __name__=='__main__':main()

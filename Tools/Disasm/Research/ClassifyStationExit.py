"""Однократная точечная разметка 81 исходного байта перехода, не часть сборки."""
from pathlib import Path
import collections,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import analyze
from StationExitFacts import FUNCTIONS,CONTRACTS,COMMENTS
from SemanticNames import name_operands,documentation_links
from SourcePresentation import format_function,instructions
from ActionFileKeyTable import render as render_key,PATH as KEY_PATH
from VerifySources import structure_symbols,main as verify


def main():
 # Проверка исходной последовательности и выделяемого физического диапазона до записи.
 verify();flow=analyze('StationExit');assert flow['code_bytes']==72 and flow['instruction_count']==28
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 e=next(e for e in manifest['entries'] if e['slot']==4);source=(ROOT/(e['path']+'.sectors.bin')).read_bytes()
 name,description=FUNCTIONS[0x4200];ins,outs,corrupt,notes=CONTRACTS['StationExit',0x4200]
 lines=['                module StationExit','                module '+name,*documentation_links('StationExit',0x4200),
  '; -----------------------------------------','; '+description,'; исходная запись 4, файловые смещения #216C..#21B3']
 for heading,values in (('In',ins),('Out',outs),('Corrupt',corrupt),('Note',notes)):
  lines+=['; '+heading+':']+[';   '+v for v in values]
 lines+=['; -----------------------------------------'];symbols={};func_path='Source/StationExit/'+name+'.asm'
 for item in flow['instructions']:
  address=item['address'];before,right=COMMENTS.get(address,([],None));lines+=['                ; '+v for v in before]
  label='Entry' if address==0x4200 else 'AfterLoad' if address==0x4236 else ''
  if label:symbols['StationExit.'+name+'.'+label]=address
  op=name_operands('StationExit',0x4200,item['operation'].replace(',',', '))
  line=((label+':').ljust(16) if label else ' '*16)+op
  if right:line=line.ljust(80)+'; '+right
  lines.append(line)
 lines+=['                endmodule','                endmodule'];code=format_function('\n'.join(lines)+'\n',None)
 key,key_symbols=render_key(source);symbols.update(key_symbols)
 candidate=ROOT/'Tools/Disasm/Research/Candidates/StationExitScoped'
 for path,text in ((func_path,code),(KEY_PATH,key)):
  q=candidate/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(text,'utf-8')
 # Проверка кандидата и сохранение только затрагиваемых файлов, без копии всего проекта.
 assert structure_symbols()['FTRDOSFILEKEY']==9 and len(instructions(code))==28
 assert source[0x216C:0x21B4]==b''.join(bytes.fromhex(x['hex']) for x in flow['instructions'])
 paths=[func_path,KEY_PATH,'Source/Files/04_STATIONF.inc','Source/Resources/04_STATIONF/Unclassified042.bin']
 paths+=['Tools/Disasm/Reports/'+v+'.json' for v in ('SourceMap','Functions','ControlFlow','Symbols','Inventory')]
 history=ROOT/'Tools/Disasm/Research/History/BeforeStationExitCode';assert not history.exists()
 for path in paths:
  q=ROOT/path
  if q.exists():
   target=history/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
 for path,text in ((func_path,code),(KEY_PATH,key)):
  q=ROOT/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(text,'utf-8')
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def write(name,value):(ROOT/('Tools/Disasm/Reports/'+name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
 sm=read('SourceMap');index=next(i for i,x in enumerate(sm) if x['slot']==4 and x['offset']==0x216C);assert sm[index]['length']==81
 sm[index:index+1]=[dict(slot=4,offset=a,length=b-a,kind=kind,path=path,origin=origin,sha256=hashlib.sha256(source[a:b]).hexdigest())
  for a,b,kind,path,origin in ((0x216C,0x21B4,'code',func_path,0x4200),(0x21B4,0x21BD,'typed_data',KEY_PATH,0x4248))]
 write('SourceMap',sm)
 f=read('Functions');f.append(dict(region='StationExit',name=name,address=0x4200,slot=4,offset=0x216C,
  description=description,semantic_status='described',end_offset=0x21B4,path=func_path));write('Functions',f)
 cf=read('ControlFlow');cf.append(flow);write('ControlFlow',cf)
 sy=read('Symbols');sy.update(symbols);write('Symbols',sy)
 i=read('Inventory');i.update(fragments=len(f),described=sum(x['semantic_status']=='described' for x in f),
  unknown=sum(x['semantic_status']=='unknown' for x in f),instructions=sum(x['instruction_count'] for x in cf))
 i['physical_bytes_by_kind']={k:sum(x['length'] for x in sm if x['kind']==k) for k in sorted({x['kind'] for x in sm})}
 i['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));write('Inventory',i)
 q=ROOT/'Source/Files/04_STATIONF.inc';s=q.read_text('utf-8')
 old='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/04_STATIONF/Unclassified042.bin"'
 new='                ; исходный переход исполняется после переноса 7EC0 в 4200\n                disp #4200\n                include "../StationExit/LoadAction.asm"\n                ent\n                assert $ == #21B4\n                disp #4248\n                include "../StationExit/Data/ActionFileName.asm"\n                ent'
 assert old in s;q.write_text(s.replace(old,new,1),'utf-8')
 # Проверка всей карты перед удалением бинарного дубликата, исходник сохранён в истории.
 verify();old=(ROOT/'Source/Resources/04_STATIONF/Unclassified042.bin').resolve()
 assert old.is_relative_to(ROOT/'Source/Resources/04_STATIONF') and old.read_bytes()==source[0x216C:0x21BD]
 old.unlink();print('StationExit: 72 code bytes, 28 instructions, 9-byte physical file key')


if __name__=='__main__':main()

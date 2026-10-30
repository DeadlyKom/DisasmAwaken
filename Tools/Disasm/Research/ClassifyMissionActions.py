"""Однократное выделение двух доказанных тел нажатия и предупреждений, без сборки."""
from pathlib import Path
import collections,hashlib,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import BLOCKS,block,analyze
from SourcePresentation import format_function
from MissionMessageTables import render,RANGES
from VerifySources import main as verify


def main():
 verify();history=ROOT/'Tools/Disasm/Research/History/BeforeMissionActionCode';assert not history.exists()
 # Проверка только новых физических диапазонов, остальной подтверждённый поток не пересоздаётся.
 BLOCKS.extend((block(4,0x1148,0xA6,0x6E9C,'StationMissionProbe',(0x6E9C,)),
                block(4,0x1209,0x58,0x6F5D,'StationMissionProbe',(0x6F5D,))))
 probe=analyze('StationMissionProbe');assert probe['code_bytes']==254 and probe['instruction_count']==111
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def write(name,value):(ROOT/('Tools/Disasm/Reports/'+name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(x for x in manifest['entries'] if x['slot']==4)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();functions=read('Functions');flow=read('ControlFlow');station=next(x for x in flow if x['name']=='Station')
 old_keys={(x['slot'],x['offset']) for x in station['instructions']}
 assert all((x['slot'],x['offset']) not in old_keys for x in probe['instructions'])
 parts=((0x6E9C,0x6F42,0x1148,'Unknown6E9C'),(0x6F5D,0x6FB5,0x1209,'Unknown6F5D'))
 names={x['address']:'Station.'+x['name']+'.Entry' for x in functions if x['region']=='Station'}
 names.update({a:'Station.'+name+'.Entry' for a,_,_,name in parts});labels={}
 for target in probe['branches']:
  for begin,end,_,name in parts:
   if begin<=target<end:
    labels[target]='Entry' if target==begin else 'Point'+format(target,'04X');names[target]='Station.'+name+'.'+labels[target]
 messages,message_symbols=render(source);pending={ROOT/path:text for path,text in messages.items()};symbols=dict(message_symbols)
 for begin,end,offset,name in parts:
  lines=['                module Station','                module '+name,
   '; Документация [Station](../../Docs/FunctionDetails/Station.md)',
   '; Граница разбора [действия миссии](../../Docs/MissionAction.md)',
   '; -----------------------------------------','; Unknown, полный алгоритм и регистровый контракт тела нажатия ещё разбираются',
   '; исходная запись 4, файловые смещения #'+format(offset,'04X')+'..#'+format(offset+end-begin-1,'04X'),
   '; In:',';   Unknown, регистровый контракт ещё не доказан','; Out:',
   ';   сохранён исходный поток управления, включая общий хвост и банковый вызов',
   '; Corrupt:',';   Unknown, требуется завершить разбор собственных расчётов и вызываемых рисователей',
   '; Note:',';   самостоятельный вход доказан исходным Handler+3 либо переходом из этого тела',
   ';   промежуточное выделение кода не считается доказательством завершённости алгоритма','; -----------------------------------------']
  selected=[x for x in probe['instructions'] if begin<=x['address']<end]
  assert b''.join(bytes.fromhex(x['hex']) for x in selected)==source[offset:offset+end-begin]
  for item in selected:
   address=item['address'];label='Entry' if address==begin else labels.get(address,'');operation=item['operation'].replace(',',', ')
   control=re.fullmatch(r'(CALL|JP|JR)\s+(?:([A-Z]+),\s*)?#([0-9A-F]+)',operation)
   if control:
    target=int(control[3],16);target_name='Text.RunMarketScript.Entry' if address==0x6F7D else names.get(target)
    if target_name:operation=control[1]+' '+(control[2]+', ' if control[2] else '')+'@'+target_name
   operation=operation.replace('LD HL, #6F42','LD HL, @MissionTonnageMessage.Entry').replace('LD HL, #6FB5','LD HL, @MissionCancelMessage.Entry')
   if label:symbols['Station.'+name+'.'+label]=address
   lines.append(((label+':').ljust(16) if label else ' '*16)+operation)
  lines+=['                endmodule','                endmodule'];path='Source/Station/'+name+'.asm'
  pending[ROOT/path]=format_function('\n'.join(lines)+'\n',None)
  functions.append(dict(region='Station',name=name,address=begin,slot=4,offset=offset,
   description='Unknown, полный алгоритм тела нажатия миссии ещё разбирается',semantic_status='unknown',end_offset=offset+end-begin,path=path))
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MissionActionScoped'
 for path,text in pending.items():
  target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,'utf-8')
 old_paths=[ROOT/'Source/Resources/04_STATIONF'/('Unclassified'+n+'.bin') for n in ('025','026')]
 affected=[ROOT/'Source/Files/04_STATIONF.inc',*old_paths,*[ROOT/('Tools/Disasm/Reports/'+name+'.json') for name in ('Functions','ControlFlow','SourceMap','Symbols','Inventory')]]
 for path in affected:
  target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 for path,text in pending.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,'utf-8')
 write('Functions',functions)
 station['instructions']=sorted(station['instructions']+probe['instructions'],key=lambda x:(x['slot'],x['offset']))
 station['roots']=sorted(set(station['roots'])|{0x6E9C,0x6F5D});station['calls']=sorted(set(station['calls'])|set(probe['calls']));station['branches']=sorted(set(station['branches'])|set(probe['branches']))
 addresses={x['address'] for x in station['instructions']}
 for item in probe['unresolved']:
  if item['address']==0x6F7D:item.update(bank=6,reason='банковый вход LANG по доказанному LD A,16 и SelectRamBank')
  if item.get('target') not in addresses or item.get('bank',0)!=0:station['unresolved'].append(item)
 station['instruction_count']+=111;station['code_bytes']+=254;station['classified_fraction']=station['code_bytes']/station['total_bytes'];write('ControlFlow',flow)
 sm=read('SourceMap')
 for old,(begin,end,offset,name),(text_begin,text_end,text_path,_) in zip(old_paths,parts,RANGES):
  index=next(i for i,x in enumerate(sm) if x['path']==old.relative_to(ROOT).as_posix())
  assert old.read_bytes()==source[offset:text_end]
  code_end=offset+end-begin
  sm[index:index+1]=[dict(slot=4,offset=a,length=b-a,kind=kind,path=path,origin=origin,sha256=hashlib.sha256(source[a:b]).hexdigest())
   for a,b,kind,path,origin in ((offset,code_end,'code','Source/Station/'+name+'.asm',begin),(text_begin,text_end,'typed_data',text_path,text_begin+0x5D54))]
 write('SourceMap',sm);sy=read('Symbols');sy.update(symbols);write('Symbols',sy)
 inventory=read('Inventory');inventory.update(fragments=len(functions),described=sum(x['semantic_status']=='described' for x in functions),
  unknown=sum(x['semantic_status']=='unknown' for x in functions),instructions=sum(x['instruction_count'] for x in flow))
 inventory['physical_bytes_by_kind']={k:sum(x['length'] for x in sm if x['kind']==k) for k in sorted({x['kind'] for x in sm})};inventory['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));write('Inventory',inventory)
 path=ROOT/'Source/Files/04_STATIONF.inc';text=path.read_text('utf-8')
 for number,(begin,end,offset,name),(text_begin,_,text_path,_) in zip(('025','026'),parts,RANGES):
  old='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/04_STATIONF/Unclassified'+number+'.bin"'
  new='                ; исходное тело нажатия миссии, семантический разбор продолжается\n                disp #'+format(begin,'04X')+'\n                include "../Station/'+name+'.asm"\n                ent\n                assert $ == #'+format(text_begin,'04X')+'\n                disp #'+format(text_begin+0x5D54,'04X')+'\n                include "../Station/Data/'+Path(text_path).name+'"\n                ent'
  assert old in text;text=text.replace(old,new,1)
 path.write_text(text,'utf-8');verify()
 for old in old_paths:
  assert old.resolve().is_relative_to(ROOT/'Source/Resources/04_STATIONF') and old.read_bytes()==(history/old.relative_to(ROOT)).read_bytes()
  old.unlink()
 print('111 original instructions, 254 code bytes and 27 message bytes classified, contracts remain Unknown')


if __name__=='__main__':main()

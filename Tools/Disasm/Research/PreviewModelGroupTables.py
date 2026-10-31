"""Физические заголовки и группы десяти исходных моделей, без переписывания данных граней."""
import re
from PreviewModelGroups import records
from PreviewSceneTables import MODEL_NAMES
STRUCTURES=(
 ('FPreviewModelHeader',(('Size',1,'исходный размер модели, первый байт заголовка'),('ScaleFlags',1,'биты 6..0 показатель масштаба, бит 7 отдельный признак второго ключа'))),
 ('FPreviewVertexGroup',(('Mask',1,'маска комбинаций вершин 7..0, нуль является однобайтовым концом списка'),('ParamFirst',1,'первый байтовый параметр группы, вход B поставщика'),('ParamSecond',1,'второй байтовый параметр группы, вход C поставщика'),('ParamThird',1,'третий байтовый параметр группы, вход D поставщика'))))


def tables(source):
 unique={}
 for index,name in enumerate(MODEL_NAMES):
  model=records(source,4*index);pointer=model['pointer']
  if pointer not in unique:unique[pointer]=dict(model,name=name,module='PreviewModel'+name,path='Source/D3D/Data/ModelGroups/'+name+'.asm',start=pointer-0xC000,end=model['terminator']-0xC000+1)
 return tuple(unique[pointer] for pointer in sorted(unique))


def parse(text,model):
 clean='\n'.join(line.split(';',1)[0] for line in text.splitlines());raw=bytearray();symbols={};pointer=model['pointer'];module=model['module']
 header=re.findall(r'Header:\s+FPreviewModelHeader\s*\{([^}]+)\}',clean);assert len(header)==1
 values=[int(v.strip().replace('#','0x'),0) for v in header[0].split(',')];assert len(values)==2;raw.extend(values);symbols[module+'.Header']=pointer
 for offset,(field,width,meaning) in enumerate(STRUCTURES[0][1]):symbols[module+'.Header.'+field]=pointer+offset
 groups=re.findall(r'(Group\d+):\s+FPreviewVertexGroup\s*\{([^}]+)\}',clean);assert len(groups)==len(model['groups'])
 for index,(name,arguments) in enumerate(groups):
  assert name=='Group'+str(index).zfill(2);values=[int(v.strip().replace('#','0x'),0) for v in arguments.split(',')];assert len(values)==4 and values[0]!=0
  address=pointer+len(raw);symbols[module+'.'+name]=address
  for offset,(field,width,meaning) in enumerate(STRUCTURES[1][1]):symbols[module+'.'+name+'.'+field]=address+offset
  raw.extend(values)
 assert re.findall(r'EndGroups:\s+DB\s+#([0-9A-Fa-f]+)',clean)==['00'];symbols[module+'.EndGroups']=pointer+len(raw);raw.append(0)
 assert len(raw)==model['end']-model['start']
 return bytes(raw),symbols


def render(source,model):
 lines=['                module '+model['module'],'                ; Документация [физические группы модели](../../../../Docs/PreviewModelGroups.md)','                assert $ == #'+format(model['pointer'],'04X'),'                ; размер и показатель сохранены из фактического заголовка','Header:         FPreviewModelHeader {']
 for index,((field,width,meaning),value) in enumerate(zip(STRUCTURES[0][1],(model['size'],model['scale_flags']))):lines.append(('                    #'+format(value,'02X')+(',' if index==0 else '')).ljust(80)+'; '+field+', '+meaning)
 lines.append('                }')
 for index,(address,values) in enumerate(model['groups']):
  lines+=['                ; -----------------------------------------','                ; группа '+str(index)+', исходный адрес #'+format(address,'04X'),('Group'+str(index).zfill(2)+':').ljust(16)+'FPreviewVertexGroup {']
  for field_index,((field,width,meaning),value) in enumerate(zip(STRUCTURES[1][1],values)):lines.append(('                    #'+format(value,'02X')+(',' if field_index<3 else '')).ljust(80)+'; '+field+', '+meaning)
  lines.append('                }')
 lines+=['                ; однобайтовый конец масок, следующие байты относятся к дальнейшим данным модели','EndGroups:      DB #00','                assert $ == #'+format(model['terminator']+1,'04X'),'                endmodule'];text='\n'.join(lines)+'\n';raw,symbols=parse(text,model);assert raw==source[model['start']:model['end']]
 return text,symbols

"""Физические исходные параметры, девять слов матрицы и пары указателей моделей."""
import re
SEED_FIELDS=tuple(('Unknown'+str(i).zfill(2),1,'исходный байт начального копирования, отдельный игровой смысл ещё не установлен') for i in range(3))
MATRIX_FIELDS=tuple(('Coeff'+str(row)+str(column),2,'исходный коэффициент строки '+str(row)+' при координате '+str(column)+', проход использует старший байт') for column in range(1,4) for row in range(1,4))
POINTER_FIELDS=(('BasePointer',2,'указатель модели при старшем байте третьего результата 31..127'),('AlternatePtr',2,'соседний указатель модели при старшем байте третьего результата 0..30'))
MODEL_NAMES=('Dominion','Sofist','Memfis','Firs','Orsan','Baros','Karen','Fervest','Kridon','Protos','Algol')
TABLES=(
 ('PreviewSharedSeed','Source/D3D/Data/PreviewSharedSeed.asm',0x200,0x203,'FPreviewSharedSeed',SEED_FIELDS,('Value',)),
 ('PreviewSceneMatrix','Source/D3D/Data/PreviewSceneMatrix.asm',0x20C,0x21E,'FPreviewSceneMatrix',MATRIX_FIELDS,('Value',)),
 ('PreviewModelPointers','Source/D3D/Data/PreviewModelPointers.asm',0x1000,0x102C,'FPreviewModelPointers',POINTER_FIELDS,MODEL_NAMES))


def parse(text,table):
 module,path,start,end,structure,fields,names=table
 clean='\n'.join(line.split(';',1)[0] for line in text.splitlines())
 records=re.findall(r'(\w+):\s+'+structure+r'\s*\{([^}]+)\}',clean);raw=bytearray();symbols={};size=sum(width for _,width,_ in fields)
 if len(records)!=len(names):raise ValueError('Изменилось число записей '+module)
 for index,((label,arguments),expected_label) in enumerate(zip(records,names)):
  if label!=expected_label:raise ValueError('Изменился порядок записей '+module)
  values=[int(v.strip().replace('#','0x'),0) for v in arguments.split(',')]
  if len(values)!=len(fields):raise ValueError('Изменилось число полей '+structure)
  address=0xC000+start+size*index;symbols[module+'.'+label]=address;offset=0
  for (field,width,_),value in zip(fields,values):
   raw.extend(value.to_bytes(width,'little'));symbols[module+'.'+label+'.'+field]=address+offset;offset+=width
 if len(raw)!=end-start:raise ValueError('Изменился размер '+module)
 return bytes(raw),symbols


def render(source,table):
 module,path,start,end,structure,fields,names=table;size=sum(width for _,width,_ in fields)
 lines=['                module '+module,'                ; Документация [подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','                assert $ == #'+format(0xC000+start,'04X')]
 for index,label in enumerate(names):
  blob=source[start+index*size:start+(index+1)*size];offset=0;lines+=['                ; -----------------------------------------','                ; исходная физическая запись '+label,(label+':').ljust(16)+structure+' {']
  for j,(field,width,meaning) in enumerate(fields):
   value=int.from_bytes(blob[offset:offset+width],'little');offset+=width
   line=' '*16+'    #'+format(value,'02X' if width==1 else '04X')+(',' if j+1<len(fields) else '')
   lines.append(line.ljust(80)+'; '+field+', '+meaning)
  lines.append('                }')
 lines+=['                assert $ == #'+format(0xC000+end,'04X'),'                endmodule'];text='\n'.join(lines)+'\n';raw,labels=parse(text,table);assert raw==source[start:end]
 return text,labels

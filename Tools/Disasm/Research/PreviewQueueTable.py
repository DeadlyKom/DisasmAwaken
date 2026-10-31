"""Физические четырнадцатибайтовые узлы исходной очереди D3D."""
import re,struct
PATH='Source/D3D/Data/PreviewQueue.asm'
START=0x700
END=0x7FC
FIELDS=(('Next',1,'младший индекс следующей записи, 1 завершает активную цепочку'),
 ('Flags',1,'бит 7 выбирает второй ключ сравнения, прочие разряды сохраняются'),
 ('ModelOffset',1,'рабочее байтовое смещение указателя модели'),
 ('AngleFirst',1,'первый исходный байтовый параметр ориентации'),
 ('AngleSecond',1,'второй исходный байтовый параметр ориентации'),
 ('AngleThird',1,'третий исходный байтовый параметр ориентации'),
 ('FirstResult',2,'результат первой строки преобразования'),
 ('SecondResult',2,'результат второй строки преобразования'),
 ('ThirdResult',2,'результат третьей строки, первый ключ сравнения'),
 ('SecondInput',2,'вторая исходная координата, второй ключ сравнения'))
FORMAT='<6B4H'


def parse(text):
 clean='\n'.join(line.split(';',1)[0] for line in text.splitlines())
 records=re.findall(r'(Node[0-9]{2}):\s+FPreviewQueueNode\s*\{([^}]+)\}',clean)
 raw=bytearray();symbols={}
 if len(records)!=18:raise ValueError('Изменилось число исходных узлов очереди D3D')
 for i,(label,arguments) in enumerate(records):
  if label!='Node'+str(i).zfill(2):raise ValueError('Изменился порядок физических узлов')
  values=[int(v.strip().replace('#','0x'),0) for v in arguments.split(',')]
  if len(values)!=len(FIELDS):raise ValueError('Изменилось число полей узла')
  raw.extend(struct.pack(FORMAT,*values));address=0xC000+START+14*i;symbols['PreviewQueue.'+label]=address;offset=0
  for field,width,_ in FIELDS:symbols['PreviewQueue.'+label+'.'+field]=address+offset;offset+=width
 return bytes(raw),symbols


def render(source):
 raw=source[START:END];assert len(raw)==18*14
 lines=['                module PreviewQueue','                ; Документация [двухключевая очередь объектов](../../../Docs/PreviewQueue.md)',
 '                ; это исходные невыделенные узлы, нули не заменяются маркером конца активного списка',
 '                assert $ == #C700']
 for i in range(18):
  values=struct.unpack(FORMAT,raw[14*i:14*i+14]);label='Node'+str(i).zfill(2)
  lines+=['                ; -----------------------------------------','                ; физический узел '+str(i)+', младший индекс #'+format(14*i,'02X'),(label+':').ljust(16)+'FPreviewQueueNode {']
  for j,((field,width,meaning),value) in enumerate(zip(FIELDS,values)):
   line=' '*16+'    #'+format(value,'02X' if width==1 else '04X')+(',' if j+1<len(values) else '')
   lines.append(line.ljust(80)+'; '+field+', '+meaning)
  lines.append('                }')
 lines+=['                assert $ == #C7FC','                endmodule'];text='\n'.join(lines)+'\n';actual,symbols=parse(text);assert actual==raw
 return text,symbols

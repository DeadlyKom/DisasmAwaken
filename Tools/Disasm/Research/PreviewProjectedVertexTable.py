"""Исходные 256 байтов рабочего буфера, 51 физическая запись и отдельный хвост страницы."""
import re
from PreviewSceneTables import parse as parse_records,render as render_records
PATH='Source/D3D/Data/PreviewProjectedVertices.asm'
FIELDS=(('SecondAxis',2,'слово второй координаты с центром HalfY'),('FirstAxis',2,'слово первой координаты с центром HalfX'),('Outcode',1,'код сторон, младшая тетрада прямая, старшая инверсная'))
TABLE=('PreviewProjectedVertices',PATH,0x600,0x6FF,'FPreviewProjectedVertex',FIELDS,tuple('Vertex'+str(i).zfill(2) for i in range(51)))


def parse(text):
 raw,labels=parse_records(text,TABLE);clean='\n'.join(line.split(';',1)[0] for line in text.splitlines());tail=re.findall(r'TailByte:\s+DB\s+#([0-9A-Fa-f]{2})',clean);assert len(tail)==1
 labels['PreviewProjectedVertices.TailByte']=0xC6FF
 return raw+bytes((int(tail[0],16),)),labels


def render(source):
 text,labels=render_records(source,TABLE);text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[записи проекции и код сторон](../../../Docs/PreviewVertexClass.md)')
 needle='                assert $ == #C6FF\n';assert needle in text
 text=text.replace(needle,needle+'                ; последний байт страницы вне 51 полной записи, сохраняется и доступен модульному обходу\nTailByte:       DB #'+format(source[0x6FF],'02X')+'\n                assert $ == #C700\n')
 raw,labels=parse(text);assert raw==source[0x600:0x700]
 return text,labels

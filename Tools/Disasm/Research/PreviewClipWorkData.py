"""Два физических конца и состояние углов, структуры существующих форматов переиспользуются."""
from PreviewSceneTables import parse,render as render_records
POINT_FIELDS=(('SecondAxis',2,'знаковая колонка, первое физическое слово точки'),('FirstAxis',2,'знаковая строка, второе физическое слово точки'),('Outcode',1,'прямая младшая и инверсная старшая тетрада кода сторон'))
TABLES=(
 ('PreviewClipFirst','Source/D3D/Data/PreviewClipFirst.asm',0x22C,0x231,'FPreviewProjectedVertex',POINT_FIELDS,('Value',)),
 ('PreviewClipSecond','Source/D3D/Data/PreviewClipSecond.asm',0x23C,0x241,'FPreviewProjectedVertex',POINT_FIELDS,('Value',)),
 ('PreviewClipCorners','Source/D3D/Data/PreviewClipCorners.asm',0x24F,0x251,'FClipCornerState',
  (('SeenFlags',1,'младшие четыре разряда отметок углов, верхние не именуются без полного набора писателей'),('BlockCode',1,'целый байт запрета добавления углов, нуль разрешает, любой ненуль подавляет')),('Value',)))


def render(source,table):
 text,labels=render_records(source,table)
 return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[концы и состояние отсечения](../../../Docs/PreviewClipSegment.md)'),labels

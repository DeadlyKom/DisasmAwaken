"""Длина контура, индекс заливки и восемь физических пар внутренних шаблонов."""
from PreviewSceneTables import parse,render as render_records
TABLES=(
 ('PreviewContourSize','Source/D3D/Data/PreviewContourSize.asm',0x22B,0x22C,'FPreviewContourSize',
  (('ByteCount',1,'число байтов пар колонка и строка, рабочий профиль ненулевое чётное значение'),),('Value',)),
 ('PreviewFillMode','Source/D3D/Data/PreviewFillMode.asm',0x23B,0x23C,'FPreviewFillMode',
  (('Index',1,'индекс пары внутренних шаблонов, крайние маски доказаны только для 0..4'),),('Value',)),
 ('PreviewFillPatterns','Source/D3D/Data/PreviewFillPatterns.asm',0x1100,0x1110,'FPreviewFillPattern',
  (('Pattern',1,'первый шаблон внутренних байтов многоугольника'),('RowXor',1,'XOR шаблона при переходе к следующей строке контура')),tuple('Mode'+str(i) for i in range(8))))


def render(source,table):
 text,labels=render_records(source,table)
 return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[контур и шаблоны заливки](../../../Docs/PreviewPolygonFill.md)'),labels

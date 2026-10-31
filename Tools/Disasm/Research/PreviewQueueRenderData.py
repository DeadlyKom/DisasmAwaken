"""Три байта ориентации, передаваемые узлом очереди матрице подготавливаемого объекта."""
from PreviewSceneTables import parse,render as render_records
TABLES=(('PreviewObjectAngles','Source/D3D/Data/PreviewObjectAngles.asm',0x21E,0x221,'FPreviewObjectAngles',
 (('First',1,'первый байтовый параметр ориентации объекта'),('Second',1,'второй байтовый параметр ориентации объекта'),('Third',1,'третий байтовый параметр ориентации объекта')),('Value',)),)


def render(source,table):
 text,labels=render_records(source,table)
 return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[параметры обхода очереди](../../../Docs/PreviewQueueRender.md)'),labels

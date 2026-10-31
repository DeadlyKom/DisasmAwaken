"""Три параметра первой исходной объектной записи, общая структура ориентации переиспользуется."""
from PreviewSceneTables import parse,render as render_records
TABLES=(('PreviewPrimaryAngles','Source/D3D/Data/PreviewPrimaryAngles.asm',0xDC7,0xDCA,'FPreviewObjectAngles',
 (('First',1,'первый байтовый параметр ориентации первой объектной записи'),('Second',1,'второй байтовый параметр ориентации первой объектной записи'),('Third',1,'третий байтовый параметр ориентации первой объектной записи')),('Value',)),)


def render(source,table):
 text,labels=render_records(source,table)
 return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[изменение ориентации перед кадром](../../../Docs/PreviewFrame.md)'),labels

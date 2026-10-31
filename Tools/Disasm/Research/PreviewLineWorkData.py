"""Десять разнесённых физических байтов текущего и предыдущего конца полилинии."""
from PreviewSceneTables import parse,render as render_records
TABLES=(
 ('PreviewLineCoordinates','Source/D3D/Data/PreviewLineCoordinates.asm',0x25B,0x261,'FPreviewLineCoordinates',
  (('PreviousColumn',2,'слово колонки предыдущего конца полилинии'),('PreviousRow',2,'слово строки предыдущего конца полилинии'),('CurrentColumn',2,'слово колонки очередного конца полилинии')),('Value',)),
 ('PreviewLineTail','Source/D3D/Data/PreviewLineTail.asm',0x26B,0x26F,'FPreviewLineTail',
  (('CurrentRow',2,'слово строки очередного конца полилинии'),('PreviousCode',1,'полный код сторон предыдущего конца'),('CurrentCode',1,'полный код сторон очередного конца')),('Value',)))


def render(source,table):
 text,labels=render_records(source,table)
 return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[разнесённое состояние полилинии](../../../Docs/PreviewClippedFaceStream.md)'),labels

"""Один физический код предыдущей ориентации, не набор независимых флагов."""
from PreviewSceneTables import parse,render as render_records
TABLES=(('PreviewFaceGateState','Source/D3D/Data/PreviewFaceGateState.asm',0x27B,0x27C,'FPreviewFaceGateState',(('RejectCode',1,'нуль после принятой ориентации, один после отвергнутой, читатель проверяет весь байт'),),('Value',)),)


def render(source,table):
 text,labels=render_records(source,table)
 return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[код предыдущей ориентации](../../../Docs/PreviewFaceStream.md)'),labels

"""Реальные слова четырёх кэшей, разрыв левого произведения не заполняется фиктивными полями."""
from PreviewSceneTables import parse,render as render_records
FIELDS=(('LowWord',2,'младшее слово исходного результата умножения'),('HighWord',2,'старшее слово того же 32-битного результата'))
WORD=(('Word',2,'физическое слово разнесённого левого кэша, смысл младшего либо старшего задаётся именем экземпляра'),)
TABLES=(
 ('PreviewClipTopProduct','Source/D3D/Data/PreviewClipTopProduct.asm',0x2DC,0x2E0,'FClipProduct',FIELDS,('Value',)),
 ('PreviewClipBottomProduct','Source/D3D/Data/PreviewClipBottomProduct.asm',0x2EA,0x2EE,'FClipProduct',FIELDS,('Value',)),
 ('PreviewClipLeftLow','Source/D3D/Data/PreviewClipLeftLow.asm',0x2EE,0x2F0,'FPreviewClipProductWord',WORD,('Value',)),
 ('PreviewClipLeftHigh','Source/D3D/Data/PreviewClipLeftHigh.asm',0x2FA,0x2FC,'FPreviewClipProductWord',WORD,('Value',)),
 ('PreviewClipRightProduct','Source/D3D/Data/PreviewClipRightProduct.asm',0x2FC,0x300,'FClipProduct',FIELDS,('Value',)))


def render(source,table):
 text,labels=render_records(source,table)
 return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[кэши произведений и разности](../../../Docs/PreviewClipProducts.md)'),labels

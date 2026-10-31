"""Физические параметры рёбер и две исходные маски пикселя банка 4."""
from PreviewSceneTables import parse,render as render_records
from MarketScriptTable import parse as parse_bytes
TABLES=(
 ('PreviewEdgeEndpoints','Source/D3D/Data/PreviewEdgeEndpoints.asm',0x24B,0x24F,'FPreviewEdgeEndpoints',
  (('StartPoint',2,'начальное слово, младший байт колонка, старший строка'),('EndPoint',2,'конечное слово в том же формате')),('Value',)),
 ('PreviewEdgeMode','Source/D3D/Data/PreviewEdgeMode.asm',0x26F,0x271,'FPreviewEdgeMode',
  (('PixelOpcode',1,'байт пиксельной инструкции A1 для AND, A9 для XOR, B1 для OR'),('BoundaryOpcode',1,'байт перехода 30 для JR NC при AND, 38 для JR C при XOR и OR')),('Value',)))
MASK_PATH='Source/D3D/Data/PreviewPixelMasks.asm'


def render(source,table):
 text,labels=render_records(source,table)
 return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[физические параметры ребра](../../../Docs/PreviewEdgeRaster.md)'),labels


def render_masks(source):
 raw=source[0xDB0:0xDC0];assert raw==bytes([128>>i for i in range(8)]+[255^(128>>i) for i in range(8)])
 lines=['                module PreviewPixelMasks','                ; Документация [маски пикселя и режимы ребра](../../../Docs/PreviewEdgeRaster.md)','                assert $ == #CDB0','                ; каждый байт выбирает один экранный бит, слева направо разряды 7..0',
 'SetBit:         DB '+', '.join('#'+format(v,'02X') for v in raw[:8]),
 '                ; каждый байт сохраняет остальные семь битов при AND',
 'ClearBit:       DB '+', '.join('#'+format(v,'02X') for v in raw[8:]),
 '                assert $ == #CDC0','                endmodule']
 text='\n'.join(lines)+'\n';actual,labels=parse_bytes(text,0xCDB0);assert actual==raw
 return text,labels

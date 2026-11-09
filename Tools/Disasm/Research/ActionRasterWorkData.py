"""Физические упакованные точки и два полных байта выбора ядер линии."""
from PreviewSceneTables import render as render_records,parse as parse_records

TABLES=(
    ('ActionRasterPoints','Source/Action/Data/RasterPoints.asm',0x2D2A,0x2D2E,'FLineRasterPoint',
     (('Second',1,'горизонтальная пиксельная координата, младший байт упакованного слова'),
      ('First',1,'вертикальная пиксельная координата, старший байт упакованного слова')),('FirstPoint','SecondPoint')),
    ('ActionRasterMode','Source/Action/Data/RasterMode.asm',0x2D4E,0x2D50,'FLineRasterMode',
     (('PixelOpcode',1,'полный байт A1 для AND, B1 для OR либо A9 для XOR'),
      ('BranchOpcode',1,'полный байт 30 для JR NC либо 38 для JR C')),('Value',)),
)


def render(source,table):
    text,labels=render_records(source,table,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физическое состояние линии](../../../Docs/ActionRasterWorkData.md)'),labels


def parse(text,table):return parse_records(text,table,0x6000)


def structures():
    return '''
                ; Упакованная пиксельная точка линии, порядок отличается от FBufferPoint
                struct FLineRasterPoint
Second          db #00                                                          ; горизонтальная пиксельная координата, младший байт слова
First           db #00                                                          ; вертикальная пиксельная координата, старший байт слова
                ends
                assert FLineRasterPoint == 2
                assert FLineRasterPoint.Second == 0
                assert FLineRasterPoint.First == 1

                ; Полные коды команд для выбранного режима линии, не независимые флаги
                struct FLineRasterMode
PixelOpcode     db #00                                                          ; A1 для AND C, B1 для OR C либо A9 для XOR C
BranchOpcode    db #00                                                          ; 30 для JR NC либо 38 для JR C
                ends
                assert FLineRasterMode == 2
                assert FLineRasterMode.PixelOpcode == 0
                assert FLineRasterMode.BranchOpcode == 1
'''

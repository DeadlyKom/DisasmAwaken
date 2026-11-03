"""Исходные указатели, одиночные маски, очистка и двенадцать форм объектного прохода."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records
from ControlsThreeRowGlyphs import FIELDS as GLYPH_FIELDS

SHAPES = ('BarI','BottomT','OpenRight','Solid','LowerLeft','HorzBars',
          'RightBar','Hollow','VerticalBars','Slash','Cross','Plus')
POINTER_FIELDS = (('Target',2,'адрес восьми фаз формы, игровое имя типа ещё не установлено'),)
PIXEL_FIELDS = (('Mask',1,'одиночный бит X внутри экранного байта'),)
CLEAR_FIELDS = (('LeftMask',1,'сохраняемые биты левой части строки'),
                ('RightMask',1,'сохраняемые биты правой части строки')) + tuple(
    ('Unknown'+format(i,'02d'),1,'исходный нулевой байт, этот потребитель его не читает') for i in range(2,6))
TABLES = (
    ('ControlsObjectGlyphPointers','Source/Controls/Data/ObjectGlyphPointers.asm',0xB7F,0xBA7,
     'FObjectGlyphPointer',POINTER_FIELDS,tuple('Kind'+format(i,'02X') for i in range(20))),
    ('ControlsObjectPixelMasks','Source/Controls/Data/ObjectPixelMasks.asm',0xBA7,0xBAF,
     'FObjectPixelMask',PIXEL_FIELDS,tuple('Phase'+format(i,'02X') for i in range(8))),
    ('ControlsObjectClearMasks','Source/Controls/Data/ObjectClearMasks.asm',0xBAF,0xBDF,
     'FObjectGlyphClearPhase',CLEAR_FIELDS,tuple('Phase'+format(i,'02X') for i in range(8))),
    ('ControlsObjectGlyphs','Source/Controls/Data/ObjectGlyphs.asm',0xBDF,0xE1F,
     'FThreeRowGlyphPhase',GLYPH_FIELDS,tuple(name+format(i,'02X') for name in SHAPES for i in range(8))))


def render(source, table):
    text, symbols = render_records(source,table,0xDADE)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[координаты и значки объектов](../../../Docs/ControlsObjectProjection.md)'), symbols


def parse(text,table):
    module,path,start,end,structure,fields,names=table
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module '+module and clean.pop(0)=='assert $ == #'+format(0xDADE+start,'04X')
    for name in names:
        assert clean.pop(0)==(name+':').ljust(16)+structure+' {'
        for index,(_,width,_) in enumerate(fields):
            assert re.fullmatch(r'#[0-9A-F]{'+str(width*2)+'}'+(',' if index+1<len(fields) else ''),clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #'+format(0xDADE+end,'04X'),'endmodule']
    return parse_records(text,table,0xDADE)

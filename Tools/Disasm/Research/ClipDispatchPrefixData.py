"""Шесть младших частей действительных адресов и две рабочие ячейки префикса CF00."""
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=(('AppendPointLow',1,'младший байт адреса AppendSecondClipPoint.Entry'),
        ('ToRightLow',1,'младший байт адреса ClipInsideToRight.Entry'),
        ('ToLeftLow',1,'младший байт адреса ClipInsideToLeft.Entry'),
        ('CornerBlock',1,'нулевой байт разрешает запись углов, любой ненулевой запрещает'),
        ('ToBottomLow',1,'младший байт адреса ClipInsideToBottom.Entry'),
        ('ToBottomRLow',1,'младший байт адреса ClipInsideToBottomRight.Entry'),
        ('ToBottomLLow',1,'младший байт адреса ClipInsideToBottomLeft.Entry'),
        ('SeenFlags',1,'отметки TL, TR, BL, BR в битах 3..0, обработчики углов сохраняют 7..4'))
TABLES=((17,0x6000,('ActionClipDispatchPrefix','Source/Action/Data/ClipDispatchPrefix.asm',0x6F00,0x6F08,'FClipDispatchPrefix',FIELDS,('Value',))),
        (19,0xC000,('ThreeDClipDispatchPrefix','Source/ThreeD/Data/ClipDispatchPrefix.asm',0xF00,0xF08,'FClipDispatchPrefix',FIELDS,('Value',))))


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[адресные байты и рабочие ячейки CF00](../../../Docs/ClipDispatchPrefixData.md)'),labels


def parse(text,origin,table):return parse_records(text,table,origin)


def structure():
    result=['                ; Префикс разделённой таблицы CF00/D000, индексы 03 и 07 используются как состояние',
            '                struct FClipDispatchPrefix']
    for name,width,meaning in FIELDS:result.append((name.ljust(16)+'db #00').ljust(80)+'; '+meaning)
    result+=['                ends','                assert FClipDispatchPrefix == 8']
    result+=['                assert FClipDispatchPrefix.'+name+' == '+str(i) for i,(name,width,meaning) in enumerate(FIELDS)]
    return '\n'.join(result)+'\n'

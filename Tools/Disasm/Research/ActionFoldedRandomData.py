"""Три физические трёхбайтовые записи, соседние неизвестные байты не объединяются с ними."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records
from ActionRandomStreamLayout import STREAMS

FIELDS=(('LowWord',2,'младшее слово смешивающей рекурсии'),('FoldByte',1,'байт свёртки переносов, числовое состояние, не набор флагов'))
TABLES=tuple(('ActionRandomStreams','Source/Action/Data/FoldRandomStream'+str(index)+'.asm',offset,offset+3,
    'FFoldedRandomState',FIELDS,('Stream'+str(index),)) for index,offset in
    sorted(((index,pointer-0x6000) for index,_,pointer in STREAMS),key=lambda pair:pair[1]))


def render(source,table):
    text,symbols=render_records(source,table,0x6000)
    text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)')
    return text,symbols


def parse(text,table):
    clean=[line.partition(';')[0].rstrip() for line in text.splitlines() if line.partition(';')[0].strip()]
    module,path,start,end,structure,fields,names=table
    assert len(clean)==8 and clean[:3]==['                module '+module,
        '                assert $ == #'+format(start+0x6000,'04X'),(names[0]+':').ljust(16)+structure+' {']
    assert re.fullmatch(r'\s+#[0-9A-F]{4},',clean[3]) and re.fullmatch(r'\s+#[0-9A-F]{2}',clean[4])
    assert clean[5:]==['                }','                assert $ == #'+format(end+0x6000,'04X'),'                endmodule']
    return parse_records(text,table,0x6000)

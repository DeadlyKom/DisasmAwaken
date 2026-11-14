"""Исходный поток XOR-линии и девять классовых байтов State02/10."""
from PreviewSceneTables import render as render_records,parse as parse_records

TABLES=(
    ('ActionOverlayLineData','Source/Action/Data/OverlayLine.asm',0x8B6E,0x8B72,'FOverlayLine',
     (('Header',1,'B2, открытый XOR-сегмент из двух вершин'),('FirstIndex',1,'байтовое смещение первой FRenderProjectedPoint'),
      ('SecondIndex',1,'байтовое смещение второй FRenderProjectedPoint'),('Terminator',1,'полный нулевой конец потока')),('Line',)),
    ('ActionClassSpawnValues','Source/Action/Data/ClassSpawnValues.asm',0x9280,0x9289,'FMissileRepeatDelay',
     (('Counter',1,'начальное значение MissileRepeatDelay после попытки пуска, авторский счётчик RCO'),),tuple('Class'+str(i) for i in range(9))))


def render(source,table):
    text,labels=render_records(source,table,0x6000)
    document='ActionOverlayPair' if table[0]=='ActionOverlayLineData' else 'ActionSpawnWindow'
    text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)','[физические данные связанного состояния](../../../Docs/'+document+'.md)')
    return text,labels


def parse(text,table):return parse_records(text,table,0x6000)


def structures():
    lines=[]
    for _,_,_,_,name,fields,_ in TABLES:
        lines+=['','                ; Исходная физическая запись связанного состояния','                struct '+name]
        offset=0
        for field,width,note in fields:
            lines.append((field.ljust(16)+'db #00').ljust(80)+'; '+note);offset+=width
        lines+=['                ends','                assert '+name+' == #'+format(offset,'02X')]
        offset=0
        for field,width,_ in fields:
            lines.append('                assert '+name+'.'+field+' == #'+format(offset,'02X'));offset+=width
    return '\n'.join(lines)+'\n'

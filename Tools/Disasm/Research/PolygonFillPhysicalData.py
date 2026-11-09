"""Старшая страница диспетчера, пять шаблонов и разреженные пары крайних масок."""
import json,re
from CheckIntro import ROOT
from PreviewSceneTables import render as render_records,parse as parse_records

HIGH_FIELDS=tuple(('SecondSides'+format(i,'X'),1,'старший байт адреса при младшей тетраде второго кода '+format(i,'X')) for i in range(16))
PATTERN_FIELDS=(('Pattern',1,'шаблон первой строки контура'),('RowXor',1,'XOR шаблона при переходе к следующей строке'))
MASK_FIELDS=(('Preserve',1,'единичные биты сохраняют прежние пиксели вне заполняемой части'),
             ('Apply',1,'единичные биты устанавливают пиксели выбранного шаблона'))
PATTERNS=((255,0),(119,170),(85,255),(17,85),(0,0))
TABLES=[]
for slot,origin,base,region in ((17,0x6000,0x7000,'Action'),(19,0xC000,0x1000,'ThreeD')):
    TABLES.extend(((slot,origin,(region+'ClipTargetHigh','Source/'+region+'/Data/ClipTargetHigh.asm',base,base+256,
        'FClipTargetHighRow',HIGH_FIELDS,tuple('FirstSides'+format(i,'X') for i in range(16)))),
        (slot,origin,(region+'PolygonPatterns','Source/'+region+'/Data/PolygonPatterns.asm',base+256,base+266,
        'FPreviewFillPattern',PATTERN_FIELDS,tuple('Mode'+str(i) for i in range(5))))))
for parity in range(2):
    for phase in range(8):
        for right in (False,True):
            tag=('Odd' if parity else 'Even')+('Right' if right else 'Left')+str(phase)
            start=0x2C00+parity*256+phase*32+(16 if right else 0)
            TABLES.append((17,0x6000,('ActionPolygonMask'+tag,'Source/Action/Data/PolygonMasks/'+tag+'.asm',
                start,start+10,'FPolygonEdgeMask',MASK_FIELDS,tuple('Mode'+str(i) for i in range(5)))))
TABLES=tuple(TABLES)
BINDINGS=(('ActionPolygonPreparationState','Patterns',0xD100,'ActionPolygonPatterns.Mode0.Pattern'),)
REQUIRED_REPORTS=('ActionPolygonFillBitmapVerification','ActionClipDispatchTable','ThreeDOverlayMirrorVerification')
DOCUMENT='PolygonFillPhysicalData'
TAG='PolygonFillPhysicalData'


def validate_sources(sources):
    rows=json.loads((ROOT/'Tools/Disasm/Reports/ActionClipDispatchTable.json').read_bytes())['rows']
    valid={row['index']:row for row in rows};assert len(valid)==81
    for slot,base in ((17,0x7000),(19,0x1000)):
        data=sources[slot]
        assert data[base+256:base+266]==bytes(v for pair in PATTERNS for v in pair)
        for index in range(256):
            if index in valid:
                assert data[base-256+index]+256*data[base+index]==valid[index]['target']
            else:assert data[base+index]==0
    data=sources[17]
    for parity in range(2):
        for phase in range(8):
            for mode,(first,delta) in enumerate(PATTERNS):
                pattern=first^(delta if parity else 0)
                for right in (False,True):
                    start=0x2C00+parity*256+phase*32+mode*2+(16 if right else 0)
                    preserve=(255>>phase) if right else ((255<<(8-phase))&255)
                    assert data[start:start+2]==bytes((preserve,pattern&~preserve))
    return dict(valid_dispatch_pairs=81,high_page_bytes=512,pattern_bytes=20,mask_bytes=320)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    # Файлы строк масок расположены на один каталог глубже остальных данных.
    prefix='../../../../' if '/PolygonMasks/' in table[1] else '../../../'
    text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                      '[физические таблицы заливки и диспетчера]('+prefix+'Docs/'+DOCUMENT+'.md)')
    if table[4]=='FClipTargetHighRow':
        rows={r['index']:r for r in json.loads((ROOT/'Tools/Disasm/Reports/ActionClipDispatchTable.json').read_bytes())['rows']}
        region='ThreeD' if table[0].startswith('ThreeD') else 'Action';first=second=None;out=[]
        for line in text.splitlines():
            match=re.match(r'FirstSides([0-9A-F]):',line)
            if match:first=int(match[1],16);second=0
            elif first is not None and re.match(r'\s+#[0-9A-F]{2}',line):
                index=first*16+second;field='SecondSides'+format(second,'X')
                meaning=('старший байт @'+region+'.'+rows[index]['name']+'.Entry, индекс '+format(index,'02X')
                         if index in rows else 'индекс '+format(index,'02X')+' не получается из 81 нормальной пары, исходный байт сохранён')
                code=line.partition(';')[0].rstrip()
                if index in rows:code=' '*20+'HIGH(@'+region+'.'+rows[index]['name']+'.Entry)'+(',' if second<15 else '')
                line=code.ljust(80)+'; '+field+', '+meaning;second+=1
            out.append(line)
        text='\n'.join(out)+'\n'
    return text,labels


def parse(text,origin,table):
    symbols={k.upper():v for k,v in json.loads((ROOT/'Tools/Disasm/Reports/Symbols.json').read_bytes()).items()}
    # Вычисление только документированного HIGH известного глобального адреса.
    text=re.sub(r'HIGH\(@([A-Za-z_][A-Za-z0-9_.]*)\)',
                lambda m:'#'+format((symbols[m[1].upper()]>>8)&255,'02X'),text)
    return parse_records(text,table,origin)


def structures():
    lines=['                ; Строка старших байтов разделённого диспетчера, младшая тетрада выбирает поле',
           '                struct FClipTargetHighRow']
    for name,width,meaning in HIGH_FIELDS:lines.append((name.ljust(16)+'db #00').ljust(80)+'; '+meaning)
    lines+=['                ends','                assert FClipTargetHighRow == 16']
    lines+=['                assert FClipTargetHighRow.'+name+' == '+str(i) for i,(name,width,meaning) in enumerate(HIGH_FIELDS)]
    lines+=['','                ; Сохранение и установка крайних пикселей по формуле (старый AND Preserve) OR Apply',
            '                struct FPolygonEdgeMask']
    for name,width,meaning in MASK_FIELDS:lines.append((name.ljust(16)+'db #00').ljust(80)+'; '+meaning)
    lines+=['                ends','                assert FPolygonEdgeMask == 2','                assert FPolygonEdgeMask.Preserve == 0',
            '                assert FPolygonEdgeMask.Apply == 1']
    return '\n'.join(lines)+'\n'

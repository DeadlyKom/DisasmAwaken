"""Оставшиеся физические части младшей страницы, без рабочих STRUCT и спорного CF08."""
import json,re
from CheckIntro import ROOT
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=tuple(('SecondSides'+format(i,'X'),1,'младший байт адреса при младшей тетраде второго кода '+format(i,'X')) for i in range(16))
TABLES=[]
for slot,origin,region in ((17,0x6000,'Action'),(19,0xC000,'ThreeD')):
    for row in (1,2):
        start=0xCF00+16*row-origin
        TABLES.append((slot,origin,(region+'ClipTargetLowRow'+str(row),'Source/'+region+'/Data/ClipTargetLowRow'+str(row)+'.asm',
            start,start+11,'FClipTargetLowHead',FIELDS[:11],('FirstSides'+str(row),))))
    start=0xCF3B-origin
    TABLES.append((slot,origin,(region+'ClipTargetLowTail3','Source/'+region+'/Data/ClipTargetLowTail3.asm',
        start,start+5,'FClipTargetLowTail',FIELDS[11:],('First3Tail',))))
    start=0xCF40-origin
    TABLES.append((slot,origin,(region+'ClipTargetLowRows4F','Source/'+region+'/Data/ClipTargetLowRows4F.asm',
        start,start+192,'FClipTargetLowRow',FIELDS,tuple('FirstSides'+format(i,'X') for i in range(4,16)))))
TABLES=tuple(TABLES)
BINDINGS=()
REQUIRED_REPORTS=('PolygonFillPhysicalDataClassification','ActionClipDispatchTable','ThreeDOverlayMirrorVerification')
DOCUMENT='ClipTargetLowPhysicalData'
TAG='ClipTargetLowPhysicalData'


def validate_sources(sources):
    rows={r['index']:r for r in json.loads((ROOT/'Tools/Disasm/Reports/ActionClipDispatchTable.json').read_bytes())['rows']}
    count=0
    for slot,origin,table in TABLES:
        for offset in range(table[2],table[3]):
            index=origin+offset-0xCF00;raw=sources[slot]
            if index in rows:
                assert raw[offset]+256*raw[offset+256]==rows[index]['target'];count+=1
            else:assert raw[offset]==0
    assert count==144
    assert all(sources[slot][0xCF08-origin:0xCF0B-origin]==bytes.fromhex('F3AFC9') for slot,origin in ((17,0x6000),(19,0xC000)))
    return dict(low_page_bytes=438,valid_low_entries=144,untouched_cf08_bytes=6)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                      '[физические младшие байты диспетчера](../../../Docs/'+DOCUMENT+'.md)')
    rows={r['index']:r for r in json.loads((ROOT/'Tools/Disasm/Reports/ActionClipDispatchTable.json').read_bytes())['rows']}
    region='ThreeD' if table[0].startswith('ThreeD') else 'Action';offset=table[2];out=[];field=0
    for line in text.splitlines():
        if re.match(r'\w+:\s+FClipTargetLow',line):field=0
        elif re.match(r'\s+#[0-9A-F]{2}',line):
            index=origin+offset-0xCF00;name=table[5][field][0];code=line.partition(';')[0].rstrip()
            if index in rows:
                code=' '*20+'LOW(@'+region+'.'+rows[index]['name']+'.Entry)'+(',' if field+1<len(table[5]) else '')
                meaning='младший байт @'+region+'.'+rows[index]['name']+'.Entry, индекс '+format(index,'02X')
            else:meaning='индекс '+format(index,'02X')+' вне 81 нормальной пары, исходный байт сохранён'
            assert len(code)<=80;line=code.ljust(80)+'; '+name+', '+meaning;offset+=1;field+=1
        out.append(line)
    assert offset==table[3]
    return '\n'.join(out)+'\n',labels


def parse(text,origin,table):
    symbols={k.upper():v for k,v in json.loads((ROOT/'Tools/Disasm/Reports/Symbols.json').read_bytes()).items()}
    text=re.sub(r'LOW\(@([A-Za-z_][A-Za-z0-9_.]*)\)',lambda m:'#'+format(symbols[m[1].upper()]&255,'02X'),text)
    return parse_records(text,table,origin)


def structures():
    lines=[]
    for name,fields in (('FClipTargetLowRow',FIELDS),('FClipTargetLowHead',FIELDS[:11]),('FClipTargetLowTail',FIELDS[11:])):
        lines+=['                ; Физическая часть строки младших адресов, пропущенные части заняты отдельными структурами',
                '                struct '+name]
        for field,width,meaning in fields:lines.append((field.ljust(16)+'db #00').ljust(80)+'; '+meaning)
        lines+=['                ends','                assert '+name+' == '+str(len(fields))]
        lines+=['                assert '+name+'.'+field+' == '+str(i) for i,(field,width,meaning) in enumerate(fields)]
        lines+=['']
    return '\n'.join(lines)+'\n'

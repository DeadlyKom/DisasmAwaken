"""Восстановленные цепочки заголовков и 48-пиксельных растров в BANK0..BANK5."""
from pathlib import Path
import re
from CheckIntro import ROOT

ROW_BYTES=6
WIDTH=48
SLOTS=tuple(range(33,39))
DOCUMENT='BankScreenStrips'
STRUCTURE='FScreenBitmapStrip'


def screen_position(address):
    assert 0x4000<=address<0x5800
    return address&31,((address>>5)&192)|((address>>8)&7)|((address>>2)&56)


def record(data,start,row_bytes=ROW_BYTES):
    if not 0<=start<=len(data)-3:return None
    address=int.from_bytes(data[start:start+2],'little');height=data[start+2]
    if not(0x4000<=address<0x5800 and height):return None
    column,y=screen_position(address);end=start+3+row_bytes*height
    if column+row_bytes>32 or y+height>192 or end>len(data):return None
    return dict(start=start,end=end,screen_address=address,column=column,y=y,height=height)


def prefix(data,row_bytes):
    rows=[];position=0
    while row:=record(data,position,row_bytes):rows.append(row);position=row['end']
    return rows,position


def analyze(data):
    assert len(data)==16384
    widths={width:len(prefix(data,width)[0]) for width in range(1,17)}
    # Выбор шага по цепочке действительных экранных заголовков, не по виду отдельного рисунка.
    assert [width for width,count in widths.items() if count>=4]==[ROW_BYTES],widths
    first,first_end=prefix(data,ROW_BYTES)
    assert len(first)==14
    floors={row['y']+row['height'] for row in first};columns={row['column'] for row in first}
    assert floors=={187} and columns=={0}
    # Независимый обратный проход от конца файла, неоднозначный предшественник запрещён.
    last=[];end=len(data)
    while True:
        candidates=[]
        for height in range(1,193):
            start=end-3-ROW_BYTES*height
            if start<first_end:continue
            row=record(data,start)
            if row and row['end']==end and row['y']+row['height'] in floors and row['column'] in columns:
                candidates.append(row)
        assert len(candidates)<=1,('ambiguous predecessor',end,candidates)
        if not candidates:break
        row=candidates[0];last.append(row);end=row['start']
    last.reverse();assert len(last)>=12 and first_end<end
    for group in (first,last):
        assert len(group)%2==0
        for a,b in zip(group[::2],group[1::2]):
            assert (a['screen_address'],a['height'])==(b['screen_address'],b['height'])
    return dict(prefix=first,suffix=last,gap_start=first_end,gap_end=end,width_chain_lengths=widths)


def tables(sources):
    result=[]
    for slot in SLOTS:
        layout=analyze(sources[slot]);number=slot-33;first_index=0
        for tag in ('prefix','suffix'):
            rows=[]
            for index,row in enumerate(layout[tag],first_index):rows.append(dict(row,index=index))
            first_index+=len(rows)
            result.append(dict(slot=slot,module='Bank'+str(number)+'Strips'+tag.title(),
                path='Source/Resources/'+str(slot)+'_BANK'+str(number)+'/Strips'+tag.title()+'.asm',
                start=rows[0]['start'],end=rows[-1]['end'],rows=rows))
    return result


def additional_tables(sources):
    result=[]
    for slot in SLOTS:
        data=sources[slot];layout=analyze(data);pairs=[]
        for start in range(layout['gap_start'],layout['gap_end']-3):
            a=record(data,start)
            if not a or a['end']>layout['gap_end'] or a['column']!=0 or a['y']+a['height']!=187:continue
            b=record(data,a['end'])
            if b and b['end']<=layout['gap_end'] and (a['screen_address'],a['height'])==(b['screen_address'],b['height']):pairs.append((a,b))
        if slot not in (37,38):assert not pairs;continue
        assert len(pairs)==1
        first_index=len(layout['prefix'])+len(layout['suffix'])
        rows=[dict(row,index=index) for index,row in enumerate(pairs[0],first_index)]
        result.append(dict(slot=slot,module='Bank'+str(slot-33)+'StripsAdditional',
            path='Source/Resources/'+str(slot)+'_BANK'+str(slot-33)+'/StripsAdditional.asm',
            start=rows[0]['start'],end=rows[-1]['end'],rows=rows))
    return result


def partial_copy_tables(sources):
    original = analyze(sources[36])['suffix'][2]
    start = original['start']
    assert (start, original['screen_address'], original['height']) == (0x265C, 0x4980, 90)
    copies = []
    for slot, end in ((37, 0x27A0), (38, 0x26B0)):
        data = sources[slot]
        assert analyze(data)['gap_end'] == end < original['end']
        assert data[start:end] == sources[36][start:end] and data[end:end + 3] != sources[36][end:end + 3]
        number = slot - 33
        copies.append(dict(slot=slot, module=f'Bank{number}PartialStripCopy',
            path=f'Source/Resources/{slot}_BANK{number}/PartialStripCopy.asm',
            start=start, end=end, rows=[dict(original, index=28, end=end, partial_copy=True)]))
    return copies


def all_tables(sources):
    return sorted(tables(sources) + additional_tables(sources) + partial_copy_tables(sources),
                  key=lambda table: (table['slot'], table['start']))


def render(data,table):
    module=table['module'];lines=['                module '+module,
        '                ; Метки являются смещениями файла BANK, номер аппаратного банка не назначается',
        '                ; Документация [заголовки и растры BANK](../../../Docs/'+DOCUMENT+'.md)',
        '                assert $ == #'+format(table['start'],'04X')]
    bitmaps={};symbols={}
    for row in table['rows']:
        number=format(row['index'],'02d');label='Strip'+number;pixels='Pixels'+number
        path=Path(table['path']).parent.as_posix()+'/Strips/Strip'+number+'.bitmap'
        payload=data[row['start']+3:row['end']]
        partial = row.get('partial_copy', False)
        bitmaps[path]=payload
        if partial:
            assert len(payload) < ROW_BYTES*row['height']
            lines.append('                ; Неполная копия полосы BANK3, сохранены заголовок и '+str(len(payload))+' байтов растра')
        else:
            assert len(payload) == ROW_BYTES*row['height']
        height_note = 'высота из исходного заголовка' if partial else 'число строк растра'
        lines+=['                ; -----------------------------------------',
                '                ; Экранная строка '+str(row['y'])+', высота '+str(row['height'])+', шесть байтов на строку',
                (label+':').ljust(16)+STRUCTURE+' {',
                ('                    #'+format(row['screen_address'],'04X')+',').ljust(80)+'; ScreenAddress, исходное слово экранных координат',
                ('                    #'+format(row['height'],'02X')).ljust(80)+'; Height, '+height_note,
                '                }',(pixels+':').ljust(16)+'incbin "Strips/Strip'+number+'.bitmap"']
        symbols[module+'.'+label]=row['start'];symbols[module+'.'+label+'.ScreenAddress']=row['start']
        symbols[module+'.'+label+'.Height']=row['start']+2;symbols[module+'.'+pixels]=row['start']+3
    lines+=['                assert $ == #'+format(table['end'],'04X'),'                endmodule','']
    return '\n'.join(lines),symbols,bitmaps


def parse(text,table,bitmap_overrides=None):
    code='\n'.join(line.partition(';')[0] for line in text.splitlines())
    pattern=(r'(Strip\d+):\s+FScreenBitmapStrip\s*\{\s*#([0-9A-Fa-f]+)\s*,\s*#([0-9A-Fa-f]+)\s*\}'
             r'\s*(Pixels\d+):\s+incbin\s+"([^"]+)"')
    matches=list(re.finditer(pattern,code));assert len(matches)==len(table['rows'])
    raw=bytearray();symbols={};module=table['module'];position=table['start']
    for match,row in zip(matches,table['rows']):
        label,address,height,pixels,relative=match.groups();address=int(address,16);height=int(height,16)
        number=format(row['index'],'02d');assert (label,pixels,relative)==('Strip'+number,'Pixels'+number,'Strips/Strip'+number+'.bitmap')
        assert position==row['start'] and (address,height)==(row['screen_address'],row['height'])
        path=(Path(table['path']).parent/relative).as_posix()
        payload=(bitmap_overrides or {}).get(path)
        if payload is None:payload=(ROOT/path).read_bytes()
        assert len(payload)==row['end']-row['start']-3
        if not row.get('partial_copy', False):
            assert len(payload)==ROW_BYTES*height
        raw+=address.to_bytes(2,'little')+bytes((height,))+payload
        symbols[module+'.'+label]=position;symbols[module+'.'+label+'.ScreenAddress']=position
        symbols[module+'.'+label+'.Height']=position+2;symbols[module+'.'+pixels]=position+3
        position+=3+len(payload)
    remainder=re.sub(pattern,'',code)
    expected=['module '+module,'assert $ == #'+format(table['start'],'04X'),
              'assert $ == #'+format(table['end'],'04X'),'endmodule']
    assert [line.strip() for line in remainder.splitlines() if line.strip()]==expected
    assert position==table['end']
    return bytes(raw),symbols


def structures():
    return '''
                ; Физический заголовок растровой полосы BANK, метаданные не задают банк загрузки
                struct FScreenBitmapStrip
ScreenAddress   dw #0000                                                        ; слово координат в раскладке ULA-экрана
Height          db #00                                                          ; количество следующих строк по шесть байтов
                ends
                assert FScreenBitmapStrip == 3
                assert FScreenBitmapStrip.ScreenAddress == 0
                assert FScreenBitmapStrip.Height == 2
'''


def verify_published(sources,source_map,symbols=None):
    from BankArchiveRouteCopies import TABLES as route_tables
    from BankStagingTails import RANGES as staging_ranges, path_for, split_gap
    import BankArchiveTileCopies as tiles

    definitions=tables(sources)
    published = {row['path'] for row in source_map}
    if any(tiles.path_for(slot) in published for slot in tiles.RANGES):
        tiles.verify_original(sources)
    routes = {slot: table for slot, _, table in route_tables if table[1] in published}
    additions = [table for table in additional_tables(sources) + partial_copy_tables(sources)
                 if table['path'] in published]
    if symbols is not None:
        assert symbols[STRUCTURE.upper()]==3
        assert symbols[(STRUCTURE+'.ScreenAddress').upper()]==0 and symbols[(STRUCTURE+'.Height').upper()]==2
    for slot in SLOTS:
        data=sources[slot];layout=analyze(data);current=[r for r in source_map if r['slot']==slot]
        groups=sorted([t for t in definitions+additions if t['slot']==slot],key=lambda t:t['start'])
        expected=[];position=0
        for table in groups:
            if position<table['start']:
                basename='UnknownGap'+format(position,'04X')+'_'+format(table['start'],'04X')+'.bin' if len(groups)>2 else 'UnknownGap.bin'
                gap_path='Source/Resources/'+str(slot)+'_BANK'+str(slot-33)+'/'+basename
                expected.append((position,table['start']-position,'unclassified',gap_path))
            expected.append((table['start'],table['end']-table['start'],'typed_data',table['path']));position=table['end']
        assert position==len(data)
        if slot in routes:
            _, route_path, first, last, *_ = routes[slot]
            gap = next(row for row in expected if row[2] == 'unclassified'
                       and row[0] < first < last < row[0] + row[1])
            start, length, _, old_path = gap
            end = start + length
            directory = old_path.rsplit('/', 1)[0]
            expected[expected.index(gap):expected.index(gap) + 1] = [
                (start, first - start, 'unclassified', f'{directory}/Unclassified{start:04X}_{first:04X}.bin'),
                (first, last - first, 'typed_data', route_path),
                (last, end - last, 'unclassified', f'{directory}/Unclassified{last:04X}_{end:04X}.bin'),
            ]
        if slot in staging_ranges and path_for(slot) in published:
            gap = next(row for row in expected if row[0] == staging_ranges[slot][0])
            assert gap[2] == 'unclassified'
            expected[expected.index(gap):expected.index(gap) + 1] = split_gap(slot, gap[0], gap[1])
        if slot in tiles.RANGES and tiles.path_for(slot) in published:
            gap = next(row for row in expected if row[0] == tiles.RANGES[slot][0])
            assert gap[2] == 'unclassified'
            expected[expected.index(gap):expected.index(gap) + 1] = tiles.split_gap(slot, gap[0], gap[1])
        assert [(r['offset'],r['length'],r['kind'],r['path']) for r in current]==expected
        for table in groups:
            raw,labels=parse((ROOT/table['path']).read_text('utf-8'),table)
            assert raw==data[table['start']:table['end']]
            if symbols is not None:assert all(symbols[key.upper()]==value for key,value in labels.items())
        for start,length,kind,path in expected:
            if kind in ('unclassified', 'binary_resource'):
                assert (ROOT/path).read_bytes()==data[start:start+length]
    return definitions

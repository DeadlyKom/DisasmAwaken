"""Сверка цепочек BANK, каждого пиксельного бита и чувствительности к неверному заголовку."""
import hashlib,json,os,tempfile
from PIL import Image,ImageDraw
from CheckIntro import ROOT
import BankScreenStrips as facts


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entries={e['slot']:e for e in manifest['entries']};original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    sources={slot:(ROOT/(entries[slot]['path']+'.bin')).read_bytes() for slot in facts.SLOTS}
    for slot,data in sources.items():assert data==original[entries[slot]['offset']:entries[slot]['offset']+16384]
    # Проверка всех экранных байтов независимой формулой кодирования координат ULA.
    for address in range(0x4000,0x5800):
        column,y=facts.screen_position(address)
        assert 0x4000+256*(y%8)+32*((y//8)%8)+2048*(y//64)+column==address
    tables=facts.tables(sources);bitmaps={};all_rows={slot:[] for slot in facts.SLOTS};symbols={};published=0
    for table in tables:
        data=sources[table['slot']];text,labels,parts=facts.render(data,table)
        assert facts.parse(text,table,parts)==(data[table['start']:table['end']],labels)
        bitmaps.update(parts);symbols.update(labels);all_rows[table['slot']].extend(table['rows'])
        if (ROOT/table['path']).exists():
            assert facts.parse((ROOT/table['path']).read_text('utf-8'),table)==(data[table['start']:table['end']],labels)
            published+=1
    first=tables[0];text,labels,parts=facts.render(sources[first['slot']],first)
    row=first['rows'][0];needle='                    #'+format(row['height'],'02X')
    assert text.count(needle)>=1
    # Проверка чувствительности к изменению высоты только в тексте кандидата.
    rejected=False
    try:facts.parse(text.replace(needle,'                    #'+format(row['height']+1,'02X'),1),first,parts)
    except AssertionError:rejected=True
    assert rejected
    # Отдельный атлас по исходным координатам, ориентация просмотра не заменяет игровой договор.
    summaries=[];total_bits=0
    for slot,rows in all_rows.items():
        top=min(row['y'] for row in rows);height=187-top;cell_height=height+28
        atlas=Image.new('RGB',(8*56,((len(rows)+7)//8)*cell_height),'white');draw=ImageDraw.Draw(atlas)
        data=sources[slot]
        for row in rows:
            index=row['index'];x=(index%8)*56;y=(index//8)*cell_height
            draw.text((x,y),str(index)+'/'+str(row['height']),fill='black')
            raw=data[row['start']+3:row['end']];pixels=bytearray()
            for byte in raw:
                pixels.extend(255*(1-((byte>>bit)&1)) for bit in range(7,-1,-1))
            assert len(pixels)==facts.WIDTH*row['height']
            # Независимая проверка адреса каждого бита внутри шестибайтовой строки.
            for pixel,value in enumerate(pixels):
                ry,rx=divmod(pixel,facts.WIDTH)
                assert value==(0 if raw[6*ry+rx//8]&(128>>(rx%8)) else 255)
            image=Image.frombytes('L',(facts.WIDTH,row['height']),bytes(pixels))
            atlas.paste(image,(x,y+20+row['y']-top));total_bits+=len(pixels)
        name='Bank'+str(slot-33)+'ScreenStrips.png';path=ROOT/'Tools/Disasm/Research/Evidence'/name
        if path.exists():assert Image.open(path).convert('RGB').tobytes()==atlas.tobytes()
        else:path.parent.mkdir(parents=True,exist_ok=True);atlas.save(path)
        layout=facts.analyze(data);covered=sum(row['end']-row['start'] for row in rows)
        summaries.append(dict(slot=slot,name=entries[slot]['name'],prefix_records=len(layout['prefix']),
            prefix_end=layout['gap_start'],suffix_records=len(layout['suffix']),suffix_start=layout['gap_end'],
            interpreted_graphic_bytes=covered,unknown_gap_bytes=layout['gap_end']-layout['gap_start'],
            gap_sha256=hashlib.sha256(data[layout['gap_start']:layout['gap_end']]).hexdigest(),
            width_candidate_chain_lengths=layout['width_chain_lengths'],
            preview='Tools/Disasm/Research/Evidence/'+name))
    covered=sum(row['interpreted_graphic_bytes'] for row in summaries);count=sum(map(len,all_rows.values()))
    assert (count,covered,total_bits)==(166,86874,691008)
    assert published in (0,len(tables))
    result=dict(passed=True,files=6,source_bytes=98304,record_count=count,paired_equal_geometry_records=count//2,
        interpreted_graphic_bytes=covered,header_bytes=3*count,linear_bitmap_bytes=covered-3*count,
        pixel_bits_independently_checked=total_bits,unknown_gap_bytes=98304-covered,
        row_bytes_uniquely_supported_by_long_prefix_chains=6,all_byte_columns_zero=True,all_bottom_rows_exclusive=187,
        reverse_suffix_predecessors_unambiguous=True,all_original_bytes_roundtrip=True,wrong_height_probe_rejected=True,
        published_tables_checked=published,summaries=summaries,runtime_loader_proved=False,
        runtime_bitmap_orientation_proved=False,paired_records_temporal_relation_proved=False,
        hardware_bank_numbers_proved=False,assembly_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/BankScreenStripsVerification.json'
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix='bank-strips-',suffix='.tmp',delete=False) as out:
        temporary=out.name;out.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,path)
    print(json.dumps({key:result[key] for key in ('passed','record_count','interpreted_graphic_bytes','header_bytes',
        'linear_bitmap_bytes','pixel_bits_independently_checked','unknown_gap_bytes','wrong_height_probe_rejected','published_tables_checked')},indent=2))


if __name__=='__main__':main()

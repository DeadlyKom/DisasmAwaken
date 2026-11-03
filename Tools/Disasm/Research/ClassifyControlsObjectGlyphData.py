"""Однократная типизация 672 доказанных байтов, кандидат и проверка перед заменой."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ControlsObjectGlyphData as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsObjectGlyphsVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==23 and i['offset']==0xB7F)
    assert (item['length'],item['kind'],item['path'])==(672,'unclassified','Source/Resources/23_CONTROL/Unclassified005.bin')
    previous=ROOT/item['path'];original=previous.read_bytes()
    assert original==source[0xB7F:0xE1F]
    pending={};pieces=[]
    for table in facts.TABLES:
        module,path,start,end,structure,fields,names=table
        text,bindings=facts.render(source,table)
        assert facts.parse(text,table)==(source[start:end],bindings)
        assert not any(key in symbols for key in bindings)
        assert not (ROOT/path).exists()
        symbols.update(bindings)
        pending[ROOT/path]=text.encode('utf-8')
        pieces.append(dict(slot=23,offset=start,length=end-start,kind='typed_data',path=path,
            origin=0xDADE+start,sha256=hashlib.sha256(source[start:end]).hexdigest()))
    index=source_map.index(item);source_map[index:index+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind)
        for kind in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');block='\n'
    for table in facts.TABLES[:3]:
        module,_,start,end,structure,fields,names=table
        assert 'struct '+structure not in text
        block+='                ; Физическая запись ресурса '+module+'\n                struct '+structure+'\n'
        for name,width,note in fields:
            block+=name.ljust(16)+('dw #0000' if width==2 else 'db #00').ljust(64)+'; '+note+'\n'
        block+='                ends\n                assert '+structure+' == '+str(sum(f[1] for f in fields))+'\n\n'
    assert text.count('                endif')==1
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/23_CONTROL.inc';text=path.read_text('utf-8')
    needle=('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
            '                incbin "../Resources/23_CONTROL/Unclassified005.bin"')
    assert text.count(needle)==1
    replacement=[]
    for table in facts.TABLES:
        module,path_string,start,end,structure,fields,names=table
        if replacement:
            replacement.append('                assert $ == #'+format(start,'04X'))
        replacement.extend(['                ; Физические записи '+module,
            '                disp #'+format(0xDADE+start,'04X'),
            '                include "../Controls/Data/'+path_string.rsplit('/',1)[-1]+'"','                ent'])
    pending[path]=text.replace(needle,'\n'.join(replacement)).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook='''    # Исходные физические ресурсы маскированных объектных значков.
    if "struct FObjectGlyphClearPhase" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsObjectGlyphData import TABLES as OBJECT_GLYPH_TABLES, render as render_object_glyph_data
        for table in OBJECT_GLYPH_TABLES:
            text, bindings = render_object_glyph_data(data_by_slot[23],table)
            write(table[1],text)
            symbols.update(bindings)
            special[23,table[2]] = (table[3],table[1],0xDADE+table[2])
'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    assert text.count(needle)==1
    hook='''    # Проверка 672 физических байтов указателей, масок и фаз объектных значков.
    from ControlsObjectGlyphData import TABLES as OBJECT_GLYPH_TABLES, parse as parse_object_glyph_data
    object_glyph_records = 0
    for table in OBJECT_GLYPH_TABLES:
        entries = [item for item in source_map if item['path']==table[1]]
        if entries:
            assert len(entries)==1
            item=entries[0]
            raw,labels=parse_object_glyph_data((ROOT/table[1]).read_text('utf-8'),table)
            assert (item['slot'],item['offset'],item['length'],item['origin'])==(23,table[2],table[3]-table[2],0xDADE+table[2])
            assert raw==sources[23][table[2]:table[3]]
            assert all(symbols.get(key.upper())==value for key,value in labels.items())
            assert symbols[table[4].upper()]==sum(field[1] for field in table[5])
            offset=0
            for name,width,note in table[5]:
                assert symbols[table[4].upper()+'.'+name.upper()]==offset
                offset+=width
            object_glyph_records+=len(table[6])

'''
    text=text.replace(needle,hook+needle)
    needle="    report['raster_return_records'] = raster_return_records"
    assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['object_glyph_records'] = object_glyph_records").encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsObjectGlyphData'
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsObjectGlyphData'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата перед проверкой конфликтов с рабочей копией.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    # Удаление заменённого бинарного блока только после точного сравнения с сохранённым оригиналом.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/23_CONTROL').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report=dict(passed=True,typed_bytes=672,physical_records=132,physical_shape_count=12,
        pointer_entries=20,unknown_clear_record_fields=['Unknown02','Unknown03','Unknown04','Unknown05'],
        physical_bytes_preserved=True,full_e291_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsObjectGlyphDataClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()

"""Физическая типизация четырёх записей, неизвестный байт 83 сохраняется явно."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionGlyphIndicatorState as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsGlyphIndicatorsVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==17 and i['offset']==0x3B19)
    assert (item['length'],item['kind'])==(0xD14,'unclassified')
    previous=ROOT/item['path']
    original=previous.read_bytes()
    assert original==source[0x3B19:0x482D]
    text,bindings=facts.render(source)
    assert facts.parse(text)==(source[facts.START:facts.END],bindings)
    assert not any(name in symbols for name in bindings)
    symbols.update(bindings)
    prefix='Source/Resources/17_ACTION/Unclassified020_BeforeGlyphIndicators.bin'
    suffix='Source/Resources/17_ACTION/Unclassified020_AfterGlyphIndicators.bin'
    pieces=[dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
        (0x3B19,0x3B81,'unclassified',prefix,None),
        (0x3B81,0x3B8D,'typed_data',facts.PATH,0x9B81),
        (0x3B8D,0x482D,'unclassified',suffix,None))]
    index=source_map.index(item)
    source_map[index:index+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind)
                                       for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.PATH:text.encode('utf-8'),ROOT/prefix:source[0x3B19:0x3B81],ROOT/suffix:source[0x3B8D:0x482D]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc'
    text=path.read_text('utf-8')
    block='\n                ; Физические входы трёх знаков, локальные роли установлены в E021\n'
    for name,fields in facts.STRUCTURES.items():
        assert 'struct '+name not in text
        block+='                struct '+name+'\n'
        for field,meaning in fields:
            block+=field.ljust(16)+('db #00').ljust(64)+'; '+meaning+'\n'
        block+='                ends\n                assert '+name+' == 3\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc'
    text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/Unclassified020_AfterWordRandom.bin"'
    assert text.count(needle)==1
    replacement=('                incbin "../Resources/17_ACTION/Unclassified020_BeforeGlyphIndicators.bin"\n'
        '                assert $ == #3B81\n                disp #9B81\n'
        '                include "../Action/Data/GlyphIndicatorState.asm"\n                ent\n'
        '                assert $ == #3B8D\n                ; Unknown, исходная область после входов знаков\n'
        '                incbin "../Resources/17_ACTION/Unclassified020_AfterGlyphIndicators.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py'
    text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook=('    # Четыре физические записи входов индикаторов, третий вектор хранит Y перед X.\n'
        '    if "struct FGlyphIndicatorControl" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ActionGlyphIndicatorState import PATH as GLYPH_INPUT_PATH, render as render_glyph_inputs\n'
        '        text, bindings = render_glyph_inputs(data_by_slot[17])\n'
        '        write(GLYPH_INPUT_PATH, text)\n        symbols.update(bindings)\n'
        '        special[17, 0x3B81] = (0x3B8D, GLYPH_INPUT_PATH, 0x9B81)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py'
    text=path.read_text('utf-8')
    needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    assert text.count(needle)==1
    hook='''    # Проверка четырёх физических записей входов трёх знаков.
    from ActionGlyphIndicatorState import PATH as GLYPH_INPUT_PATH, STRUCTURES as GLYPH_INPUT_STRUCTURES, parse as parse_glyph_inputs
    glyph_input_records = 0
    entries = [item for item in source_map if item['path'] == GLYPH_INPUT_PATH]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_glyph_inputs((ROOT/GLYPH_INPUT_PATH).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin']) == (17,0x3B81,12,0x9B81)
        assert raw == sources[17][0x3B81:0x3B8D]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        for name,fields in GLYPH_INPUT_STRUCTURES.items():
            assert symbols[name.upper()] == 3
            assert [symbols[name.upper()+'.'+field.upper()] for field,_ in fields] == [0,1,2]
        glyph_input_records = 4

'''
    text=text.replace(needle,hook+needle)
    needle="    report['three_row_glyph_records'] = three_row_glyph_records"
    assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['glyph_input_records'] = glyph_input_records").encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionGlyphIndicatorState'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionGlyphIndicatorState'
    assert not candidate.exists() and not history.exists()
    # Создание отдельного кандидата и проверка отсутствия новых пользовательских правок.
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    # Удаление только заменённого бинарного ресурса после сверки его сохранённой копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report=dict(passed=True,typed_bytes=12,physical_records=4,structures=list(facts.STRUCTURES),
        unknown_fields=['Control.Unknown83'],full_vector_game_meaning_proved=False,
        physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionGlyphIndicatorStateClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()

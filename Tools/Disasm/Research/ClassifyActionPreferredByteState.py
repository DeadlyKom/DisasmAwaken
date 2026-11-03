"""Типизация только двух исходных байтов, соседний ресурс сохраняется в двух частях."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionPreferredByteState as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionPreferredByteVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==17 and i['offset']==0x3B8D)
    assert (item['length'],item['kind'])==(0xCA0,'unclassified')
    previous=ROOT/item['path'];original=previous.read_bytes()
    assert original==source[0x3B8D:0x482D]
    text,bindings=facts.render(source)
    assert facts.parse(text)==(source[0x3C10:0x3C12],bindings)
    assert not any(key in symbols for key in bindings)
    symbols.update(bindings)
    prefix='Source/Resources/17_ACTION/Unclassified020_BeforePreferredByte.bin'
    suffix='Source/Resources/17_ACTION/Unclassified020_AfterPreferredByte.bin'
    pieces=[dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
        (0x3B8D,0x3C10,'unclassified',prefix,None),
        (0x3C10,0x3C12,'typed_data',facts.TABLE[1],0x9C10),
        (0x3C12,0x482D,'unclassified',suffix,None))]
    index=source_map.index(item);source_map[index:index+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind)
        for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8'),ROOT/prefix:source[0x3B8D:0x3C10],ROOT/suffix:source[0x3C12:0x482D]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8')
    assert 'struct FPreferredBytePair' not in text
    block='\n                ; Физическая пара ACTION для выбора значения и его изменяемого адреса\n                struct FPreferredBytePair\n'
    for name,width,note in facts.FIELDS:block+=name.ljust(16)+('db #00').ljust(64)+'; '+note+'\n'
    block+='                ends\n                assert FPreferredBytePair == 2\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+previous.name+'"'
    assert text.count(needle)==1
    replacement='                incbin "../Resources/17_ACTION/'+prefix.rsplit('/',1)[-1]+'"\n'
    replacement+='                assert $ == #3C10\n                disp #9C10\n                include "../Action/Data/PreferredByteState.asm"\n                ent\n'
    replacement+='                assert $ == #3C12\n                ; Unknown, соседний ресурс ещё не разобран\n'
    replacement+='                incbin "../Resources/17_ACTION/'+suffix.rsplit('/',1)[-1]+'"'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)'
    hook='''    # Физическая пара байтов, выбираемых вместе с адресом в ACTION.
    if "struct FPreferredBytePair" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionPreferredByteState import TABLE as PREFERRED_BYTES, render as render_preferred_bytes
        text,bindings=render_preferred_bytes(data_by_slot[17])
        write(PREFERRED_BYTES[1],text)
        symbols.update(bindings)
        special[17,0x3C10]=(0x3C12,PREFERRED_BYTES[1],0x9C10)
'''
    assert text.count(needle)==1
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    hook='''    # Проверка физической пары Preferred/Fallback, игровая семантика здесь не подменяется.
    from ActionPreferredByteState import TABLE as PREFERRED_BYTES, parse as parse_preferred_bytes
    preferred_byte_records=0
    entries=[item for item in source_map if item['path']==PREFERRED_BYTES[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_preferred_bytes((ROOT/PREFERRED_BYTES[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x3C10,2,0x9C10)
        assert raw==sources[17][0x3C10:0x3C12]
        assert all(symbols.get(key.upper())==value for key,value in labels.items())
        assert symbols['FPREFERREDBYTEPAIR']==2
        assert symbols['FPREFERREDBYTEPAIR.PREFERRED']==0 and symbols['FPREFERREDBYTEPAIR.FALLBACK']==1
        preferred_byte_records=1

'''
    assert text.count(needle)==1
    text=text.replace(needle,hook+needle)
    needle="    report['gauge_mask_records'] = gauge_mask_records"
    assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['preferred_byte_records'] = preferred_byte_records").encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionPreferredByteState'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionPreferredByteState'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и проверка отсутствия новых ручных изменений.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого бинарного блока после проверки исходной копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report=dict(passed=True,typed_bytes=2,physical_records=1,structure='FPreferredBytePair',
        physical_bytes_preserved=True,game_meaning_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionPreferredByteStateClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

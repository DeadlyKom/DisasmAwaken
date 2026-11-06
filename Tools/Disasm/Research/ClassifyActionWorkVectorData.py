"""Точечное описание девяти исходных рабочих байтов, соседние девять остаются без переименования."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionWorkVectorData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionSubtractWorkVectorVerification')['passed'] and read('ActionWorkVectorEntrySplitClassification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();text,labels=facts.render(source)
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x3B6F)
    assert old['kind']=='unclassified' and old['length']==18
    previous=ROOT/old['path'];original=previous.read_bytes();assert original==source[0x3B6F:0x3B81]
    prefix='Source/Resources/17_ACTION/BeforeWorkVector24.bin'
    pieces=[dict(old,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
        (0x3B6F,facts.START,'unclassified',prefix,None),(facts.START,facts.END,'typed_data',facts.PATH,0x9B78))]
    source_map[source_map.index(old):source_map.index(old)+1]=pieces
    assert not any(key in symbols for key in labels);symbols.update(labels)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.PATH:text.encode('utf-8'),ROOT/prefix:source[0x3B6F:facts.START]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8')
    assert 'struct FActionWorkVector24' not in text and text.count('                endif')==1
    pending[path]=text.replace('                endif',facts.STRUCT_BLOCK+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+previous.name+'"';assert text.count(needle)==1
    replacement=('                incbin "../Resources/17_ACTION/BeforeWorkVector24.bin"\n'
        '                assert $ == #3B78\n                disp #9B78\n'
        '                include "../Action/Data/WorkVector24.asm"\n                ent')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка трёх физических страниц корня, включая особый старший диапазон и исходные исключения.'
    assert text.count(needle)==1 and 'signed_work_vector_records' not in text
    hook='''    # Проверка физического 24-битного рабочего вектора и смещений всех вложенных полей.
    from ActionWorkVectorData import PATH as WORK_VECTOR, parse as parse_work_vector
    signed_work_vector_records = 0
    work_entries = [item for item in source_map if item['path'] == WORK_VECTOR]
    if work_entries:
        assert len(work_entries) == 1
        item = work_entries[0]
        raw, labels = parse_work_vector((ROOT / WORK_VECTOR).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x3B78, 9, 0x9B78)
        assert raw == sources[17][0x3B78:0x3B81]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FACTIONWORKCOMPONENT24'] == 3 and symbols['FACTIONWORKVECTOR24'] == 9
        assert symbols['FACTIONWORKCOMPONENT24.LOWWORD'] == 0 and symbols['FACTIONWORKCOMPONENT24.HIGH'] == 2
        for component in range(3):
            assert symbols['FACTIONWORKVECTOR24.COMPONENT'+str(component)] == 3*component
        signed_work_vector_records = 1

'''
    text=text.replace(needle,hook+needle);needle="    report['wide_vector_records'] = wide_vector_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['signed_work_vector_records'] = signed_work_vector_records").encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    needle='    # Шесть начальных широких векторов, байты и вложенный физический формат сохраняются.';assert text.count(needle)==1
    hook=('    # Физический знаковый рабочий вектор после соседнего отдельного блока.\n'
        '    from ActionWorkVectorData import PATH as WORK_VECTOR, render as render_work_vector\n'
        '    text, bindings = render_work_vector(data_by_slot[17])\n    write(WORK_VECTOR, text)\n    symbols.update(bindings)\n'
        '    special[17, 0x3B78] = (0x3B81, WORK_VECTOR, 0x9B78)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Docs/DataFormats.md';text=path.read_text('utf-8')
    pending[path]=(text+'\n## Знаковый рабочий вектор ACTION\n\n[WorkVector24](../Source/Action/Data/WorkVector24.asm) содержит физический FActionWorkVector24 с тремя FActionWorkComponent24. Каждая компонента состоит из LowWord и High в дополнительном коде, всего сохранены девять байтов 9B78..9B80. Это другой числовой формат, чем знак и модуль FComponent24. См. [вычитание и ранние выходы](ActionSubtractWorkVector.md).\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionWorkVectorData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionWorkVectorData'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes();previous.unlink()
    report=dict(passed=True,typed_bytes=9,physical_records=1,nested_signed_components=3,original_bytes_preserved=True,
        neighbor_bytes_preserved=9,arithmetic_game_meaning_not_extended_beyond_consumers=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionWorkVectorDataClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

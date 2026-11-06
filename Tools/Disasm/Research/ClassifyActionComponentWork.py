"""Физические три FComponent24 вместо доказанных девяти байтов, соседний хвост сохранён отдельно."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionComponentWorkData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionComponentEncodingVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();raw=facts.validate(source)
    text,labels=facts.render(source);assert facts.parse(text)==(raw,labels)
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x3B1E)
    assert old['kind']=='unclassified' and old['length']==99
    previous=ROOT/old['path'];original=previous.read_bytes();assert original==source[0x3B1E:0x3B81]
    suffix='Source/Resources/17_ACTION/Unclassified020_AfterComponentWork.bin'
    pieces=[dict(old,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
            (0x3B1E,0x3B27,'typed_data',facts.TABLE[1],0x9B1E),(0x3B27,0x3B81,'unclassified',suffix,None))]
    source_map[source_map.index(old):source_map.index(old)+1]=pieces
    assert not any(key in symbols for key in labels);symbols.update(labels)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8'),ROOT/suffix:source[0x3B27:0x3B81]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+previous.name+'"';assert text.count(needle)==1
    text=text.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'+needle,needle)
    replacement=('                disp #9B1E\n                include "../Action/Data/ComponentWork.asm"\n                ent\n'
        '                assert $ == #3B27\n                ; Unknown, соседние байты после трёх физических компонент\n'
        '                incbin "../Resources/17_ACTION/Unclassified020_AfterComponentWork.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка трёх физических страниц корня, включая особый старший диапазон и исходные исключения.'
    assert text.count(needle)==1 and 'component_work_records' not in text
    hook='''    # Проверка трёх физических FComponent24, старших знаковых слов и сохранённых младших байтов.
    from ActionComponentWorkData import TABLE as COMPONENT_WORK, parse as parse_component_work, validate as validate_component_work
    component_work_records = 0
    component_entries = [item for item in source_map if item['path'] == COMPONENT_WORK[1]]
    if component_entries:
        assert len(component_entries) == 1
        item = component_entries[0]
        raw, labels = parse_component_work((ROOT / COMPONENT_WORK[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x3B1E, 9, 0x9B1E)
        assert raw == validate_component_work(sources[17])
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FCOMPONENT24'] == 3
        assert [symbols['FCOMPONENT24.'+field] for field in ('LOW','MIDDLE','HIGH')] == [0,1,2]
        component_work_records = 3

'''
    text=text.replace(needle,hook+needle);needle="    report['root_cache_records'] = root_cache_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,"    report['component_work_records'] = component_work_records\n"+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1 and 'COMPONENT_WORK_TABLE' not in text
    hook=('    # Три физические исходные компоненты в общей RAM ACTION.\n'
        '    from ActionComponentWorkData import TABLE as COMPONENT_WORK_TABLE, render as render_component_work\n'
        '    text, bindings = render_component_work(data_by_slot[17])\n'
        '    write(COMPONENT_WORK_TABLE[1], text)\n    symbols.update(bindings)\n'
        '    special[17, 0x3B1E] = (0x3B27, COMPONENT_WORK_TABLE[1], 0x9B1E)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Docs/DataFormats.md';text=path.read_text('utf-8')
    paragraph='[ComponentWork](../Source/Action/Data/ComponentWork.asm) содержит три физических FComponent24 по три байта, Low/Middle/High имеют смещения 0/1/2. Старшее слово хранит знаковый код и 15-разрядный модуль после [кодирования](ActionComponentEncoding.md), физические девять исходных нулей сохранены.'
    pending[path]=(text+'\n## Физические компоненты преобразования\n\n'+paragraph+'\n').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/GenerateDocs.py';text=path.read_text('utf-8');line=next(v for v in text.splitlines() if '"| FComponent24 |' in v)
    row='| FComponent24 | #03 | Low, Middle, High, три физических [ComponentWork](../Source/Action/Data/ComponentWork.asm), см. [ActionComponentEncoding](ActionComponentEncoding.md) и [ControlsComponentCompare](ControlsComponentCompare.md) |'
    pending[path]=text.replace(line,line[:len(line)-len(line.lstrip())]+json.dumps(row,ensure_ascii=False)+',').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionComponentWork';history=ROOT/'Tools/Disasm/Research/History/BeforeActionComponentWork'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и проверка отсутствия новых пользовательских правок перед заменой.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого бинарного файла после сверки сохранённой копии и точных исходных байтов.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes();previous.unlink()
    report=dict(passed=True,typed_bytes=9,physical_records=3,existing_structure_reused='FComponent24',
        original_bytes_preserved=True,neighbor_bytes_preserved=90,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionComponentWorkClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

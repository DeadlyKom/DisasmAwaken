"""Точечная замена 72 доказанных байтов шестью физическими экземплярами, соседние 18 сохранены."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionWideVectorsData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionWideTargetStepClassification')['passed'] and read('ActionWideTargetStepVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();text,labels=facts.render(source)
    assert facts.parse(text)==(source[facts.START:facts.END],labels)
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    old=next(i for i in source_map if i['slot']==17 and i['offset']==facts.START)
    assert old['kind']=='unclassified' and old['length']==90
    previous=ROOT/old['path'];original=previous.read_bytes();assert original==source[0x3B27:0x3B81]
    suffix='Source/Resources/17_ACTION/Unclassified020_AfterWideVectors.bin'
    pieces=[dict(old,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
        (facts.START,facts.END,'typed_data',facts.PATH,0x9B27),(facts.END,0x3B81,'unclassified',suffix,None))]
    source_map[source_map.index(old):source_map.index(old)+1]=pieces
    assert not any(key in symbols for key in labels);symbols.update(labels)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.PATH:text.encode('utf-8'),ROOT/suffix:source[facts.END:0x3B81]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+previous.name+'"';assert text.count(needle)==1
    text=text.replace('                ; Unknown, соседние байты после трёх физических компонент\n'+needle,needle)
    replacement=('                disp #9B27\n                include "../Action/Data/WideVectors.asm"\n                ent\n'
        '                assert $ == #3B6F\n                ; Unknown, соседние рабочие байты после шести физических векторов\n'
        '                incbin "../Resources/17_ACTION/Unclassified020_AfterWideVectors.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка трёх физических страниц корня, включая особый старший диапазон и исходные исключения.'
    assert text.count(needle)==1 and 'wide_vector_records' not in text
    hook='''    # Проверка всех физических байтов и вложенных полей шести исходных широких векторов.
    from ActionWideVectorsData import PATH as WIDE_VECTORS, parse as parse_wide_vectors
    wide_vector_records = 0
    wide_entries = [item for item in source_map if item['path'] == WIDE_VECTORS]
    if wide_entries:
        assert len(wide_entries) == 1
        item = wide_entries[0]
        raw, labels = parse_wide_vectors((ROOT / WIDE_VECTORS).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x3B27, 72, 0x9B27)
        assert raw == sources[17][0x3B27:0x3B6F]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FACTIONWIDECOMPONENT'] == 4 and symbols['FACTIONWIDEVECTOR'] == 12
        for component in range(3):
            assert symbols['FACTIONWIDEVECTOR.COMPONENT'+str(component)] == 4*component
            for byte in range(4):
                assert symbols['FACTIONWIDEVECTOR.COMPONENT'+str(component)+'.BYTE'+str(byte)] == 4*component+byte
        wide_vector_records = 6

'''
    text=text.replace(needle,hook+needle);needle="    report['component_work_records'] = component_work_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['wide_vector_records'] = wide_vector_records").encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    # Двадцать шесть физических указателей класса до первого RET обработчиков.';assert text.count(needle)==1
    hook=('    # Шесть начальных широких векторов, байты и вложенный физический формат сохраняются.\n'
        '    from ActionWideVectorsData import PATH as WIDE_VECTORS, render as render_wide_vectors\n'
        '    text, bindings = render_wide_vectors(data_by_slot[17])\n    write(WIDE_VECTORS, text)\n    symbols.update(bindings)\n'
        '    special[17, 0x3B27] = (0x3B6F, WIDE_VECTORS, 0x9B27)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    paragraph='[WideVectors](../Source/Action/Data/WideVectors.asm) содержит шесть физических FActionWideVector по 12 байтов, каждый состоит из трёх FActionWideComponent по четыре байта. Все 72 исходных байта и little-endian порядок сохранены. Шесть записей описывают этот физический участок, допустимый игровой счётчик этим не ограничивается. См. [формат и потребители](ActionWideVectors.md).'
    path=ROOT/'Docs/DataFormats.md';pending[path]=(path.read_text('utf-8')+'\n## Физические широкие векторы ACTION\n\n'+paragraph+'\n').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/GenerateDocs.py';text=path.read_text('utf-8');line=next(v for v in text.splitlines() if '"| FComponent24 |' in v)
    row='| FActionWideVector | #0C | Три FActionWideComponent, шесть физических [WideVectors](../Source/Action/Data/WideVectors.asm), см. [ActionWideVectors](ActionWideVectors.md) |'
    pending[path]=text.replace(line,line+'\n'+line[:len(line)-len(line.lstrip())]+json.dumps(row,ensure_ascii=False)+',').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionWideVectors';history=ROOT/'Tools/Disasm/Research/History/BeforeActionWideVectors'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и проверка неизменности ручных исходников перед точечной публикацией.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого бинарного файла после проверки точной сохранённой копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes();previous.unlink()
    report=dict(passed=True,typed_bytes=72,physical_records=6,nested_structures=True,original_bytes_preserved=True,
        neighbor_bytes_preserved=18,physical_records_not_asserted_as_game_count_limit=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionWideVectorsClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

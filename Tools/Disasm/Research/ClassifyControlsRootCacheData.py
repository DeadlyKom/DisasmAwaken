"""Кандидат и защита замены одного полностью доказанного бинарного диапазона C000..C2FF."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from CheckControlsTextQueue import base_memory
import ControlsRootCacheData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionCachedRootVerification')['passed'] and read('ActionCachedRootClassification')['passed']
    source=bytes(base_memory()[0xC000:0xDADE]);raw=facts.validate(source);text,labels=facts.render(source)
    assert facts.parse(text)==(raw,labels)
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==22 and i['offset']==0)
    assert (item['length'],item['kind'])==(768,'unclassified')
    previous=ROOT/item['path'];original=previous.read_bytes();assert original==raw
    item.update(kind='typed_data',path=facts.TABLE[1],origin=0xC000)
    assert not any(key in symbols for key in labels);symbols.update(labels)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind)
        for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8')}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FRootCacheByte' not in text
    block=('\n                ; Физический байт одной из трёх плоскостей табличного корня\n'
        '                struct FRootCacheByte\n'
        'Value           db #00                                                          ; значение исходного байта, плоскость и индекс заданы именем экземпляра\n'
        '                ends\n                assert FRootCacheByte == 1\n\n')
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/22_CONTROL0.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/22_CONTROL0/'+previous.name+'"';assert text.count(needle)==1
    text=text.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'+needle,needle)
    pending[path]=text.replace(needle,'                disp #C000\n                include "../Controls/Data/RootCache.asm"\n                ent').encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка обеих физических плоскостей квадратов и всех 512 экземпляров структуры.'
    assert text.count(needle)==1 and 'root_cache_records' not in text
    hook='''    # Проверка трёх физических страниц корня, включая особый старший диапазон и исходные исключения.
    from ControlsRootCacheData import TABLE as ROOT_CACHE, parse as parse_root_cache, validate as validate_root_cache
    root_cache_records = 0
    root_cache_entries = [item for item in source_map if item['path'] == ROOT_CACHE[1]]
    if root_cache_entries:
        assert len(root_cache_entries) == 1
        item = root_cache_entries[0]
        raw, labels = parse_root_cache((ROOT / ROOT_CACHE[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (22, 0, 768, 0xC000)
        assert raw == validate_root_cache(sources[22])
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FROOTCACHEBYTE'] == 1 and symbols['FROOTCACHEBYTE.VALUE'] == 0
        root_cache_records = 768

'''
    text=text.replace(needle,hook+needle);needle="    report['square_table_records'] = square_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,"    report['root_cache_records'] = root_cache_records\n"+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1 and 'ROOT_CACHE_TABLE' not in text
    hook=('    # Буквальные исходные байты трёх страниц табличного корня, значения не пересоздаются формулой.\n'
        '    if "struct FRootCacheByte" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsRootCacheData import TABLE as ROOT_CACHE_TABLE, render as render_root_cache\n'
        '        text, bindings = render_root_cache(data_by_slot[22])\n'
        '        write(ROOT_CACHE_TABLE[1], text)\n        symbols.update(bindings)\n'
        '        special[22, 0] = (0x300, ROOT_CACHE_TABLE[1], 0xC000)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Docs/DataFormats.md';text=path.read_text('utf-8');assert 'FRootCacheByte' not in text
    row='| FRootCacheByte | #01 | 768 физических байтов трёх плоскостей корня, см. [ActionCachedRoot](ActionCachedRoot.md) |'
    pending[path]=(text+'\n## Физические страницы табличного корня\n\n| Структура | Размер | Назначение |\n|---|---|---|\n'+row+'\n').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/GenerateDocs.py';text=path.read_text('utf-8');line=next(v for v in text.splitlines() if '"| FSquareTableByte |' in v)
    pending[path]=text.replace(line,line+'\n'+line[:len(line)-len(line.lstrip())]+json.dumps(row,ensure_ascii=False)+',').encode('utf-8')
    path=ROOT/'Docs/ActionCachedRoot.md';text=path.read_text('utf-8');needle='Все 768 исходных байтов проверены.';assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+' Физические [RootCache](../Source/Controls/Data/RootCache.asm) оформлены 768 экземплярами FRootCacheByte размером один байт, поле Value имеет смещение ноль. В сборку включены буквальные значения, формула служит только проверкой.').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsRootCacheData';history=ROOT/'Tools/Disasm/Research/History/BeforeControlsRootCacheData'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата, сверка рабочей копии и сохранение каждого заменяемого файла.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только целиком заменённого бинарного файла после проверки и сохранения точной копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/22_CONTROL0').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes();previous.unlink()
    report=dict(passed=True,typed_bytes=768,physical_records=768,planes=3,records_per_plane=256,
        original_upper_rows_preserved=23,original_lower_exceptions_preserved=3,physical_bytes_preserved=True,
        formula_used_to_generate_build_data=False,sha256=hashlib.sha256(raw).hexdigest(),assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsRootCacheDataClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()

"""Замена четырёх исходных байтов ACTION физическим экземпляром без изменения окружения."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionWordRandomState as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsWordRandomVerification')['passed'] and read('ControlsWordRandomClassification')['passed']
    source = (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    disk = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    assert next(i for i in disk['entries'] if i['slot']==17)['parameter']==0x6000
    source_map, symbols, inventory = read('SourceMap'), read('Symbols'), read('Inventory')
    item = next(i for i in source_map if i['slot']==17 and i['offset']==0x3A00)
    assert (item['length'], item['kind'])==(0xE2D, 'unclassified')
    previous = ROOT/item['path']
    original = previous.read_bytes()
    assert original==source[0x3A00:0x482D]
    text, bindings = facts.render(source)
    assert facts.parse(text)==(facts.validate(source), bindings)
    assert not any(key in symbols for key in bindings)
    symbols.update(bindings)
    prefix = 'Source/Resources/17_ACTION/Unclassified020_BeforeWordRandom.bin'
    suffix = 'Source/Resources/17_ACTION/Unclassified020_AfterWordRandom.bin'
    pieces = [dict(slot=17, offset=start, length=end-start, kind=kind, path=path, origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start, end, kind, path, origin in (
        (0x3A00, 0x3B15, 'unclassified', prefix, None),
        (0x3B15, 0x3B19, 'typed_data', facts.TABLE[1], 0x9B15),
        (0x3B19, 0x482D, 'unclassified', suffix, None))]
    index = source_map.index(item)
    source_map[index:index+1] = pieces
    inventory['ranges_by_kind'] = dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(i['length'] for i in source_map if i['kind']==kind)
                                         for kind in inventory['ranges_by_kind']}
    pending = {ROOT/facts.TABLE[1]: text.encode('utf-8'), ROOT/prefix: source[0x3A00:0x3B15],
               ROOT/suffix: source[0x3B19:0x482D]}
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')] = encode(value)
    path = ROOT/'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    assert 'struct FWordRandomState' not in text
    block = ('\n                ; Физическое двухсловное состояние генератора ACTION\n'
        '                struct FWordRandomState\n'
        'First           dw #0000                                                        ; получает прежнее Second\n'
        'Second          dw #0000                                                        ; результат смешивающей рекурсии\n'
        '                ends\n                assert FWordRandomState == 4\n\n')
    pending[path] = text.replace('                endif', block+'                endif').encode('utf-8')
    path = ROOT/'Source/Files/17_ACTION.inc'
    text = path.read_text('utf-8')
    needle = '                incbin "../Resources/17_ACTION/Unclassified020_Suffix.bin"'
    assert text.count(needle)==1
    replacement = ('                incbin "../Resources/17_ACTION/Unclassified020_BeforeWordRandom.bin"\n'
        '                assert $ == #3B15\n                disp #9B15\n'
        '                include "../Action/Data/WordRandomState.asm"\n                ent\n'
        '                assert $ == #3B19\n                ; Unknown, исходные байты после состояния генератора\n'
        '                incbin "../Resources/17_ACTION/Unclassified020_AfterWordRandom.bin"')
    pending[path] = text.replace(needle, replacement).encode('utf-8')
    path = ROOT/'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook = ('    # Четыре исходных байта двухсловного генератора ACTION.\n'
        '    if "struct FWordRandomState" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ActionWordRandomState import TABLE as WORD_RANDOM_STATE, render as render_word_random\n'
        '        text, bindings = render_word_random(data_by_slot[17])\n'
        '        write(WORD_RANDOM_STATE[1], text)\n        symbols.update(bindings)\n'
        '        special[17, 0x3B15] = (0x3B19, WORD_RANDOM_STATE[1], 0x9B15)\n')
    pending[path] = text.replace(needle, hook+needle).encode('utf-8')
    path = ROOT/'Tools/Disasm/VerifySources.py'
    text = path.read_text('utf-8')
    needle = '    # Проверка обеих физических плоскостей квадратов и всех 512 экземпляров структуры.'
    assert text.count(needle)==1
    hook = '''    # Проверка двух физических слов состояния генератора ACTION.
    from ActionWordRandomState import TABLE as WORD_RANDOM, parse as parse_word_random
    word_random_records = 0
    entries = [item for item in source_map if item['path'] == WORD_RANDOM[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_word_random((ROOT/WORD_RANDOM[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x3B15, 4, 0x9B15)
        assert raw == sources[17][0x3B15:0x3B19]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FWORDRANDOMSTATE'] == 4
        assert symbols['FWORDRANDOMSTATE.FIRST'] == 0 and symbols['FWORDRANDOMSTATE.SECOND'] == 2
        word_random_records = 1

'''
    text = text.replace(needle, hook+needle)
    needle = "    report['action_sine_records'] = action_sine_records"
    assert text.count(needle)==1
    pending[path] = text.replace(needle, needle+"\n    report['word_random_records'] = word_random_records").encode('utf-8')
    candidate = ROOT/'Tools/Disasm/Research/Candidates/ActionWordRandomState'
    history = ROOT/'Tools/Disasm/Research/History/BeforeActionWordRandomState'
    assert not candidate.exists() and not history.exists()
    # Создание отдельного кандидата и проверка отсутствия новых пользовательских изменений.
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for path, before, after in plan:
        target = candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    for path, before, after in plan:
        assert path.read_bytes()==before if before is not None else not path.exists()
    for path, before in {**{p: b for p, b, _ in plan if b is not None}, previous: original}.items():
        target = history/path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(before)
    for path, before, after in plan:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    # Удаление только заменённого ресурса после проверки сохранённой исходной копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report = dict(passed=True, typed_bytes=4, physical_records=1, structure='FWordRandomState',
        logical_file_offset=0x3B15, runtime_address=0x9B15, physical_bytes_preserved=True, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionWordRandomStateClassification.json').write_bytes(encode(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

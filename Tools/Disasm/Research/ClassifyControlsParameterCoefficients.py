"""Типизация пятнадцати исходных правил формирования параметров, перекрытие шаблона сохранено."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ControlsParameterCoefficients as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsParameterTablesVerification')['passed']
    source = (ROOT/'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()
    disk = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    assert next(i for i in disk['entries'] if i['slot']==23)['length']==len(source)
    source_map, symbols, inventory = read('SourceMap'), read('Symbols'), read('Inventory')
    item = next(i for i in source_map if i['slot']==23 and i['offset']==0x3FE)
    assert (item['length'], item['kind'])==(325, 'unclassified')
    previous = ROOT/item['path']
    original = previous.read_bytes()
    assert original==source[0x3FE:0x543]
    text, bindings = facts.render(source)
    assert facts.parse(text)==(facts.validate(source), bindings)
    assert not any(key in symbols for key in bindings)
    symbols.update(bindings)
    prefix = 'Source/Resources/23_CONTROL/Unclassified003_BeforeCoefficients.bin'
    suffix = 'Source/Resources/23_CONTROL/Unclassified003_AfterCoefficients.bin'
    pieces = [dict(slot=23, offset=start, length=end-start, kind=kind, path=path, origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start, end, kind, path, origin in (
        (0x3FE, 0x486, 'unclassified', prefix, None),
        (0x486, 0x4B3, 'typed_data', facts.TABLE[1], 0xDF64),
        (0x4B3, 0x543, 'unclassified', suffix, None))]
    index = source_map.index(item)
    source_map[index:index+1] = pieces
    inventory['ranges_by_kind'] = dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(i['length'] for i in source_map if i['kind']==kind)
                                         for kind in inventory['ranges_by_kind']}
    pending = {ROOT/facts.TABLE[1]: text.encode('utf-8'), ROOT/prefix: source[0x3FE:0x486],
               ROOT/suffix: source[0x4B3:0x543]}
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')] = encode(value)
    path = ROOT/'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    assert 'struct FParameterCoefficient' not in text
    block = '\n                ; Физическое правило формирования одного байта параметра\n                struct FParameterCoefficient\n'
    for name,width,note in facts.FIELDS:
        block += name.ljust(16)+('db #00').ljust(64)+'; '+note+'\n'
    block += '                ends\n                assert FParameterCoefficient == 3\n\n'
    pending[path] = text.replace('                endif',block+'                endif').encode('utf-8')
    path = ROOT/'Source/Files/23_CONTROL.inc'
    text = path.read_text('utf-8')
    needle = '                incbin "../Resources/23_CONTROL/Unclassified003.bin"'
    assert text.count(needle)==1
    replacement = ('                incbin "../Resources/23_CONTROL/Unclassified003_BeforeCoefficients.bin"\n'
        '                assert $ == #0486\n                disp #DF64\n'
        '                include "../Controls/Data/ParameterCoefficients.asm"\n                ent\n'
        '                assert $ == #04B3\n                ; Unknown, исходные байты после правил параметров\n'
        '                incbin "../Resources/23_CONTROL/Unclassified003_AfterCoefficients.bin"')
    pending[path] = text.replace(needle, replacement).encode('utf-8')
    path = ROOT/'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook = ('    # Исходные трёхбайтовые правила параметров, перекрытые шаблонные чтения сохраняются.\n'
        '    if "struct FParameterCoefficient" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsParameterCoefficients import TABLE as PARAMETER_COEFFICIENTS, render as render_parameter_coefficients\n'
        '        text, bindings = render_parameter_coefficients(data_by_slot[23])\n'
        '        write(PARAMETER_COEFFICIENTS[1], text)\n        symbols.update(bindings)\n'
        '        special[23, 0x486] = (0x4B3, PARAMETER_COEFFICIENTS[1], 0xDF64)\n')
    pending[path] = text.replace(needle, hook+needle).encode('utf-8')
    path = ROOT/'Tools/Disasm/VerifySources.py'
    text = path.read_text('utf-8')
    needle = '    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    assert text.count(needle)==1
    hook = """    # Проверка пятнадцати физических правил формирования параметров.
    from ControlsParameterCoefficients import TABLE as PARAMETER_RULES, parse as parse_parameter_rules
    parameter_rule_records = 0
    entries = [item for item in source_map if item['path'] == PARAMETER_RULES[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_parameter_rules((ROOT/PARAMETER_RULES[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (23, 0x486, 45, 0xDF64)
        assert raw == sources[23][0x486:0x4B3]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FPARAMETERCOEFFICIENT'] == 3
        assert [symbols['FPARAMETERCOEFFICIENT.'+name.upper()] for name,_,_ in PARAMETER_RULES[5]] == [0,1,2]
        parameter_rule_records = 15

"""
    text = text.replace(needle,hook+needle)
    needle = "    report['circle_work_records'] = circle_work_records"
    assert text.count(needle)==1
    pending[path] = text.replace(needle,needle+"\n    report['parameter_rule_records'] = parameter_rule_records").encode('utf-8')
    candidate = ROOT/'Tools/Disasm/Research/Candidates/ControlsParameterCoefficients'
    history = ROOT/'Tools/Disasm/Research/History/BeforeControlsParameterCoefficients'
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
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/23_CONTROL').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report = dict(passed=True,typed_bytes=45,physical_records=15,structure='FParameterCoefficient',
        logical_file_offset=0x486,runtime_address=0xDF64,overlapping_h4_template_preserved=True,
        physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsParameterCoefficientsClassification.json').write_bytes(encode(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

"""Физические 12 байтов исходной рабочей записи, без переноса и без экспорта поверх исходников."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from CheckControlsTextQueue import base_memory
import ControlsCircleWork as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for tag in ('ControlsCircleSetup', 'ControlsCircleSpan', 'ControlsSquares', 'ControlsRasterStep'):
        assert read(tag+'Verification')['passed'] and read(tag+'Classification')['passed']
    source = bytes(base_memory()[0xC000:0xDADE])
    source_map, symbols, inventory = read('SourceMap'), read('Symbols'), read('Inventory')
    item = next(i for i in source_map if i['slot']==22 and i['offset']==0x1181)
    assert (item['length'], item['kind']) == (12, 'unclassified')
    previous = ROOT/item['path']
    original = previous.read_bytes()
    assert original == source[0x1181:0x118D] == bytes(12)
    text, labels = facts.render(source)
    assert facts.parse(text) == (original, labels)
    assert not any(key in symbols for key in labels)
    symbols.update(labels)
    item.update(kind='typed_data', path=facts.TABLE[1], origin=0xD181,
                sha256=hashlib.sha256(original).hexdigest())
    inventory['ranges_by_kind'] = dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(i['length'] for i in source_map if i['kind']==kind)
                                         for kind in inventory['ranges_by_kind']}
    pending = {ROOT/facts.TABLE[1]: text.encode('utf-8')}
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')] = encode(value)
    path = ROOT/'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    assert 'struct FCircleRasterWork' not in text
    block = '\n                ; Физическая рабочая запись большого контура, исходное размещение сохранено\n                struct FCircleRasterWork\n'
    offset = 0
    for name, width, note in facts.FIELDS:
        block += name.ljust(16)+('db #00' if width==1 else 'dw #0000').ljust(64)+'; '+note+'\n'
        offset += width
    assert offset == 12
    block += '                ends\n                assert FCircleRasterWork == 12\n\n'
    pending[path] = text.replace('                endif', block+'                endif').encode('utf-8')
    path = ROOT/'Source/Files/22_CONTROL0.inc'
    text = path.read_text('utf-8')
    needle = ('                ; Unknown, следующие 12 рабочих байтов сохраняются отдельно\n'
              '                incbin "../Resources/22_CONTROL0/Unclassified004_AfterProjection.bin"')
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, '                disp #D181\n'
        '                include "../Controls/Data/CircleWork.asm"\n                ent').encode('utf-8')
    path = ROOT/'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle) == 1
    hook = ('    # Физическая рабочая запись, сохранение исходного порядка и байтов.\n'
        '    if "struct FCircleRasterWork" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsCircleWork import TABLE as CIRCLE_WORK, render as render_circle_work\n'
        '        text, bindings = render_circle_work(data_by_slot[22])\n'
        '        write(CIRCLE_WORK[1], text)\n        symbols.update(bindings)\n'
        '        special[22, 0x1181] = (0x118D, CIRCLE_WORK[1], 0xD181)\n')
    pending[path] = text.replace(needle, hook+needle).encode('utf-8')
    path = ROOT/'Tools/Disasm/VerifySources.py'
    text = path.read_text('utf-8')
    needle = '    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    assert text.count(needle) == 1
    hook = '''    # Проверка каждого поля физической рабочей записи большого контура.
    from ControlsCircleWork import TABLE as CIRCLE_WORK, parse as parse_circle_work
    circle_work_records = 0
    entries = [item for item in source_map if item['path'] == CIRCLE_WORK[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_circle_work((ROOT/CIRCLE_WORK[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (22, 0x1181, 12, 0xD181)
        assert raw == sources[22][0x1181:0x118D]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FCIRCLERASTERWORK'] == 12
        offset = 0
        for name, width, _ in CIRCLE_WORK[5]:
            assert symbols['FCIRCLERASTERWORK.'+name.upper()] == offset
            offset += width
        circle_work_records = 1

'''
    text = text.replace(needle, hook+needle)
    needle = "    report['body_projection_records'] = body_projection_records"
    assert text.count(needle) == 1
    text = text.replace(needle, needle+"\n    report['circle_work_records'] = circle_work_records")
    pending[path] = text.encode('utf-8')
    candidate = ROOT/'Tools/Disasm/Research/Candidates/ControlsCircleWork'
    history = ROOT/'Tools/Disasm/Research/History/BeforeControlsCircleWork'
    assert not candidate.exists() and not history.exists()
    # Создание отдельного кандидата до проверки отсутствия новых ручных правок.
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
    # Удаление только заменённого ресурса после проверки его точной сохранённой копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/22_CONTROL0').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    result = dict(passed=True, typed_bytes=12, physical_records=1, structure='FCircleRasterWork',
        physical_bytes_preserved=True, mode_full_game_meaning_proved=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsCircleWorkClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

"""Физическая точка и два звуковых потока назначения цели, соседние байты сохраняются."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionAyStreams as streams
import ActionAimPointData as point


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    proof = read('ActionAyStreamPlaybackVerification')
    assert proof['passed'] and (proof['streams'], proof['sequences'], proof['ticks']) == (7, 42, 570)
    assert read('ActionAimFollowVerification')['passed']
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map, symbols, inventory = [read(n) for n in ('SourceMap', 'Symbols', 'Inventory')]
    point_old = next(i for i in source_map if i['slot'] == 17 and i['offset'] == 0x3B19)
    gap_old = next(i for i in source_map if i['slot'] == 17 and i['offset'] == 0x8DC1)
    assert point_old['length'] == 2 and gap_old['length'] == 140
    removed = {}
    for old in (point_old, gap_old):
        assert old['kind'] == 'unclassified'
        path = ROOT / old['path']
        removed[path] = path.read_bytes()
        assert removed[path] == source[old['offset']:old['offset'] + old['length']]
    pending = {}

    def piece(start, end, path, typed):
        return dict(slot=17, offset=start, length=end - start, kind='typed_data' if typed else 'unclassified', path=path,
                    origin=start + 0x6000 if typed else None, sha256=hashlib.sha256(source[start:end]).hexdigest())
    text, labels = point.render(source)
    assert point.parse(text) == (source[0x3B19:0x3B1B], labels)
    assert not set(symbols) & set(labels)
    symbols.update(labels)
    pending[ROOT / point.PATH] = text.encode('utf-8')
    source_map[source_map.index(point_old)] = piece(0x3B19, 0x3B1B, point.PATH, True)
    path, selected = streams.GROUPS[2]
    text, labels = streams.render(source, selected)
    start, end = streams.bounds(selected)
    assert (start, end) == (0x8E02, 0x8E34) and streams.parse(text, selected) == (source[start:end], labels)
    assert not set(symbols) & set(labels)
    symbols.update(labels)
    pending[ROOT / path] = text.encode('utf-8')
    pieces = [(0x8DC1, 0x8E02, 'Source/Resources/17_ACTION/Unclassified044_BeforeCaptureStreams.bin', False),
              (start, end, path, True),
              (0x8E34, 0x8E4D, 'Source/Resources/17_ACTION/Unclassified044_AfterCaptureStreams.bin', False)]
    for begin, finish, relative, typed in pieces:
        if not typed:
            pending[ROOT / relative] = source[begin:finish]
    index = source_map.index(gap_old)
    source_map[index:index + 1] = [piece(*p) for p in pieces]
    inventory['ranges_by_kind'] = dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(i['length'] for i in source_map if i['kind'] == kind) for kind in inventory['ranges_by_kind']}
    for stem, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[ROOT / ('Tools/Disasm/Reports/' + stem + '.json')] = encode(value)
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    assert 'struct FActionAimPoint' not in text
    pending[path] = text.replace('                endif', point.structure_text() + '\n                endif').encode('utf-8')
    path = ROOT / 'Source/Files/17_ACTION.inc'
    text = path.read_text('utf-8')
    needle = '                incbin "../Resources/17_ACTION/' + (ROOT / point_old['path']).name + '"'
    assert text.count(needle) == 1
    text = text.replace(needle, '                disp #9B19\n                include "../Action/Data/AimPoint.asm"\n                ent')
    needle = '                incbin "../Resources/17_ACTION/' + (ROOT / gap_old['path']).name + '"'
    assert text.count(needle) == 1
    lines = []
    for begin, finish, relative, typed in pieces:
        lines.append('                assert $ == #' + format(begin, '04X'))
        if typed:
            lines += ['                disp #' + format(begin + 0x6000, '04X'), '                include "../Action/Data/' + relative.rsplit('/', 1)[-1] + '"', '                ent']
        else:
            lines += ['                ; Unknown, соседние байты вне доказанных потоков назначения цели', '                incbin "../Resources/17_ACTION/' + relative.rsplit('/', 1)[-1] + '"']
    pending[path] = text.replace(needle, '\n'.join(lines)).encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text('utf-8')
    needle = '    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    assert text.count(needle) == 1
    hook = '''    # Проверка двух исходных байтов сопровождающей точки и физических полей X/Y.
    from ActionAimPointData import PATH as AIM_POINT_PATH, parse as parse_aim_point
    aim_records=[i for i in source_map if i['path']==AIM_POINT_PATH]
    assert len(aim_records)==1
    aim_item=aim_records[0]
    assert (aim_item['slot'],aim_item['offset'],aim_item['length'],aim_item['origin'])==(17,0x3B19,2,0x9B19)
    aim_raw,aim_labels=parse_aim_point((ROOT/AIM_POINT_PATH).read_text('utf-8'))
    assert aim_raw==sources[17][0x3B19:0x3B1B]
    assert all(symbols.get(k.upper())==v for k,v in aim_labels.items())
    assert (symbols['FACTIONAIMPOINT'],symbols['FACTIONAIMPOINT.X'],symbols['FACTIONAIMPOINT.Y'])==(2,0,1)

'''
    pending[path] = text.replace(needle, hook + needle).encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle) == 1
    hook = '''    # Физическая двухбайтовая точка с доказанными потребителями, X перед Y.
    if "struct FActionAimPoint" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionAimPointData import PATH as AIM_POINT_PATH, render as render_aim_point
        text,bindings=render_aim_point(data_by_slot[17])
        write(AIM_POINT_PATH,text)
        symbols.update(bindings)
        special[17,0x3B19]=(0x3B1B,AIM_POINT_PATH,0x9B19)
'''
    pending[path] = text.replace(needle, hook + needle).encode('utf-8')
    # Создание отдельного кандидата и точной истории, старые ресурсы удаляются лишь после полной проверки.
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionAimData'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionAimData'
    assert not candidate.exists() and not history.exists()
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for path, before, after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    for path, before, after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path, before in {**{p: b for p, b, _ in plan if b is not None}, **removed}.items():
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(before)
    for path, before, after in plan:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for path, before in removed.items():
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources/17_ACTION').resolve())
        assert path.read_bytes() == before == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    report = dict(passed=True, physical_point_bytes=2, point_initial_xy=[119, 43], new_sound_frames=12,
                  new_sound_markers=2, new_sound_bytes=50, original_bytes_preserved=True, unclassified_neighbor_sound_bytes=383,
                  sequences=42, ticks=570, actual_ay_hardware_executed=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionAimDataClassification.json').write_bytes(encode(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

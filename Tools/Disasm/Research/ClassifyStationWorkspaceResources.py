"""Публикация исходных байтов рабочих страниц через отдельный кандидат."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import json
import sys

from CheckIntro import ROOT


RESOURCES = (
    (0x2238, 0x2300, 'Source/Station/Resources/InitialRowHighTail.bin', 'INITIAL_STATION_ROW_HIGH',
     'исходный хвост страницы 82 до построения старших байтов экранных строк'),
    (0x2300, 0x2400, 'Source/Station/Resources/InitialRowLow.bin', 'INITIAL_STATION_ROW_LOW',
     'исходная страница 83 до построения младших байтов экранных строк'),
    (0x2400, 0x2500, 'Source/Station/Resources/InitialColumnByte.bin', 'INITIAL_STATION_COLUMN_BYTE',
     'исходная страница 84 до построения байтовых столбцов'),
    (0x2600, 0x2900, 'Source/Station/Resources/InitialCellOwners.bin', 'INITIAL_STATION_CELL_OWNERS',
     'исходные 768 байтов карты владельцев до очистки в RebuildInterface'),
)


def publish(*, slot, origin, ranges, resources, tag, resource_module, resource_name, proof):
    sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
    from VerifySources import main as verify

    def check_sources():
        with redirect_stdout(StringIO()):
            verify()

    check_sources()
    reports = ROOT / 'Tools/Disasm/Reports'

    def read(name):
        return json.loads((reports / (name + '.json')).read_bytes())

    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    sm, inventory = read('SourceMap'), read('Inventory')
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry = next(entry for entry in manifest['entries'] if entry['slot'] == slot)
    source = (ROOT / (entry['path'] + '.bin')).read_bytes()
    include = next((ROOT / 'Source/Files').glob(f'{slot:02d}_*.inc'))
    text = include.read_text('utf-8')
    pending = {}
    removed = {}
    for start, end in ranges:
        old = next(row for row in sm if row['slot'] == slot and row['offset'] == start)
        assert old['kind'] == 'unclassified' and old['length'] == end - start
        path = ROOT / old['path']
        assert path.read_bytes() == source[start:end]
        removed[path] = path.read_bytes()
        pieces = []
        lines = []
        for first, last, filename, kind, note in resources:
            if not start <= first < last <= end:
                continue
            target = ROOT / filename
            assert not target.exists()
            raw = source[first:last]
            pending[target] = raw
            row = dict(slot=slot, offset=first, length=len(raw), path=filename,
                       sha256=sha256(raw).hexdigest())
            if kind is None:
                row.update(kind='unclassified', origin=None)
            else:
                row.update(kind='binary_resource', origin=origin + first, format=kind)
            pieces.append(row)
            lines.extend((f'                assert $ == #{first:04X}', f'                ; {note}',
                          '                incbin "../' + filename[7:] + '"'))
        assert b''.join(pending[ROOT / row['path']] for row in pieces) == removed[path]
        sm[sm.index(old):sm.index(old) + 1] = pieces
        needle = '                incbin "../' + old['path'][7:] + '"'
        source_lines = text.splitlines()
        assert source_lines.count(needle) == 1
        index = source_lines.index(needle)
        first_line = index - 1
        if source_lines[first_line].startswith('                ; '):
            first_line -= 1
        assert source_lines[first_line] == f'                assert $ == #{start:04X}'
        source_lines[first_line:index + 1] = lines
        text = '\n'.join(source_lines) + '\n'
    modified = read('ModifiedCode')
    changed_modified = False
    for item in modified:
        if 'target_path' not in item or ROOT / item['target_path'] not in removed:
            continue
        assert item['target_slot'] == slot
        row = next(row for row in sm if row['slot'] == slot
                   and row['offset'] <= item['target_offset'] < row['offset'] + row['length'])
        item['target_path'] = row['path']
        item['target_source_classified'] = row['kind'] != 'unclassified'
        changed_modified = True
    if changed_modified:
        pending[reports / 'ModifiedCode.json'] = encode(modified)
    pending[include] = text.encode('utf-8')
    inventory['ranges_by_kind'] = dict(Counter(row['kind'] for row in sm))
    inventory['physical_bytes_by_kind'] = {
        kind: sum(row['length'] for row in sm if row['kind'] == kind) for kind in inventory['ranges_by_kind']
    }
    pending[reports / 'SourceMap.json'] = encode(sm)
    pending[reports / 'Inventory.json'] = encode(inventory)
    exporter = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = exporter.read_text('utf-8')
    needle = '    # Тексты панелей банка станции, исходные управляющие коды и написание сохраняются.'
    assert text.count(needle) == 1
    hook = (f'    from {resource_module} import RESOURCES as {resource_name}\n'
            f'    for start,end,path,kind,_ in {resource_name}:\n'
            f'        if kind is not None:binary_resources[{slot},start]=(end,path,kind)\n\n')
    pending[exporter] = text.replace(needle, hook + needle).encode('utf-8')

    candidate = ROOT / 'Tools/Disasm/Research/Candidates' / tag
    history = ROOT / 'Tools/Disasm/Research/History' / ('Before' + tag)
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in pending}
    for path, after in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    for path, raw in {**before, **removed}.items():
        if raw is None:
            assert not path.exists()
            continue
        assert path.read_bytes() == raw
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, after in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
    check_sources()
    for path, raw in removed.items():
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == raw == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    known = [item for item in resources if item[3] is not None]
    result = dict(passed=True, classified_resource_bytes=sum(end - start for start, end, *_ in known),
                  resources=len(known), **proof, original_bytes_preserved=True,
                  generated_values_not_serialized=True, assembly_executed=False)
    (reports / (tag + 'Classification.json')).write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    report = ROOT / 'Tools/Disasm/Reports/StationInitialWorkspaceVerification.json'
    proof = json.loads(report.read_bytes())
    assert proof['passed'] and not proof['workspace_instructions_executed']
    assert [proof['first_write_groups'][name]['bytes'] for name in
            ('row_high_tail', 'row_low', 'column', 'cell_owners')] == [200, 256, 256, 768]
    publish(slot=4, origin=0x6000, ranges=((0x2238, 0x2500), (0x2600, 0x2900)),
            resources=RESOURCES, tag='StationInitialWorkspace',
            resource_module='ClassifyStationWorkspaceResources', resource_name='STATION_INITIAL_STORAGE',
            proof=dict(original_index_pair_bytes_checked_separately=256))

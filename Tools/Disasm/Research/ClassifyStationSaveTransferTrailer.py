"""Публикация одного хвоста состояния в STATIONF и шести файлах SAVE."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import json
import sys

from CheckStationSaveTransferTrailer import FORMAT, REPORT, ROOT, SAVE_OFFSET, SIZE, STATION_OFFSET
from SavedStateLayout import SLOTS


RESOURCES = (
    (4, STATION_OFFSET, STATION_OFFSET + SIZE, 'Source/Station/Resources/InitialTransferTrailer.bin'),
    *((slot, SAVE_OFFSET, SAVE_OFFSET + SIZE,
       f'Source/Resources/{slot}_{name}/InitialTransferTrailer.bin') for slot, name in SLOTS),
)
TAG = 'StationSaveTransferTrailer'


def main():
    sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
    from VerifySources import main as verify

    with redirect_stdout(StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    proof = json.loads((reports / (REPORT + '.json')).read_bytes())
    assert proof['passed'] and proof['trailer_size'] == SIZE
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entries = {entry['slot']: entry for entry in manifest['entries']}
    source_map = json.loads((reports / 'SourceMap.json').read_bytes())
    inventory = json.loads((reports / 'Inventory.json').read_bytes())
    pending = {}
    removed = {}
    for slot, start, end, name in RESOURCES:
        old = next(row for row in source_map if row['slot'] == slot and row['offset'] == start)
        old_end = start + old['length']
        assert old['kind'] == 'unclassified' and old_end >= end
        old_path = ROOT / old['path']
        raw = old_path.read_bytes()
        original = (ROOT / (entries[slot]['path'] + '.bin')).read_bytes()
        assert raw == original[start:old_end] and raw[:SIZE] == bytes(SIZE)
        removed[old_path] = raw
        pieces = [dict(old, length=SIZE, kind='binary_resource', path=name,
                       origin=0x6000 + start if slot == 4 else None,
                       format=FORMAT, sha256=sha256(raw[:SIZE]).hexdigest())]
        pending[ROOT / name] = raw[:SIZE]
        new_lines = ['                ; Хвост исходного состояния перед переносом в ACTION',
                     f'                incbin "../{name[7:]}"']
        if old_end > end:
            assert slot == 4
            remainder = f'Source/Resources/04_STATIONF/Unclassified{end:04X}_{old_end:04X}.bin'
            pending[ROOT / remainder] = raw[SIZE:]
            pieces.append(dict(old, offset=end, length=old_end - end, path=remainder,
                               sha256=sha256(raw[SIZE:]).hexdigest()))
            new_lines.extend((f'                assert $ == #{end:04X}',
                              '                ; Unknown, продолжение находится за границей переноса состояния',
                              f'                incbin "../{remainder[7:]}"'))
        source_map[source_map.index(old):source_map.index(old) + 1] = pieces
        unit = next((ROOT / 'Source/Files').glob(f'{slot:02}_*.inc'))
        lines = unit.read_text('utf-8').splitlines()
        needle = f'                incbin "../{old["path"][7:]}"'
        assert lines.count(needle) == 1
        index = lines.index(needle)
        boundary = f'                assert $ == #{start:04X}'
        if slot == 4:
            assert lines[index - 2] == boundary and lines[index - 1].startswith('                ; Unknown')
            lines[index - 1:index + 1] = new_lines
        else:
            assert lines[index - 1] == boundary and lines[index - 2].startswith('                ; Неизвестные')
            lines[index - 2:index + 1] = [boundary, *new_lines]
        pending[unit] = ('\n'.join(lines) + '\n').encode('utf-8')

    inventory['ranges_by_kind'] = dict(Counter(row['kind'] for row in source_map))
    sizes = Counter()
    for row in source_map:
        sizes[row['kind']] += row['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    exporter = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = exporter.read_text('utf-8')
    marker = '    # Тексты панелей банка станции, исходные управляющие коды и написание сохраняются.'
    assert text.count(marker) == 1
    hook = ('    from ClassifyStationSaveTransferTrailer import RESOURCES as SAVE_TRAILER_RESOURCES, FORMAT as SAVE_TRAILER_FORMAT\n'
            '    for slot,start,end,path in SAVE_TRAILER_RESOURCES:\n'
            '        binary_resources[slot,start]=(end,path,SAVE_TRAILER_FORMAT)\n\n')
    pending[exporter] = text.replace(marker, hook + marker).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates' / TAG
    history = ROOT / 'Tools/Disasm/Research/History' / ('Before' + TAG)
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in pending}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, raw in {**before, **removed}.items():
        if raw is None:
            assert not path.exists()
            continue
        assert path.read_bytes() == raw
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    with redirect_stdout(StringIO()):
        verify()
    for path, raw in removed.items():
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == raw == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    result = dict(passed=True, resources=len(RESOURCES), original_bytes=len(RESOURCES) * SIZE,
                  old_image_bytes_preserved=True, gameplay_fields_proved=False, assembly_executed=False)
    (reports / (TAG + 'Classification.json')).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

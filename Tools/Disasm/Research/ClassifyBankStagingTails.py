"""Публикация хвостов фиксированного LDIR по подтверждённым диапазонам."""

from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import json
import sys

from Analyze import payload
from BankStagingTails import FORMAT, RANGES, path_for, split_gap
from CheckIntro import ROOT


def main():
    sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
    from VerifySources import main as verify

    def check():
        with redirect_stdout(StringIO()):
            verify()

    def encode(data):
        return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    check()
    reports = ROOT / 'Tools/Disasm/Reports'
    source_map = json.loads((reports / 'SourceMap.json').read_bytes())
    inventory = json.loads((reports / 'Inventory.json').read_bytes())
    proof = json.loads((reports / 'BankStripArchiveConsumerVerification.json').read_bytes())
    assert proof['passed'] and {row['slot']: (row['start'], row['end_exclusive'])
                                for row in proof['staging_tail_checks']} == RANGES
    pending, removed = {}, {}
    for slot, (begin, end) in RANGES.items():
        data = payload(slot)
        old = next(row for row in source_map if row['slot'] == slot and row['offset'] == begin)
        if old['kind'] == 'binary_resource':
            assert (old['length'], old['path'], old['format']) == (end - begin, path_for(slot), FORMAT)
            assert (ROOT / old['path']).read_bytes() == data[begin:end]
            continue
        assert old['kind'] == 'unclassified'
        old_path = ROOT / old['path']
        original = old_path.read_bytes()
        assert original == data[begin:begin + old['length']]
        removed[old_path] = original
        lines = ['                ; Документация [чтения за концом полосы](../../Docs/BankStripArchiveConsumer.md)']
        rows = []
        for first, length, kind, path in split_gap(slot, begin, old['length']):
            target = ROOT / path
            assert not target.exists()
            blob = data[first:first + length]
            pending[target] = blob
            row = dict(slot=slot, offset=first, length=length, kind=kind, path=path,
                       origin=None, sha256=sha256(blob).hexdigest())
            if kind == 'binary_resource':
                assert first + length == end
                row['format'] = FORMAT
                note = 'Исходные байты, которые фиксированный LDIR читает за концом растра полосы'
            else:
                note = 'Unknown, дальнейшие чтения промежутка этой трассой не установлены'
            rows.append(row)
            lines.extend((f'                assert $ == #{first:04X}', '                ; ' + note,
                          '                incbin "../' + path[7:] + '"'))
        assert b''.join(pending[ROOT / row['path']] for row in rows) == original
        source_map[source_map.index(old):source_map.index(old) + 1] = rows
        include = ROOT / f'Source/Files/{slot}_BANK{slot - 33}.inc'
        text = include.read_text('utf-8')
        needle = '                incbin "../' + old['path'][7:] + '"'
        assert text.count(needle) == 1
        pending[include] = text.replace(needle, '\n'.join(lines)).encode('utf-8')
    modified = json.loads((reports / 'ModifiedCode.json').read_bytes())
    assert all(ROOT / row['target_path'] not in removed for row in modified if row.get('target_path'))
    inventory['ranges_by_kind'] = dict(Counter(row['kind'] for row in source_map))
    inventory['physical_bytes_by_kind'] = {
        kind: sum(row['length'] for row in source_map if row['kind'] == kind)
        for kind in inventory['ranges_by_kind']
    }
    pending[reports / 'SourceMap.json'] = encode(source_map)
    pending[reports / 'Inventory.json'] = encode(inventory)
    research = ROOT / 'Tools/Disasm/Research'
    if removed:
        suffix = ''.join(path.stem for path in pending if path.suffix == '.inc')
        candidate = research / 'Candidates' / ('BankStagingTails' + suffix)
        history = research / 'History' / ('BeforeBankStagingTails' + suffix)
        assert not candidate.exists() and not history.exists()
    else:
        return
    before = {path: path.read_bytes() if path.exists() else None for path in pending}
    for path, blob in pending.items():
        assert path.resolve().is_relative_to(ROOT.resolve())
        copy = candidate / path.relative_to(ROOT)
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(blob)
    for path, blob in {**before, **removed}.items():
        assert path.read_bytes() == blob if blob is not None else not path.exists()
        if blob is not None:
            copy = history / path.relative_to(ROOT)
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_bytes(blob)
    for path, blob in pending.items():
        path.write_bytes(blob)
    check()
    for path, blob in removed.items():
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == blob == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    result = dict(passed=True, resources=len(RANGES), bytes=sum(end - begin for begin, end in RANGES.values()),
                  raw_bytes_preserved=True, runtime_read_proved=True,
                  game_entry_proved=False, assembly_executed=False)
    (reports / 'BankStagingTailsClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

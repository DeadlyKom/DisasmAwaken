"""Заменяет исходный бинарный средний контекст теми же байтами в станционных структурах."""

from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
import json
import sys

from ActionContextMapRecords import END, ORIGIN, PATH, START, render
from Analyze import payload
from CheckIntro import ROOT


def main():
    sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
    from VerifySources import main as verify

    reports = ROOT / 'Tools/Disasm/Reports'

    def read(name):
        return json.loads((reports / (name + '.json')).read_bytes())

    def encode(data):
        return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    with redirect_stdout(StringIO()):
        verify()
    transfer = read('StationHyperJumpCostTransferVerification')
    assert transfer['passed'] and transfer['whole_512_byte_copy_checked']
    assert transfer['original_distance_arithmetic_and_both_state_copies_executed']
    raw = payload(17)
    text, labels, differences = render(raw, payload(4))
    source_map = read('SourceMap')
    row = next(row for row in source_map if row['slot'] == 17 and row['offset'] == START)
    assert row['format'] == 'INITIAL_ACTION_CONTEXT_MIDDLE' and row['length'] == END - START
    previous_path = ROOT / row['path']
    previous_data = previous_path.read_bytes()
    assert previous_data == raw[START:END]
    assert all(item.get('target_path') != row['path'] for item in read('ModifiedCode'))
    row.update(kind='typed_data', path=PATH, origin=ORIGIN + START)
    del row['format']
    symbols = read('Symbols')
    assert not set(labels) & set(symbols)
    symbols.update(labels)
    inventory = read('Inventory')
    inventory['ranges_by_kind'] = dict(Counter(row['kind'] for row in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(row['length'] for row in source_map if row['kind'] == kind)
                                           for kind in inventory['ranges_by_kind']}
    include = ROOT / 'Source/Files/17_ACTION.inc'
    source = include.read_text('utf-8')
    old = ('                ; исходный диапазон внутри 512-байтового назначения переноса, до таблицы активных клавиш\n'
           '                incbin "../Action/Resources/InitialTransferredContextMiddle.bin"')
    assert source.count(old) == 1
    new = ('                disp #9C8B\n                include "../Action/Data/ContextMapAndOptions.asm"\n'
           '                ent')
    pending = {ROOT / PATH: text.encode('utf-8'), include: source.replace(old, new).encode('utf-8'),
               reports / 'SourceMap.json': encode(source_map), reports / 'Symbols.json': encode(symbols),
               reports / 'Inventory.json': encode(inventory)}
    assert not (ROOT / PATH).exists()
    research = ROOT / 'Tools/Disasm/Research'
    candidate = research / 'Candidates/ActionContextMapRecords'
    history = research / 'History/BeforeActionContextMapRecords'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in pending}
    for path, blob in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    for path, blob in {**before, previous_path: previous_data}.items():
        assert path.read_bytes() == blob if blob is not None else not path.exists()
        if blob is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
    for path, blob in pending.items():
        path.write_bytes(blob)
    with redirect_stdout(StringIO()):
        verify()
    assert previous_path.resolve().is_relative_to((ROOT / 'Source/Action/Resources').resolve())
    assert previous_path.read_bytes() == (history / previous_path.relative_to(ROOT)).read_bytes() == previous_data
    previous_path.unlink()
    result = dict(passed=True, physical_bytes=END - START, record_labels=len(labels),
                  groups=len(differences), differing_disk_bytes=differences,
                  original_transfer_proved=True, all_action_consumers_proved=False,
                  original_bytes_preserved=True, assembly_executed=False)
    (reports / 'ActionContextMapRecordsClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

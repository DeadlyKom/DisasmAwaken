"""Публикация физических записей эффектов без пересборки."""
from collections import Counter
from hashlib import sha256
import json

from ActionVisualEffectData import END, ORIGIN, PATH, START, render
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()

    def read(name):
        return json.loads((reports / (name + '.json')).read_bytes())

    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    mapping, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    entry = next(item for item in mapping if item['slot'] == 17 and item['offset'] == 0x4780)
    assert entry['kind'] == 'unclassified' and entry['offset'] + entry['length'] == END
    original_path = ROOT / entry['path']
    original = original_path.read_bytes()
    assert original == source[0x4780:END]
    text, bindings = render(source)
    assert not (bindings.keys() & symbols.keys())
    symbols.update(bindings)
    prefix_path = 'Source/Resources/17_ACTION/Unclassified020_BeforeVisualEffects.bin'
    prefix = source[0x4780:START]
    pieces = [dict(entry, path=prefix_path, length=len(prefix), sha256=sha256(prefix).hexdigest()),
              dict(entry, path=PATH, offset=START, length=END - START, kind='typed_data',
                   origin=ORIGIN, sha256=sha256(source[START:END]).hexdigest())]
    index = mapping.index(entry)
    mapping[index:index + 1] = pieces
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in mapping))
    inventory['physical_bytes_by_kind'] = {kind: sum(item['length'] for item in mapping if item['kind'] == kind)
                                          for kind in inventory['ranges_by_kind']}
    includes = ROOT / 'Source/Files/17_ACTION.inc'
    include_text = includes.read_text('utf-8')
    needle = ('                ; Unknown, соседнее состояние A780..A82C ещё не разобрано\n'
              '                incbin "../Resources/17_ACTION/Unclassified020_AfterObjectRecords.bin"')
    assert include_text.count(needle) == 1
    replacement = ('                ; Unknown, соседнее состояние A780..A794 ещё не разобрано\n'
                   '                incbin "../Resources/17_ACTION/Unclassified020_BeforeVisualEffects.bin"\n'
                   '                assert $ == #4795\n'
                   '                disp #A795\n'
                   '                include "../Action/Data/VisualEffects.asm"\n'
                   '                ent')
    pending = {ROOT / PATH: text.encode('utf-8'), ROOT / prefix_path: prefix,
               includes: include_text.replace(needle, replacement).encode('utf-8')}
    for name, value in (('SourceMap', mapping), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = encode(value)
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionVisualEffectData'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionVisualEffectData'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in pending}
    before[original_path] = original
    for path, content in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    for path, content in before.items():
        assert path.read_bytes() == content if content is not None else not path.exists()
        if content is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    for path, content in pending.items():
        path.write_bytes(content)
    verify()
    assert original_path.resolve().is_relative_to((ROOT / 'Source/Resources/17_ACTION').resolve())
    assert original_path.read_bytes() == original == (history / original_path.relative_to(ROOT)).read_bytes()
    original_path.unlink()
    (reports / 'ActionVisualEffectDataClassification.json').write_bytes(encode(
        dict(passed=True, typed_bytes=152, physical_records=8, marker_prefix_bytes=8, assembly_executed=False)))


if __name__ == '__main__':
    main()

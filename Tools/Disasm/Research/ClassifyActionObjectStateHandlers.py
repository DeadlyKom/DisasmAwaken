"""Выделение 44 байтов указателей, соседний код сохраняется отдельным ресурсом."""
from collections import Counter
import contextlib
import hashlib
import io
import json

from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from ActionObjectStateHandlersData import TABLE, STRUCT, render, parse


def main():
    reports = ROOT / 'Tools/Disasm/Reports'

    def read(name):
        return json.loads((reports / (name+'.json')).read_text(encoding='utf-8'))

    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    assert read('ActionObjectStateDispatchVerification')['stopped_after_indirect_JP']
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    mapping, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    old = next(item for item in mapping if item['slot'] == 17 and item['offset'] == 0x8F50)
    assert old['kind'] == 'unclassified' and old['length'] == 237
    before_path = ROOT / old['path']
    original = before_path.read_bytes()
    assert original == source[0x8F50:0x903D] and original[44] == 0xC9
    text, labels = render(source)
    assert parse(text) == (original[:44], labels)
    assert not any(name in symbols for name in labels)
    symbols.update(labels)
    remainder = 'Source/Resources/17_ACTION/AfterObjectStateHandlers.bin'
    first = dict(old, path=TABLE[1], kind='typed_data', length=44, origin=0xEF50, sha256=hashlib.sha256(original[:44]).hexdigest())
    last = dict(old, path=remainder, offset=0x8F7C, length=193, sha256=hashlib.sha256(original[44:]).hexdigest())
    index = mapping.index(old)
    mapping[index:index+1] = [first, last]
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in mapping))
    inventory['physical_bytes_by_kind'] = {kind: sum(item['length'] for item in mapping if item['kind'] == kind)
                                          for kind in inventory['ranges_by_kind']}
    include_path = ROOT / 'Source/Files/17_ACTION.inc'
    includes = include_path.read_text(encoding='utf-8')
    needle = '                incbin "../Resources/17_ACTION/'+before_path.name+'"'
    assert includes.count(needle) == 1
    replacement = ('                disp #EF50\n                include "../Action/Data/ObjectStateHandlers.asm"\n'
                   '                ent\n                assert $ == #8F7C\n'
                   '                incbin "../Resources/17_ACTION/AfterObjectStateHandlers.bin"')
    struct_path = ROOT / 'Includes/Structs/Include.inc'
    structs = struct_path.read_text(encoding='utf-8')
    assert 'struct FObjectStateHandler' not in structs and structs.count('                endif') == 1
    pending = {ROOT/TABLE[1]: text.encode('utf-8'), ROOT/remainder: original[44:],
               include_path: includes.replace(needle, replacement).encode('utf-8'),
               struct_path: structs.replace('                endif', STRUCT+'                endif').encode('utf-8')}
    for name, data in (('SourceMap', mapping), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name+'.json')] = encode(data)
    candidate = ROOT/'Tools/Disasm/Research/Candidates/ActionObjectStateHandlers'
    history = ROOT/'Tools/Disasm/Research/History/BeforeActionObjectStateHandlers'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in pending}
    before[before_path] = original
    for path, data in pending.items():
        output = candidate/path.relative_to(ROOT)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    for path, data in before.items():
        assert path.read_bytes() == data if data is not None else not path.exists()
        if data is not None:
            output = history/path.relative_to(ROOT)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
    for path, data in pending.items():
        path.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert before_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert before_path.read_bytes() == original == (history/before_path.relative_to(ROOT)).read_bytes()
    before_path.unlink()
    result = dict(passed=True, typed_bytes=44, physical_records=22, preserved_following_bytes=193,
                  original_bytes_preserved=True, handler_execution_proved=False, assembly_executed=False)
    (reports/'ActionObjectStateHandlersClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

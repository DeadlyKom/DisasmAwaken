"""Физический экземпляр уже описанного 24-битного вектора по 9B6F."""
import contextlib
from collections import Counter
import io
import json

from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from ActionWorkVectorData import TRANSFORM_PATH, TRANSFORM_MODULE, render


def main():
    reports = ROOT / 'Tools/Disasm/Reports'

    def read(name):
        return json.loads((reports / (name+'.json')).read_text(encoding='utf-8'))

    def encode(data):
        return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    assert read('ActionPrepareBodyTransformVerification')['passed']
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    mapping, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    item = next(entry for entry in mapping if entry['slot'] == 17 and entry['offset'] == 0x3B6F)
    assert item['kind'] == 'unclassified' and item['length'] == 9
    previous = ROOT / item['path']
    original = previous.read_bytes()
    assert original == source[0x3B6F:0x3B78]
    text, bindings = render(source, 0x9B6F, TRANSFORM_MODULE, 'ActionPrepareBodyTransform')
    assert not any(name in symbols for name in bindings)
    symbols.update(bindings)
    item.update(path=TRANSFORM_PATH, kind='typed_data', origin=0x9B6F)
    inventory['ranges_by_kind'] = dict(Counter(entry['kind'] for entry in mapping))
    inventory['physical_bytes_by_kind'] = {kind: sum(entry['length'] for entry in mapping if entry['kind'] == kind)
                                          for kind in inventory['ranges_by_kind']}
    includes = ROOT / 'Source/Files/17_ACTION.inc'
    include_text = includes.read_text(encoding='utf-8')
    needle = ('                ; Unknown, соседние рабочие байты после шести физических векторов\n'
              '                incbin "../Resources/17_ACTION/BeforeWorkVector24.bin"')
    assert include_text.count(needle) == 1
    replacement = ('                disp #9B6F\n'
                   '                include "../Action/Data/TransformWorkVector24.asm"\n                ent')
    pending = {ROOT / TRANSFORM_PATH: text.encode('utf-8'), includes: include_text.replace(needle, replacement).encode('utf-8')}
    for name, data in (('SourceMap', mapping), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name+'.json')] = encode(data)
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionTransformWorkVector'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionTransformWorkVector'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in pending}
    before[previous] = original
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
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes() == original == (history / previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    result = dict(passed=True, typed_bytes=9, physical_records=1, reused_structure='FActionWorkVector24',
                  original_bytes_preserved=True, assembly_executed=False)
    (reports / 'ActionTransformWorkVectorClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

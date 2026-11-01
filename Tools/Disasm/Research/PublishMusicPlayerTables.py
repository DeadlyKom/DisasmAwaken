"""Точные экземпляры структур вместо 545 исходных двоичных байтов, без сборки."""
from pathlib import Path
import collections, contextlib, hashlib, io, json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'), str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify
from MusicPlayerTables import TABLES, STRUCTURES, render, parse


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encoded(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert all(read(stem)['passed'] for stem in ('MusicSynthesisVerification', 'MusicPatternRowsVerification', 'MusicAdvanceAVerification'))
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/MusicPlayerTables'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeMusicPlayerTables'
    assert not candidate.exists() and not history.exists()
    pending = {}
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    source_map = read('SourceMap')
    original = [item for item in source_map if item['slot'] == 10 and item['offset'] in (0xA0, 0x31E)]
    assert len(original) == 2 and sorted(item['length'] for item in original) == [1, 544]
    removed = {ROOT / item['path']: (ROOT / item['path']).read_bytes() for item in original}
    assert all(item['kind'] == 'unclassified' and (ROOT/item['path']).read_bytes() == raw[item['offset']:item['offset']+item['length']] for item in original)
    symbols = read('Symbols')
    replacements = []
    for table in TABLES:
        module, path, start, end, structure, fields, names = table
        text, bindings = render(raw, table)
        rebuilt, parsed = parse(text, table)
        assert rebuilt == raw[start:end] and parsed == bindings and not (ROOT/path).exists()
        pending[ROOT/path] = text.encode('utf-8')
        for name, address in bindings.items():
            assert name not in symbols
            symbols[name] = address
        replacements.append(dict(slot=10, offset=start, length=end-start, kind='typed_data',
                                 path=path, origin=0xDB00+start, sha256=hashlib.sha256(rebuilt).hexdigest()))
    assert sum(item['length'] for item in replacements) == 545
    source_map = sorted([item for item in source_map if item not in original] + replacements, key=lambda item: (item['slot'], item['offset']))
    p = ROOT/'Includes/Structs/Include.inc'
    text = p.read_text('utf-8')
    block = '\n                ; Исходные физические данные проигрывателя, поля не выделяют новую память\n'
    for structure, fields in STRUCTURES.items():
        assert 'struct ' + structure not in text
        block += '                struct ' + structure + '\n'
        for name, width, note in fields:
            assert len(name) < 16 and width in (1, 2)
            block += name.ljust(16) + ('db #00' if width == 1 else 'dw #0000').ljust(64) + '; ' + note + '\n'
        block += '                ends\n                assert ' + structure + ' == ' + str(sum(width for _, width, _ in fields)) + '\n\n'
    assert text.count('                endif') == 1
    pending[p] = text.replace('                endif', block + '                endif').encode('utf-8')
    p = ROOT/'Source/Files/10_MUZ1.inc'
    text = p.read_text('utf-8')
    for old in original:
        note = ('Unknown, прежние байты перед первым словом эффектов A сохранены без интерпретации'
                if old['offset'] == 0xA0 else 'Unknown, исходные байты вне подтверждённого прямого потока управления')
        needle = '                ; ' + note + '\n                incbin "../Resources/10_MUZ1/' + Path(old['path']).name + '"'
        assert text.count(needle) == 1
        parts = [table for table in TABLES if old['offset'] <= table[2] < old['offset']+old['length']]
        block = ''
        for table in parts:
            module, path, start, end, _, _, _ = table
            block += '                disp #' + format(0xDB00+start, '04X') + '\n'
            block += '                include "../Music/Data/' + Path(path).name + '"\n                ent\n'
            block += '                assert $ == #' + format(end, '04X') + '\n'
        text = text.replace(needle, block.rstrip())
    pending[p] = text.encode('utf-8')
    inventory = read('Inventory')
    inventory['physical_bytes_by_kind'] = {kind: sum(item['length'] for item in source_map if item['kind'] == kind) for kind in inventory['physical_bytes_by_kind']}
    inventory['ranges_by_kind'] = dict(collections.Counter(item['kind'] for item in source_map))
    for stem, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')] = encoded(value)
    plan = [(p, p.read_bytes() if p.exists() else None, data) for p, data in pending.items()]
    for p, before, data in plan:
        c = candidate/p.relative_to(ROOT)
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(data)
    for p, before, data in plan:
        assert (p.read_bytes() == before) if before is not None else not p.exists()
    for p, before in {**{p: before for p, before, _ in plan if before is not None}, **removed}.items():
        h = history/p.relative_to(ROOT)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_bytes(before)
    for p, before, data in plan:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for p, before in removed.items():
        assert p.resolve().is_relative_to((ROOT/'Source/Resources/10_MUZ1').resolve())
        assert p.read_bytes() == before == (history/p.relative_to(ROOT)).read_bytes()
        p.unlink()
    result = dict(passed=True, typed_bytes=545, physical_instances=sum(len(table[6]) for table in TABLES),
        source_files=len(TABLES), physical_bytes_preserved=True, instructions_changed=0,
        volume_zero_overlay_preserved=True, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MusicPlayerTablesClassification.json').write_bytes(encoded(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

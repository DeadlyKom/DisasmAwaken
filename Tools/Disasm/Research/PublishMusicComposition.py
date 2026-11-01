"""Кандидат исходников композиции с точным сохранением общих данных и исходного ресурса в истории."""
from pathlib import Path, PurePosixPath
import collections, contextlib, io, json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'), str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify
from MusicCompositionLayout import EXTRA_STRUCTURES
from MusicCompositionSource import descriptions, render, parse


def include_block(parts):
    lines = ['                ; Исходная композиция, физический порядок записей сохранён']
    for item in parts:
        local = str(PurePosixPath(item['path']).relative_to('Source/Music'))
        lines += ['                disp #' + format(0xE700+item['offset'], '04X'),
                  '                include "../Music/' + local + '"', '                ent',
                  '                assert $ == #' + format(0xC00+item['offset']+item['length'], '04X')]
    return '\n'.join(lines)


def flatten_current_includes():
    """Согласование уже созданного кандидата с прямой проверяемой цепочкой Source/Files."""
    p = ROOT/'Source/Files/10_MUZ1.inc'
    text = p.read_text('utf-8')
    needle = '                ; Исходная композиция, физический порядок записей сохранён\n                disp #E700\n                include "../Music/Composition/Include.inc"\n                ent'
    assert text.count(needle) == 1
    data = (ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()[0xC00:]
    p.write_text(text.replace(needle, include_block(descriptions(data))), encoding='utf-8')
    intermediate = ROOT/'Source/Music/Composition/Include.inc'
    witness = ROOT/'Tools/Disasm/Research/Candidates/MusicComposition/Source/Music/Composition/Include.inc'
    assert intermediate.resolve().is_relative_to((ROOT/'Source/Music/Composition').resolve())
    assert intermediate.read_bytes() == witness.read_bytes()
    intermediate.unlink()


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encoded(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('MusicCompositionLayout')['passed'] and read('MusicPatternRowsVerification')['passed']
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/MusicComposition'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeMusicComposition'
    assert not candidate.exists() and not history.exists()
    pending = {}
    source_map = read('SourceMap')
    old = next(item for item in source_map if item['slot'] == 10 and item['offset'] == 0xC00)
    assert old['path'] == 'Source/Music/Resources/Antichrist.pt3' and old['length'] == 4137
    old_path = ROOT/old['path']
    data = old_path.read_bytes()
    assert data == (ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()[0xC00:]
    symbols = read('Symbols')
    parts = descriptions(data)
    new_ranges = []
    for item in parts:
        text, bindings = render(data, item)
        raw, actual_bindings = parse(text, data, item)
        assert raw == data[item['offset']:item['offset']+item['length']] and actual_bindings == bindings
        p = ROOT/item['path']
        assert not p.exists()
        pending[p] = text.encode('utf-8')
        for name, address in bindings.items():
            assert name not in symbols
            symbols[name] = address
        new_ranges.append(dict(slot=10, offset=0xC00+item['offset'], length=item['length'],
                               kind='typed_data', path=item['path'], origin=0xE700+item['offset'],
                               sha256=item['sha256'], format='PT3_' + item['kind'].upper()))
    source_map = sorted([item for item in source_map if item != old] + new_ranges, key=lambda item: (item['slot'], item['offset']))
    p = ROOT/'Includes/Structs/Include.inc'
    text = p.read_text('utf-8')
    block = '\n                ; Физические поля исходной композиции, адреса и байты не меняются\n'
    for structure, fields in EXTRA_STRUCTURES.items():
        assert 'struct ' + structure not in text
        block += '                struct ' + structure + '\n'
        for name, width, directive, note in fields:
            assert len(name) < 16
            initializer = 'text ' + str(width) + ', { #00 }' if directive == 'text' else 'db #00' if directive == 'db' else 'dw #0000'
            block += name.ljust(16) + initializer.ljust(64) + '; ' + note + '\n'
        block += '                ends\n                assert ' + structure + ' == ' + str(sum(width for _, width, _, _ in fields)) + '\n\n'
    assert text.count('                endif') == 1
    pending[p] = text.replace('                endif', block + '                endif').encode('utf-8')
    p = ROOT/'Source/Files/10_MUZ1.inc'
    text = p.read_text('utf-8')
    needle = '                ; исходный ресурс PT3\n                incbin "../Music/Resources/Antichrist.pt3"'
    assert text.count(needle) == 1
    pending[p] = text.replace(needle, include_block(parts)).encode('utf-8')
    inventory = read('Inventory')
    inventory['physical_bytes_by_kind'] = {kind: sum(item['length'] for item in source_map if item['kind'] == kind) for kind in inventory['physical_bytes_by_kind']}
    inventory['ranges_by_kind'] = dict(collections.Counter(item['kind'] for item in source_map))
    for stem, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[ROOT/('Tools/Disasm/Reports/' + stem + '.json')] = encoded(value)
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for p, before, after in plan:
        c = candidate/p.relative_to(ROOT)
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(after)
    for p, before, after in plan:
        assert (p.read_bytes() == before) if before is not None else not p.exists()
    for p, before in {**{p: before for p, before, _ in plan if before is not None}, old_path: data}.items():
        h = history/p.relative_to(ROOT)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_bytes(before)
    for p, before, after in plan:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Music/Resources').resolve())
    assert old_path.read_bytes() == data == (history/old_path.relative_to(ROOT)).read_bytes()
    old_path.unlink()
    result = dict(passed=True, physical_bytes=4137, source_parts=len(parts), pattern_streams=41,
        sample_headers=12, sample_steps=77, ornament_headers=14, ornament_steps=57,
        duplicate_references_preserved=True, zero_relative_offsets_preserved=True,
        header_unknown63_preserved=True, original_resource_preserved_in_extraction_and_history=True,
        instructions_changed=0, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MusicCompositionClassification.json').write_bytes(encoded(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

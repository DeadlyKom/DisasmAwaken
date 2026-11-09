"""Публикация BAR и кадров BD, с сохранением неизвестного хвоста и всех секторов."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import sys

from FighterAssetData import FIELDS, ROOT, original, decode, render, parse
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    assert read('FighterAssetsVerification')['passed']
    source_map, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    bar, banks = original()
    pointers, groups, sprites, ends = decode(bar, banks)
    pending, removed = {}, []
    table_path = 'Source/Resources/39_BAR/PoseSequences.asm'
    table = render(bar, pointers, groups)
    pending[ROOT / table_path] = table.encode('utf-8')
    for label, offset in parse(table)[1].items():
        symbol = 'FighterPoseData.' + label
        assert symbol not in symbols
        symbols[symbol] = offset
    for slot, name in ((39, 'BAR'), *((40 + bank, 'BD' + str(bank)) for bank in range(4))):
        old = next(item for item in source_map if item['slot'] == slot)
        assert old['kind'] == 'unclassified'
        old_path = ROOT / old['path']
        data = old_path.read_bytes()
        assert data == (ROOT / f'Tools/Disasm/Extracted/Active/{slot}_{name}.C.sectors.bin').read_bytes()
        spans = []
        prefix = f'Source/Resources/{slot}_{name}/'
        lines = ['; -----------------------------------------', f'; запись {slot}, {name}.C',
                 '; -----------------------------------------',
                 '                ; Документация [таблицы и кадры бойцов](../../Docs/FighterAssets.md)']
        def part(start, end, path, kind):
            assert start < end
            raw = data[start:end]
            spans.append(dict(slot=slot, offset=start, length=end - start, path=path, kind=kind,
                              origin=None, sha256=hashlib.sha256(raw).hexdigest()))
            if kind != 'typed_data':
                pending[ROOT / path] = raw
            lines.extend((f'                assert $ == #{start:04X}',
                          '                ' + ('include' if kind == 'typed_data' else 'incbin') +
                          f' "../Resources/{slot}_{name}/' + path.rsplit('/', 1)[1] + '"'))
        if slot == 39:
            part(0, len(bar), table_path, 'typed_data')
            logical = len(bar)
        else:
            bank = slot - 40
            for _, offset, width, height in (sprite for sprite in sprites if sprite[0] == bank):
                lines.append(f'                ; Маска и пиксели, ширина {width} байтов, высота {height} строк, ссылка BAR на #{0xC000 + offset:04X}.')
                part(offset, offset + 2 * width * height, prefix + f'Sprite{offset:04X}.bin', 'binary_resource')
            logical = len(banks[bank])
            if ends[bank] < logical:
                lines.append('                ; 720 логических байтов без подтверждённой ссылки BAR, формат не назначается.')
                part(ends[bank], logical, prefix + 'UnknownLogicalTail.bin', 'unclassified')
        if logical < len(data):
            lines.append('                ; Исходный секторный хвост после логического файла, сохранён отдельно.')
            part(logical, len(data), prefix + 'SectorTail.bin', 'unclassified')
        lines.extend((f'                assert $ == #{len(data):04X}', ''))
        assert sum(item['length'] for item in spans) == len(data)
        index = source_map.index(old)
        source_map[index:index + 1] = spans
        pending[ROOT / f'Source/Files/{slot}_{name}.inc'] = '\n'.join(lines).encode('utf-8')
        removed.append(old_path)
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in source_map))
    sizes = Counter()
    for item in source_map:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert 'struct FFighterPosePointer' not in text and text.count('                endif') == 1
    block = '                ; Физические записи BAR, значения полей подтверждены архивным потребителем\n'
    for structure, fields in FIELDS.items():
        block += f'                struct {structure}\n'
        for name, size, note in fields:
            directive = 'db #00' if size == 1 else 'dw #0000'
            block += (name.ljust(16) + directive).ljust(80) + '; ' + note + '\n'
        length = sum(size for _, size, _ in fields)
        block += f'                ends\n                assert {structure} == #{length:02X}\n\n'
    pending[path] = text.replace('                endif', block + '                endif').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка связанного набора BAR и BD, геометрии каждого кадра и сохранения неизвестных хвостов.
    from FighterAssetData import parse as parse_fighter, decode as decode_fighter
    bar = sources[39][:3076]
    banks = [sources[40 + bank][:length] for bank, length in enumerate((16268,16152,16248,12048))]
    _, _, sprites, _ = decode_fighter(bar, banks)
    text = (ROOT/'Source/Resources/39_BAR/PoseSequences.asm').read_text('utf-8')
    actual, labels = parse_fighter(text)
    assert actual == bar
    for label, offset in labels.items():
        assert symbols[('FighterPoseData.' + label).upper()] == offset
    assert symbols['FFIGHTERPOSEPOINTER'] == 2 and symbols['FFIGHTERPOSEHEADER'] == 4
    assert symbols['FFIGHTERPOSESTEP'] == 14
    for field, offset in (('BANKINDEX',9),('SPRITEADDRESS',10),('WIDTHBYTES',12),('HEIGHT',13)):
        assert symbols['FFIGHTERPOSESTEP.' + field] == offset
    for bank, offset, width, height in sprites:
        path = f'Source/Resources/{40+bank}_BD{bank}/Sprite{offset:04X}.bin'
        assert (ROOT/path).read_bytes() == banks[bank][offset:offset + 2*width*height]

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/FighterAssets'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeFighterAssets'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in (*pending, *removed)}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, previous in before.items():
        assert path.read_bytes() == previous if previous is not None else not path.exists()
        if previous is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(previous)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for path in removed:
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    print('BAR: 3076 байтов физических структур, BD: 56 кадров и 59996 байтов, хвосты сохранены')


if __name__ == '__main__':
    main()

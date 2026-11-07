"""Публикация сохранённых 256 отсчётов без подстановки таблицы, создаваемой при исполнении."""
from collections import Counter
import contextlib
import io
import json
import os
import tempfile
from pathlib import Path
import sys

from IntroCoordinateSeed import ROOT, PATH, render, parse
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    assert read('IntroCoordinateSeedVerification')['passed']
    sm, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    old = next(item for item in sm if item['slot'] == 3 and item['offset'] == 256)
    old_path = ROOT / old['path']
    raw = old_path.read_bytes()
    assert old['kind'] == 'unclassified' and old['length'] == 256
    text = render(raw)
    assert parse(text) == raw
    pending = {ROOT / PATH: text.encode('utf-8')}
    sm[sm.index(old)] = dict(old, kind='typed_data', path=PATH, origin=0x6400)
    for index in range(256):
        key = f'IntroCoordinateSeed.Index{index:02X}'
        assert key not in symbols
        symbols[key] = 0x6400 + index
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in sm))
    sizes = Counter()
    for item in sm:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', sm), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Source/Files/03_AWAKEN.inc'
    text = path.read_text(encoding='utf-8')
    needle = '                incbin "../Resources/03_AWAKEN/UnclassifiedIntroCoordinateSeed.bin"'
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, '                disp #6400\n                include "../Intro/Data/CoordinateSeed.asm"\n                ent').encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert 'struct FIntroCoordinateSample' not in text
    block = '''                struct FIntroCoordinateSample
Value           db #00                                                          ; беззнаковый исходный отсчёт координатной таблицы, не готовый адрес и не флаги
                ends
                assert FIntroCoordinateSample == #01

'''
    pending[path] = text.replace('                endif', block + '                endif').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка исходных отсчётов, нулевая вторая половина не заменяется результатом исполнения.
    from IntroCoordinateSeed import PATH as intro_coordinate_path, parse as parse_intro_coordinate_seed
    assert parse_intro_coordinate_seed((ROOT/intro_coordinate_path).read_text('utf-8'))==sources[3][256:512]
    assert symbols['FINTROCOORDINATESAMPLE']==1
    assert all(symbols[f'INTROCOORDINATESEED.INDEX{index:02X}']==0x6400+index for index in range(256))

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    path = ROOT / 'Source/Intro/BuildScreenTables.asm'
    text = path.read_text(encoding='utf-8')
    needle = '; Документация [Intro](../../Docs/FunctionDetails/Intro.md)'
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, needle + '\n                ; Исходные отсчёты [координатная таблица](../../Docs/IntroCoordinateSeed.md)').encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/IntroCoordinateSeed'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeIntroCoordinateSeed'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in (*pending, old_path)}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, original in before.items():
        assert path.read_bytes() == original if original is not None else not path.exists()
        if original is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == '.json':
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='intro-coordinates-', suffix='.tmp', delete=False) as output:
                temporary = Path(output.name)
                output.write(raw)
            try:
                os.replace(temporary, path)
            finally:
                if temporary.exists():
                    temporary.unlink()
        else:
            path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert old_path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
    assert old_path.read_bytes() == (history / old_path.relative_to(ROOT)).read_bytes()
    old_path.unlink()
    print('256 исходных отсчётов вступления оформлены, вторая половина сохранена нулевой')


if __name__ == '__main__':
    main()

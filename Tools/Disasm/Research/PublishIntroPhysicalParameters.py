"""Публикация проверенного кандидата параметров вступления с сохранением истории."""
from collections import Counter
import contextlib
import hashlib
import io
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
from CheckIntro import ROOT
from IntroPhysicalParameters import BLOCKS, TYPES, REPLACEMENTS, render, parse, source_path
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text('utf-8'))
    assert read('IntroPhysicalParametersVerification')['passed']
    source_map, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    source = (ROOT / 'Tools/Disasm/Extracted/Active/03_AWAKEN.B.sectors.bin').read_bytes()
    pending, removed = {}, []
    includes = ROOT / 'Source/Files/03_AWAKEN.inc'
    include_text = includes.read_text('utf-8')
    for block in BLOCKS:
        offset, length, module, filename = block
        old = next(row for row in source_map if row['slot'] == 3 and row['offset'] == offset)
        assert old['kind'] == 'unclassified' and old['length'] in (length, length+1)
        old_path = ROOT / old['path']
        assert old_path.read_bytes() == source[offset:offset+old['length']]
        removed.append(old_path)
        raw = source[offset:offset+length]
        text, labels = render(block, raw)
        assert parse(block, text) == raw
        new_path = source_path(filename)
        pending[ROOT / new_path] = text.encode('utf-8')
        new_row = dict(old, length=length, kind='typed_data', origin=0x6300+offset,
                       path=new_path, sha256=hashlib.sha256(raw).hexdigest())
        replacement_rows = [new_row]
        replacement = f'                disp #{0x6300+offset:04X}\n                include "../Intro/Data/{filename}"\n                ent'
        if old['length'] != length:
            residual = 'Source/Resources/03_AWAKEN/UnknownAfterLookupParameters.bin'
            tail = source[offset+length:offset+old['length']]
            pending[ROOT / residual] = tail
            replacement_rows.append(dict(old, offset=offset+length, length=len(tail), path=residual,
                                         sha256=hashlib.sha256(tail).hexdigest()))
            replacement += '\n                ; Назначение соседнего байта 66A2 ещё не установлено.\n'
            replacement += '                incbin "../Resources/03_AWAKEN/UnknownAfterLookupParameters.bin"'
        source_map[source_map.index(old):source_map.index(old)+1] = replacement_rows
        needle = '                incbin "../' + old_path.relative_to(ROOT / 'Source').as_posix() + '"'
        assert include_text.count(needle) == 1
        include_text = include_text.replace(needle, replacement)
        for key, value in labels.items():
            assert key not in symbols
            symbols[key] = value
    pending[includes] = include_text.encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    additions = []
    for name, field, meaning in TYPES:
        assert 'struct ' + name not in text
        additions += ['                struct ' + name,
                      (field.ljust(16) + 'db #00').ljust(80) + '; ' + meaning,
                      '                ends', '                assert ' + name + ' == #01', '']
    pending[path] = text.replace('                endif', '\n'.join(additions) + '\n                endif').encode('utf-8')
    for name, replacements in REPLACEMENTS.items():
        path = ROOT / f'Source/Intro/{name}.asm'
        text = path.read_text('utf-8')
        for old, new in replacements.items():
            assert text.count(old) == 1
            text = text.replace(old, new)
        needle = '                module ' + name
        text = text.replace(needle, needle + '\n                ; Физические параметры [источники и потребители](../../Docs/IntroPhysicalParameters.md)', 1)
        pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/SemanticNames.py'
    text = path.read_text('utf-8')
    text = text.replace('def name_operands(region, function_address, operation):',
                        'def name_operands(region, function_address, operation):\n    operation = intro_physical_parameter_name_operands(region, function_address, operation)', 1)
    text += '\nfrom IntroPhysicalParameters import name_operands as intro_physical_parameter_name_operands\n'
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text('utf-8')
    marker = '    # Проверка исходных отсчётов, нулевая вторая половина не заменяется результатом исполнения.'
    assert text.count(marker) == 1
    hook = '''    # Проверка физических параметров вступления и каждой исходной записи, включая два состояния фаз.
    from IntroPhysicalParameters import BLOCKS as intro_parameter_blocks, TYPES as intro_parameter_types
    from IntroPhysicalParameters import parse as parse_intro_parameters, render as render_intro_parameters, source_path
    for block in intro_parameter_blocks:
        offset, length, _, filename = block
        raw = sources[3][offset:offset+length]
        assert parse_intro_parameters(block, (ROOT/source_path(filename)).read_text('utf-8')) == raw
        _, labels = render_intro_parameters(block, raw)
        assert all(symbols[key.upper()] == value for key, value in labels.items())
    for name, field, _ in intro_parameter_types:
        assert symbols[name.upper()] == 1 and symbols[(name+'.'+field).upper()] == 0

'''
    pending[path] = text.replace(marker, hook+marker).encode('utf-8')
    inventory['ranges_by_kind'] = dict(Counter(row['kind'] for row in source_map))
    totals = Counter()
    for row in source_map:
        totals[row['kind']] += row['length']
    inventory['physical_bytes_by_kind'] = dict(totals)
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name+'.json')] = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/IntroPhysicalParameters'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeIntroPhysicalParameters'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in (*pending, *removed)}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    # Проверка отсутствия пересечения с новыми ручными правками перед заменой файлов.
    for path, raw in before.items():
        assert path.read_bytes() == raw if raw is not None else not path.exists()
        if raw is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == '.json':
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='intro-parameters-', suffix='.tmp', delete=False) as output:
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
        importlib.reload(sys.modules['VerifySources']).main()
    for path in removed:
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == (history/path.relative_to(ROOT)).read_bytes()
        path.unlink()
    print('172 исходных байта параметров вступления оформлены, соседний байт 66A2 оставлен Unknown')


if __name__ == '__main__':
    main()

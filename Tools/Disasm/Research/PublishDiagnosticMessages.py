"""Публикация 20 исходных строковых байтов и точных ссылок диагностической процедуры."""
from collections import Counter
import contextlib
import io
import json
import sys

from CheckIntro import ROOT
from DiagnosticMessages import PATH, DATA, LABELS, SOURCE, parse
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    source_map, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    old = next(item for item in source_map if item['slot'] == 17 and item['offset'] == 0x4CD6)
    old_path = ROOT / old['path']
    assert old['kind'] == 'unclassified' and old['length'] == 20 and old_path.read_bytes() == DATA
    assert parse(SOURCE) == (DATA, LABELS)
    # Выравнивание только трёх новых комментариев данных, текстовые литералы сохраняются.
    source = '\n'.join(line.partition(';')[0].rstrip().ljust(80) + ';' + line.partition(';')[2]
                       if ';' in line and line.partition(';')[0].strip() else line
                       for line in SOURCE.splitlines()) + '\n'
    pending = {ROOT / PATH: source.encode('utf-8')}
    replacement = dict(old, path=PATH, kind='typed_data', origin=0xACD6)
    source_map[source_map.index(old)] = replacement
    for label, address in LABELS.items():
        name = 'ActionDiagnosticMessages.' + label
        assert name not in symbols
        symbols[name] = address
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in source_map))
    sizes = Counter()
    for item in source_map:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Source/Files/17_ACTION.inc'
    text = path.read_text(encoding='utf-8')
    needle = '                ; Unknown, соседние байты вне доказанного входа QueueDiagnosticCounters\n' + (
        '                incbin "../Resources/17_ACTION/' + old_path.name + '"')
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, '                disp #ACD6\n'
        '                include "../Action/Data/DiagnosticMessages.asm"\n                ent').encode('utf-8')
    for relative in ('Source/Action/QueueDiagnosticCounters.asm', 'Tools/Disasm/Research/ActionDiagnosticQueueFacts.py'):
        path = ROOT / relative
        text = path.read_text(encoding='utf-8')
        if relative.endswith('.asm'):
            for label, address in LABELS.items():
                needle = 'LD DE, #' + format(address, '04X')
                assert text.count(needle) == 1
                text = text.replace(needle, 'LD DE, @ActionDiagnosticMessages.' + label)
        else:
            needle = "    return operation\n"
            assert text.count(needle) == 1
            hook = "    if region == 'Action' and function_address == 0xACAB:\n"
            for label, address in LABELS.items():
                hook += f"        operation = operation.replace('LD DE, #{address:04X}', 'LD DE, @ActionDiagnosticMessages.{label}')\n"
            text = text.replace(needle, hook + needle)
        pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка трёх исходных диагностических строк и управляющих CR/LF.
    from DiagnosticMessages import PATH as diagnostic_path, DATA as diagnostic_data, LABELS as diagnostic_labels, parse as parse_diagnostic
    raw, labels = parse_diagnostic((ROOT/diagnostic_path).read_text('utf-8'))
    assert raw == diagnostic_data == sources[17][0x4CD6:0x4CEA]
    assert labels == diagnostic_labels
    assert all(symbols[('ActionDiagnosticMessages.'+label).upper()]==address for label,address in labels.items())

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    path = ROOT / 'Docs/ActionDiagnosticQueue.md'
    text = path.read_text(encoding='utf-8')
    pending[path] = (text + '\nТри физических текста с сохранёнными CR и LF находятся в\n'
        '[DiagnosticMessages.asm](../Source/Action/Data/DiagnosticMessages.asm), всего 20 исходных байтов.\n').encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/DiagnosticMessages'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeDiagnosticMessages'
    assert not candidate.exists() and not history.exists()
    originals = {path: path.read_bytes() if path.exists() else None for path in (*pending, old_path)}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, original in originals.items():
        assert path.read_bytes() == original if original is not None else not path.exists()
        if original is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert old_path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
    assert old_path.read_bytes() == DATA == (history / old_path.relative_to(ROOT)).read_bytes()
    old_path.unlink()
    print('20 строковых байтов Status, Deads и CR/LF оформлены без преобразования')


if __name__ == '__main__':
    main()

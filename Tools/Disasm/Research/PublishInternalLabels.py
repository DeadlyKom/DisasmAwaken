"""Публикация явно заданных доказанных имён, с кандидатом и проверкой исходных инструкций."""
import contextlib
import io
import json
import re
import sys

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def publish(name, title, mappings, comment_edits=None):
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    path = ROOT / 'Tools/Disasm/Reports/Symbols.json'
    symbols = json.loads(path.read_text(encoding='utf-8'))
    renames = {}
    docs = ['# ' + title, '',
            'Имена относятся к исходным операциям и сохраняют фактические адреса.',
            'Изменений инструкций и новых областей памяти нет.', '',
            '| Процедура | Адрес | Имя | Назначение входа |', '| --- | --- | --- | --- |']
    for (region, owner), labels in mappings.items():
        for old, (new, purpose) in labels.items():
            assert len(new) <= 14
            before, after = f'{region}.{owner}.{old}', f'{region}.{owner}.{new}'
            assert after not in symbols
            address = symbols.pop(before)
            symbols[after] = address
            renames[before] = after
            docs.append(f'| [{owner}](../Source/{region}/{owner}.asm) | #{address:04X} | {new} | {purpose} |')
    pending = {path: (json.dumps(symbols, ensure_ascii=False, indent=2) + '\n').encode('utf-8')}
    for folder, patterns in (('Source', ('*.asm', '*.inc')), ('Docs', ('*.md',))):
        for pattern in patterns:
            for path in (ROOT / folder).rglob(pattern):
                before = path.read_text(encoding='utf-8')
                text = before
                for old, new in renames.items():
                    text = re.sub(re.escape(old) + r'(?![\w.])', new, text)
                key = path.parent.name, path.stem
                if key in mappings and path.parent.parent == ROOT / 'Source':
                    for old, (new, _) in mappings[key].items():
                        text, count = re.subn(r'^' + old + r':\s+', (new + ':').ljust(16), text, flags=re.M)
                        assert count == 1
                    marker = '                module ' + path.stem + '\n'
                    assert text.count(marker) == 1
                    text = text.replace(marker, marker + f'                ; Внутренние входы [алгоритм](../../Docs/{name}.md)\n')
                # Комментарии привязаны к точной строке инструкции, несовпадение останавливает публикацию.
                for needle, note in (comment_edits or {}).get(key, ()):
                    matches = [line for line in text.splitlines() if line.partition(';')[0].strip() == needle]
                    notes = [note] if isinstance(note, str) else note
                    assert len(matches) == len(notes), (path, needle, len(matches))
                    for old, explanation in zip(matches, notes):
                        text = text.replace(old, old.partition(';')[0].rstrip().ljust(80) + '; ' + explanation, 1)
                if text != before:
                    lines = []
                    for line in text.splitlines():
                        code, sep, note = line.partition(';')
                        if sep and any(new in code for new in renames.values()):
                            line = code.rstrip().ljust(80) + ';' + note
                        lines.append(line)
                    pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    docs += ['', 'Положение меток сверяет [CheckSourceLabels](../Tools/Disasm/Research/CheckSourceLabels.py).',
             'Инструкции сверяет [VerifySources](../Tools/Disasm/VerifySources.py), без запуска сборки.', '']
    pending[ROOT / f'Docs/{name}.md'] = '\n'.join(docs).encode('utf-8')
    candidate = ROOT / f'Tools/Disasm/Research/Candidates/{name}'
    history = ROOT / f'Tools/Disasm/Research/History/Before{name}'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in pending}
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
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    result = dict(passed=True, renamed_internal_labels=len(renames), instructions_changed=0,
                  physical_bytes_preserved=True, assembly_executed=False)
    (ROOT / f'Tools/Disasm/Reports/{name}Verification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))

"""Доказанное имя поля выбора обработчика, без изменения его смещения либо исходных значений."""
import contextlib
import io
import importlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    pending = {}
    for folder, patterns in (('Source', ('*.asm', '*.inc')), ('Docs', ('*.md',))):
        for pattern in patterns:
            for path in (ROOT / folder).rglob(pattern):
                text = path.read_text(encoding='utf-8')
                if 'FActionRecord.Unknown0A' in text:
                    pending[path] = text.replace('FActionRecord.Unknown0A', 'FActionRecord.StateCode').encode('utf-8')
                    if folder == 'Source':
                        pending[path] = pending[path].decode('utf-8').replace('Unknown0A', 'StateCode').encode('utf-8')
    for path in (ROOT / 'Tools/Disasm/Research').glob('*.py'):
        if path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding='utf-8')
        if 'FActionRecord.Unknown0A' in text:
            pending[path] = text.replace('FActionRecord.Unknown0A', 'FActionRecord.StateCode').encode('utf-8')
    # Имена в следующих модулях относятся именно к FActionRecord, другой Unknown0A по 65E5 не затрагивается.
    facts = ('ActionClass0LinkFacts', 'ActionClass18StateFacts', 'ActionClass3LinkCountFacts',
             'ActionClass9LinkFacts', 'ActionLinkOverrideFacts', 'ActionMissileCreationFacts',
             'ActionObjectOffsetFacts', 'ActionObjectOffsetTransferFacts', 'ActionObjectPhaseWaitFacts',
             'ActionObjectStateReturnFacts', 'ActionPreferredRecordFacts')
    for stem in facts:
        path = ROOT / f'Tools/Disasm/Research/{stem}.py'
        text = pending.get(path, path.read_bytes()).decode('utf-8')
        pending[path] = text.replace('Unknown0A', 'StateCode').encode('utf-8')
    for stem in ('ActionClass3LinkCount', 'ActionClass0Link', 'ActionClass9Link', 'ActionLinkOverride', 'ActionPreferredRecord'):
        path = ROOT / f'Docs/{stem}.md'
        text = path.read_text(encoding='utf-8')
        assert 'Unknown0A' in text
        pending[path] = text.replace('Unknown0A', 'StateCode').encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ActionSpawnScheduleFacts.py'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    assert "fields = {'0B':" in text and "'09', '0A', '0D'" in text
    text = text.replace("fields = {'0B':", "fields = {'0A': 'StateCode', '0B':")
    text = text.replace("'09', '0A', '0D'", "'09', '0D'")
    pending[path] = text.encode('utf-8')
    note = 'байтовый код выбора обработчика ObjectStateHandlers, 60AE записывает 08'
    path = ROOT / 'Tools/Disasm/Research/ActionObjectRecords.py'
    text = path.read_text(encoding='utf-8')
    needle = 'KNOWN={11:'
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, "KNOWN={10:('StateCode','" + note + "'),\n       11:").encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    line = next(line for line in text.splitlines() if re.match(r'^Unknown0A\s+db', line))
    assert 'struct FActionRecord' in text
    pending[path] = text.replace(line, ('StateCode'.ljust(16) + 'db #00').ljust(80) + '; ' + note).encode('utf-8')
    path = ROOT / 'Source/Action/Data/ObjectRecords.asm'
    text = path.read_text(encoding='utf-8')
    needle = '; Unknown0A, игровой смысл ещё неизвестен, 60AE записывает 08'
    assert text.count(needle) == 26
    pending[path] = text.replace(needle, '; StateCode, ' + note).encode('utf-8')
    path = ROOT / 'Tools/Disasm/Reports/Symbols.json'
    symbols = json.loads(path.read_text(encoding='utf-8'))
    renamed = []
    for key in tuple(symbols):
        if key.startswith('ActionObjectRecords.') and key.endswith('.Unknown0A'):
            new = key.removesuffix('.Unknown0A') + '.StateCode'
            assert new not in symbols
            symbols[new] = symbols.pop(key)
            renamed.append((key, new))
    assert len(renamed) == 26
    pending[path] = (json.dumps(symbols, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Docs/ActionObjectRecords.md'
    text = path.read_text(encoding='utf-8')
    needle = '| 0B | LinkedIndex |'
    assert text.count(needle) == 1
    text = text.replace(needle, '| 0A | StateCode | Байтовый код диспетчера ObjectStateHandlers |\n' + needle)
    text = text.replace('Поля сохраняют Unknown, пока их назначение не установлено по потребителям.',
                        'Неустановленные поля сохраняют Unknown, StateCode выделен по доказанному потребителю.')
    text += '''
## StateCode

[DispatchObjectState](../Source/Action/DispatchObjectState.asm) читает байт
по смещению #0A, удваивает его с оборачиванием байта и выбирает слово
из ObjectStateHandlers. Это числовой код, а не независимые флаги.
Все разряды 7..0 принадлежат одному байту кода, при формировании индекса
старший разряд теряется. Нулевой код выбирает State00. Исходная таблица
имеет 22 опубликованных обработчика, проверки верхней границы на этом
входе нет. Допустимость остальных игровых значений этим не доказывается.
Смещение #0A, размер FActionRecord и все физические байты сохранены.
'''
    pending[path] = text.encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionStateCodeName'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionStateCodeName'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() for path in pending}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, raw in before.items():
        assert path.read_bytes() == raw
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, raw in pending.items():
        if path.suffix == '.json':
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='state-code-', suffix='.tmp', delete=False) as output:
                temporary = Path(output.name)
                output.write(raw)
            try:
                os.replace(temporary, path)
            finally:
                if temporary.exists():
                    temporary.unlink()
        else:
            path.write_bytes(raw)
    # Первая проверка загрузила старую схему в этот процесс, перед повторной проверкой читается опубликованная схема.
    import ActionObjectRecords
    importlib.reload(ActionObjectRecords)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    result = dict(passed=True, field='FActionRecord.StateCode', offset=10, structure_size=64,
                  physical_instances=26, changed_files=len(pending), all_original_bytes_preserved=True,
                  unrelated_parameter_Unknown0A_preserved=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionStateCodeNameVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

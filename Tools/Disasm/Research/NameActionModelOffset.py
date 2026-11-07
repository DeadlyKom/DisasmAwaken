"""Имя байтового смещения 9E00 по доказанным читателям и таблицам всех установленных писателей."""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile

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
                after = text.replace('FActionRecord.Unknown06', 'FActionRecord.ModelOffset')
                after = after.replace('FSpawnTemplateRow.RecordByte06', 'FSpawnTemplateRow.ModelOffset')
                after = after.replace('FSpawnModelPair.RecordByte06', 'FSpawnModelPair.ModelOffset')
                if after != text:
                    lines = []
                    for line in after.splitlines():
                        code, sep, note = line.partition(';')
                        if sep and 'ModelOffset' in code:
                            line = code.rstrip().ljust(80) + ';' + note
                        lines.append(line)
                    pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    for path in (ROOT / 'Tools/Disasm/Research').glob('*.py'):
        if path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding='utf-8')
        after = text.replace('FActionRecord.Unknown06', 'FActionRecord.ModelOffset')
        after = after.replace('FSpawnTemplateRow.RecordByte06', 'FSpawnTemplateRow.ModelOffset')
        after = after.replace('FSpawnModelPair.RecordByte06', 'FSpawnModelPair.ModelOffset')
        if after != text:
            pending[path] = after.encode('utf-8')
    for stem in ('ActionLargeEffectEntryFacts', 'ActionMissileCreationFacts', 'ActionRecordScaleFacts'):
        path = ROOT / f'Tools/Disasm/Research/{stem}.py'
        text = pending.get(path, path.read_bytes()).decode('utf-8')
        text = text.replace('Unknown06', 'ModelOffset')
        text = text.replace('поле намеренно не переименовано для всех остальных потребителей',
                            'байтовое смещение используется всеми установленными читателями заголовка')
        pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ActionSpawnScheduleFacts.py'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    assert "fields = {'0A':" in text and "('06', '07'" in text
    text = text.replace("fields = {'0A':", "fields = {'06': 'ModelOffset', '0A':")
    text = text.replace("('06', '07'", "('07'")
    pending[path] = text.encode('utf-8')
    note = 'байтовое смещение таблицы указателей 9E00, ReadObjectHeaderWord читает заголовок выбранной модели'
    path = ROOT / 'Tools/Disasm/Research/ActionObjectRecords.py'
    text = path.read_text(encoding='utf-8')
    assert text.count('KNOWN={10:') == 1
    pending[path] = text.replace('KNOWN={10:', "KNOWN={6:('ModelOffset','" + note + "'),\n       10:").encode('utf-8')
    path = ROOT / 'Source/Action/Data/ObjectRecords.asm'
    text = path.read_text(encoding='utf-8')
    needle = '; Unknown06, игровой смысл ещё неизвестен, 60AE записывает 90'
    assert text.count(needle) == 26
    pending[path] = text.replace(needle, '; ModelOffset, ' + note).encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    start = text.index('                struct FActionRecord\n')
    end = text.index('                ends', start)
    record = text[start:end]
    line = next(line for line in record.splitlines() if re.match(r'^Unknown06\s+db', line))
    record = record.replace(line, ('ModelOffset'.ljust(16) + 'db #00').ljust(80) + '; ' + note)
    text = text[:start] + record + text[end:]
    text = re.sub(r'^RecordByte06\s+db #00[^\n]*$', ('ModelOffset'.ljust(16)+'db #00').ljust(80) + '; байтовое смещение, записываемое в FActionRecord.ModelOffset', text, flags=re.M)
    pending[path] = text.encode('utf-8')
    for stem in ('SpawnPhysicalRows', 'PublishSpawnPhysicalRows'):
        path = ROOT / f'Tools/Disasm/Research/{stem}.py'
        text = pending.get(path, path.read_bytes()).decode('utf-8')
        pending[path] = text.replace('RecordByte06', 'ModelOffset').encode('utf-8')
    for relative in ('Source/Action/Data/SpawnTemplates.asm', 'Source/Action/Data/SpawnModelChoices.asm'):
        path = ROOT / relative
        text = pending.get(path, path.read_bytes()).decode('utf-8')
        pending[path] = text.replace('RecordByte06', 'ModelOffset').encode('utf-8')
    path = ROOT / 'Source/Action/PrepareRecordScale.asm'
    text = pending.get(path, path.read_bytes()).decode('utf-8').replace('Unknown06', 'ModelOffset')
    text = text.replace('поле намеренно не переименовано для всех остальных потребителей',
                        'смещение задаёт исходный заголовок модели')
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Docs/ActionRecordScale.md'
    text = path.read_text(encoding='utf-8').replace('Unknown06', 'ModelOffset')
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/Reports/Symbols.json'
    symbols = json.loads(path.read_text(encoding='utf-8'))
    count = 0
    for key in tuple(symbols):
        if key.startswith('ActionObjectRecords.') and key.endswith('.Unknown06'):
            new = key.removesuffix('.Unknown06') + '.ModelOffset'
            assert new not in symbols
            symbols[new] = symbols.pop(key)
            count += 1
    assert count == 26
    pending[path] = (json.dumps(symbols, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Docs/ActionObjectRecords.md'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    needle = '| 0A | StateCode |'
    assert text.count(needle) == 1
    text = text.replace(needle, '| 06 | ModelOffset | Байтовое смещение таблицы указателей моделей 9E00 |\n' + needle)
    text += '''
## ModelOffset

По смещению #06 хранится байтовое смещение таблицы 9E00, читаемое
[ReadObjectHeaderWord](../Source/Action/ReadObjectHeaderWord.asm).
Нулевое значение выбирает первую пару таблицы и само по себе не
означает отсутствие модели. Для обычных чётных значений номер пары
равен ModelOffset/2, но поле не переименовано в порядковый индекс.
Сам читатель не проверяет чётность, нечётное смещение и FF сохраняют
своё описанное физическое поведение. Разряды 7..0 образуют числовое
смещение, независимые флаги здесь не назначаются.

[PrepareRecordScale](../Source/Action/PrepareRecordScale.asm),
[FinishSpawnRecord](../Source/Action/FinishSpawnRecord.asm) и
[PrepareLargeEffect](../Source/Action/PrepareLargeEffect.asm) передают
поле одному читателю заголовка. Установленные писатели используют
разобранные таблицы шаблонов, пары моделей, выборку потока либо
константу #90 при создании ракеты. Конкретные игровые наименования
всех моделей этим именем не утверждаются.
'''
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Docs/ActionSpawnPhysicalRows.md'
    text = path.read_text(encoding='utf-8').replace('записываемых в Unknown06 и Unknown08', 'записываемых в ModelOffset и Unknown08')
    text += '\nПервый байт каждой параметрической пары и байт +6 шаблона оформлены полем ModelOffset, это байтовое смещение таблицы 9E00.\n'
    pending[path] = text.encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionModelOffsetName'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionModelOffsetName'
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
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='model-offset-', suffix='.tmp', delete=False) as output:
                temporary = Path(output.name)
                output.write(raw)
            try:
                os.replace(temporary, path)
            finally:
                if temporary.exists():
                    temporary.unlink()
        else:
            path.write_bytes(raw)
    import ActionObjectRecords, SpawnPhysicalRows
    importlib.reload(ActionObjectRecords)
    importlib.reload(SpawnPhysicalRows)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    result = dict(passed=True, field='FActionRecord.ModelOffset', offset=6, structure_size=64,
                  physical_instances=26, changed_files=len(pending), source_bytes_preserved=True,
                  parameter_fields_named=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionModelOffsetNameVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

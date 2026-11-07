"""Уточнение условного контракта трёх байтов без переименования Unknown и без изменения кода."""
import contextlib
import io
import json
import sys

from CheckIntro import ROOT
from ClipAliasExecutionFacts import CONTRACT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    report = json.loads((ROOT / 'Tools/Disasm/Reports/ClipAliasExecutionVerification.json').read_text(encoding='utf-8'))
    assert report['passed'] and report['execution_entry_proved'] is False
    pending = {}
    for region in ('Action', 'ThreeD'):
        path = ROOT / f'Source/{region}/UnknownCF08.asm'
        text = path.read_text(encoding='utf-8')
        start = text.index('; In:')
        start = text.rfind('\n', 0, start) + 1
        end = text.index('Entry:')
        block = []
        for heading, values in zip(('In', 'Out', 'Corrupt', 'Note'), CONTRACT):
            block.append('                ; ' + heading + ':')
            block.extend('                ;   ' + value for value in values)
            if heading == 'Note':
                document = 'ActionClipTableAlias' if region == 'Action' else 'ThreeDOverlayMirror'
                block.append(f'                ;   [Табличная роль и неоднозначность исполнения](../../Docs/{document}.md)')
        block.extend(('                ; -----------------------------------------',
                      '                ; Условное исполнение запрещает прерывания, очищает AF и снимает внешний возврат.'))
        pending[path] = (text[:start] + '\n'.join(block) + '\n' + text[end:]).encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/Contracts.py'
    text = path.read_text(encoding='utf-8')
    assert 'from ClipAliasExecutionFacts import' not in text
    pending[path] = (text + '\nfrom ClipAliasExecutionFacts import CONTRACTS as CLIP_ALIAS_EXECUTION_CONTRACTS\n'
                     'CONTRACTS.update(CLIP_ALIAS_EXECUTION_CONTRACTS)\n').encode('utf-8')
    path = ROOT / 'Docs/ActionClipTableAlias.md'
    text = path.read_text(encoding='utf-8')
    text = text.replace('Вход в этот фрагмент пока не доказан, его контракт и статус Unknown сохраняются.',
                        'Вход в этот фрагмент пока не доказан, статус Unknown сохраняется. Условный эффект трёх инструкций уточнён ниже.')
    addition = '''
## Условный эффект исполнения

[CheckClipAliasExecution](../Tools/Disasm/Research/CheckClipAliasExecution.py)
проверил 7680 условных входов, все 256 значений F, пять значений A,
два состояния IFF и три режима IM. При читаемом внешнем возврате
получены A=0, F=#44, запрещённые прерывания, SP+2 и R+3 M1.
Остальные регистры, I, IM, вся память и paging сохраняются.
Инструкции не используют временную рамку и не записывают память.
Те же байты присутствуют в копии 3DPART, их условный эффект совпадает.

Эта проверка уточняет прежний завышенный Corrupt, но не подтверждает
игровой вход. Назначение трёх байтов как младших частей указателей
уже установлено, намерение автора использовать их также как процедуру
остаётся неизвестным. Unknown не переименован и не объявлен завершённым.
'''
    pending[path] = (text + addition).encode('utf-8')
    path = ROOT / 'Docs/ThreeDOverlayMirror.md'
    text = path.read_text(encoding='utf-8')
    pending[path] = (text + '\nДля UnknownCF08 [условный эффект трёх инструкций](ActionClipTableAlias.md#условный-эффект-исполнения)\n'
        'уточнён отдельно, игровой вход и назначение совмещения по-прежнему неизвестны.\n').encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ClipAliasContract'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeClipAliasContract'
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
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    print('Два условных контракта CF08 уточнены, неизвестное назначение и исходные инструкции сохранены')


if __name__ == '__main__':
    main()

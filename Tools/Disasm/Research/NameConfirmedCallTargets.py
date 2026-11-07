"""Имена доказанных целей в контексте загрузки, без подбора символа только по числу."""
import contextlib
import io
import json
import sys

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


CALLS = {
    'StationBoot/StartStation': {
        'CALL #639F': 'CALL @Station.SelectMemoryPage.Entry',
        'CALL #DB00': 'CALL @Music.Initialize.Entry',
        'CALL #9EFF': 'CALL @Station.UnpackResource.Entry',
        'CALL #CB7F': 'CALL @Station.RestoreAllBounds.Entry',
        'CALL #9EED': 'CALL @Station.GetItemField.Entry',
        'CALL #C333': 'CALL @Map.CenterMapView.Entry',
        'JP #9A59': 'JP @Station.MainLoop.Entry'},
    'Station/HandleShipListHover': {'JP #67D0': 'JP @Station.UpdateShipListHover.Entry'},
    'Station/HandleHelpIndexHover': {'JP #6A4B': 'JP @Station.UpdateIndexListHover.Entry'},
    'Station/HandleEquipmentListHover': {'JP #7210': 'JP @Station.UpdateEquipmentHover.Entry'},
    'Station/HandleSaveSlotHover': {'JP #7482': 'JP @Station.UpdateToPositionHover.Entry'},
    'Station/HandleLoadSlotHover': {'JP #750B': 'JP @Station.UpdateFromPositionHover.Entry'},
    'Station/ActivateContextMenu': {'CALL #C85E': 'CALL @Station.CloseMenuOnRow.Entry',
                                    'CALL #C873': 'CALL @Station.DropItemDraw.Entry',
                                    'JP #CBA9': 'JP @Station.RestoreItemBounds.Entry'},
    'Station/TryDrawVariantPanel': {'CALL #CB64': 'CALL @Station.TestDrawPointer.Entry'},
    'Station/HandleItem08': {'JP #4200': 'JP @StationExit.LoadAction.Entry'},
    'Station/RemoveOtherPopups': {'CALL #C873': 'CALL @Station.DropItemDraw.Entry'},
    'Station/CloseAllItems': {'CALL #C873': 'CALL @Station.DropItemDraw.Entry'},
    'Station/ArrangeAllItems': {'JP #CB7F': 'JP @Station.RestoreAllBounds.Entry'},
    'Station/OpenEnvOptions': {'JP #CBA9': 'JP @Station.RestoreItemBounds.Entry'},
    'Station/OpenGameOptions': {'JP #CBA9': 'JP @Station.RestoreItemBounds.Entry'},
    'Station/OpenRestoreDialog': {'JP #CBA9': 'JP @Station.RestoreItemBounds.Entry'},
    'ActionBoot/InitializeRandomStates': {'CALL #EB72': 'CALL @Action.NextRandomWord0.Entry'},
    'Action/ShowNoiseBeforeReload': {'CALL #C870': 'CALL @Controls.CopyViewportToScreen.Entry'},
    'Action/SpawnAlternate': {'CALL #DE9A': 'CALL @Controls.BuildSeededIndices.Entry'},
    'Controls/ToggleTargetOverlay': {'CALL #ADC5': 'CALL @Action.ProjectOverlayCoordinates.Entry'},
}


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    pending, count = {}, 0
    for relative, replacements in CALLS.items():
        path = ROOT / ('Source/' + relative + '.asm')
        text = path.read_text(encoding='utf-8')
        for before, after in replacements.items():
            # Поиск ровно указанной инструкции, литералы в комментариях не подменяются.
            lines = text.splitlines()
            matches = [i for i, line in enumerate(lines) if line[16:].partition(';')[0].strip() == before]
            assert matches, (relative, before)
            for index in matches:
                prefix = lines[index][:16]
                _, sep, note = lines[index].partition(';')
                line = prefix + after
                if sep:
                    line = line.ljust(80) + ';' + note
                lines[index] = line
            text = '\n'.join(lines) + '\n'
            count += len(matches)
        pending[path] = text.encode('utf-8')
    path = ROOT / 'Source/Final/ReadSpeedKeys.asm'
    text = path.read_text(encoding='utf-8')
    old = 'RET Z'.ljust(64) + '; выход, если флаг Z установлен'
    assert text.count(old) == 2
    for note in ('выход, если задержка уже равна нулю, Q не уменьшает её дальше',
                 'выход, если задержка уже равна ста, A не увеличивает её дальше'):
        text = text.replace(old, 'RET Z'.ljust(64) + '; ' + note, 1)
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Source/Final/NextBitmapLine.asm'
    text = path.read_text(encoding='utf-8')
    for before, note in (('RET NZ', 'выход, если следующая строка не первая в знакоместе, адрес готов'),
                         ('RET C', 'выход, если сложение L с #20 дало перенос, следующая треть уже выбрана')):
        line = next(line for line in text.splitlines() if line[16:].partition(';')[0].strip() == before)
        text = text.replace(line, line.partition(';')[0].rstrip().ljust(80) + '; ' + note)
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Source/ActionBoot/InitializeRandomStates.asm'
    text = pending[path].decode('utf-8')
    text = text.replace(';   формула общего обработчика генератора требует отдельного анализа',
                        ';   используется доказанный поток NextRandomWord0 и общий StepFoldedRandom, игровое назначение потока не установлено')
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Docs/ControlsTargetOverlay.md'
    text = path.read_text(encoding='utf-8')
    text = text.replace('По `ADC5` координаты получаются',
                        'В [ProjectOverlayCoordinates](../Source/Action/ProjectOverlayCoordinates.asm)\nпо `ADC5` координаты получаются')
    pending[path] = (text + '\n[Договор общей проекции](ActionOverlayProjection.md) отдельно описывает оба отказа и кадр стека.\n').encode('utf-8')
    # Имена сохраняются также в исследовательском экспортёре, повторный кандидат их не потеряет.
    path = ROOT / 'Tools/Disasm/Research/ConfirmedCallTargets.py'
    pending[path] = ('''"""Доказанные цели с контекстом региона и процедуры, без изменения инструкций."""
CALLS = ''' + repr(CALLS) + '''


def name_operands(region, function_name, operation):
    for before, after in CALLS.get(region + '/' + function_name, {}).items():
        if operation == before:
            return after
    return operation
''').encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ConfirmedCallTargets'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeConfirmedCallTargets'
    assert not candidate.exists() and not history.exists()
    originals = {path: path.read_bytes() if path.exists() else None for path in pending}
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
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    print(json.dumps(dict(passed=True, named_call_targets=count, instructions_changed=0, assembly_executed=False)))


if __name__ == '__main__':
    main()

"""Физические указатели состояний EF50..EF7B перед кодом EF7C."""
from PreviewSceneTables import render as render_records, parse as parse_records

FIELDS = (('Handler', 2, 'исходный адрес обработчика состояния, проверка цели выполняется отдельно'),)
TABLE = ('ActionObjectStateHandlers', 'Source/Action/Data/ObjectStateHandlers.asm', 0x8F50, 0x8F7C,
         'FObjectStateHandler', FIELDS, tuple(f'State{index:02X}' for index in range(22)))
KNOWN_HANDLERS = {0xF57F: 'Action.ApproachTargetRecordAndResolve.Entry',
                  0xF289: 'Action.HandleLinkedPhaseState.Entry',
                  0xF138: 'Action.HandleLinkedTargetState.Entry',
                  0xF3C8: 'Action.StepTimedLinkedOverlay.Entry',
                  0xF0BE: 'Action.StepSelectedWideVector.Entry',
                  0xF49C: 'Action.SweepClass17AndPrepareSpawn.Entry',
                  0xF6EC: 'Action.StartSmallRecordEffect.Entry',
                  0xF009: 'Action.HandleLinkedRecordProximity.Entry',
                  0xF3F0: 'Action.SpawnPeriodicClass3Record.Entry',
                  0xF6BD: 'Action.AcquireLinkAndApplyOffsets.Entry',
                  0xF3A1: 'Action.StepTimedPhasePattern.Entry',
                  0xF6AB: 'Action.StepFastRecordPhases.Entry',
                  0xF67F: 'Action.StepIdleObjectOffset.Entry',
                  0xF66A: 'Action.StepTimedRecordDecay.Entry',
                  0xF07C: 'Action.UpdatePhaseAndNearVector.Entry',
                  0xF081: 'Action.UpdateLinkedOrNearPhase.Entry',
                  0xF04A: 'Action.HandleSelectedRecordProximity.Entry',
                  0xF356: 'Action.HandleClass18Proximity.Entry',
                  0xF51E: 'Action.UpdatePreferredClass18.Entry',
                  0xEFB5: 'Action.AdvanceObjectPhaseWait.Entry',
                  0xEF7D: 'Action.AdvanceObjectOffsetRise.Entry',
                  0xEF9A: 'Action.AdvanceObjectOffsetFall.Entry'}
STRUCT = ('\n                ; Физический указатель обработчика состояния объекта\n'
          '                struct FObjectStateHandler\n'
          + 'Handler'.ljust(16) + 'dw #0000'.ljust(64) + '; адрес в банке ACTION\n'
          + '                ends\n                assert FObjectStateHandler == 2\n\n')


def render(source):
    text, labels = render_records(source, TABLE, 0x6000)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[выбор обработчика состояния](../../../Docs/ActionObjectStateDispatch.md)')
    lines = []
    for line in text.splitlines():
        code, separator, note = line.partition(';')
        for address, name in KNOWN_HANDLERS.items():
            literal = '#'+format(address, '04X')
            if code.strip() == literal:
                assert separator
                line = code.rstrip().replace(literal, '@'+name).ljust(80)+';'+note
                break
        lines.append(line)
    return '\n'.join(lines)+'\n', labels


def parse(text):
    for address, name in KNOWN_HANDLERS.items():
        text = text.replace('@'+name, '#'+format(address, '04X'))
    return parse_records(text, TABLE, 0x6000)

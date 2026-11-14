"""Фазовый фон и обход значков в окне радара."""
from ControlsObjectProjectionFacts import COMMENTS as OBJECT_COMMENTS
from ControlsRasterBackgroundFacts import COMMENTS as BACKGROUND_COMMENTS, ROWS


FUNCTIONS = {0xE291: ('DrawRadar', 'Фазовый фон радара, центральная метка и вывод объектов со знаковыми линиями')}
LOCAL = {
    0xE2AF: 'Accumulate', 0xE2BB: 'DispatchIndex', 0xE2DB: 'DrawPhase00', 0xE2DC: 'RepeatPhase',
    0xE46B: 'FinishPeriod', 0xE48E: 'RestoreStack',
    0xE4B1: 'CheckEnd', 0xE4B7: 'ResetStride', 0xE4BA: 'NextRecord',
    0xE4DC: 'CheckX', 0xE4EA: 'CheckHeight', 0xE4F8: 'CheckDepth',
    0xE576: 'BeginUp', 0xE577: 'DrawUp', 0xE58C: 'RepeatUp',
    0xE5A0: 'CheckIconTop', 0xE5B1: 'CheckIconBase', 0xE5B5: 'CheckBottom',
    0xE5CA: 'BeginDown', 0xE5CB: 'DrawDown', 0xE5DF: 'RepeatDown',
    0xE5E1: 'CheckIcon', 0xE5E5: 'PrepareIcon', 0xE5FC: 'FindIcon',
    0xE632: 'DrawIconMiddle', 0xE650: 'DrawIconBottom',
}
LOCAL.update({address: f'DrawPhase{index:02d}' for index, address in enumerate(ROWS) if index})
LABELS = {('Controls', address): name for address, name in LOCAL.items()}
RENAMES = {'Controls.UnknownE291.Entry': 'Controls.DrawRadar.Entry'}
RENAMES.update({f'Controls.UnknownE291.Point{address:04X}': 'Controls.DrawRadar.' + name
                for address, name in LOCAL.items() if address != 0xE2BB})
RENAMES['Controls.UnknownE291.DispatchIndex'] = 'Controls.DrawRadar.DispatchIndex'
CONTRACTS = {('Controls', 0xE291): (
    ['банк 1 выбран, SpeedWord задаёт приращение фона, доступен список FActionRecord с конечным маркером',
     'на входном стеке внешний возврат, прерывания не вмешиваются в временный SP'],
    ['пересчитаны остаток и фаза, записаны 80 строк фона и центральная метка',
     'допущенные объекты получают линии и маскированные значки, SP восстанавливается до объектного прохода',
     'внешний RET происходит после маркера #8080, IX указывает на маркер'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, R, экран, изменяемые операнды и временные слова стека'],
    ['допустимые индексы форм от 0 до 19, при отсутствии идентификатора целей используется форма 1',
     'сквозная модель сверяет весь экран на всех фазах с одной проверяемой записью и маркером',
     'отдельные модели сверяют регистры и записи фона, линий и значков, общий IRQ не моделируется'],
)}
COMMENTS = {**BACKGROUND_COMMENTS, **OBJECT_COMMENTS}
COMMENTS[0xE4B7] = (['Восстановление шага после обработки экранных координат или значка.'], None)


def name_operands(region, address, operation):
    if region != 'Controls' or address != 0xE291:
        return operation
    operation = operation.replace('IX+#', 'IX + #')
    for offset, field in (('00', 'Components.Component0.Low'), ('01', 'Components.Component0.High'), ('12', 'ClassCode')):
        operation = operation.replace('IX + #' + offset, 'IX + @FActionRecord.' + field)
    for operand, alias in (('(#A78F)', '(@ActionPanelGaugesState.SpeedWord)'),
                           ('(#9C2B)', '(@ActionShipEquipment.TargetIdentity.Value)'),
                           ('(#E2BC)', '(@ControlsRasterReturnsState.EntryIndex)'),
                           ('(#E471)', '(@ControlsRasterReturnsState.RepeatIndex)'),
                           ('LD SP, #E271', 'LD SP, @ControlsRasterReturns.Index00'),
                           ('LD HL, #E685', 'LD HL, @ControlsObjectPixelMasks.Phase00'),
                           ('LD HL, #E68D', 'LD HL, @ControlsObjectClearMasks.Phase00')):
        operation = operation.replace(operand, alias)
    return operation

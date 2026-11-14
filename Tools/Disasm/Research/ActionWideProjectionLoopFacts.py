"""Договор обхода широких векторов, двух путей и публикации результата."""
FUNCTIONS = {0x6B16: ('ProjectWideVectors', 'Обход широких векторов с выбором масштаба, отрисовкой близких записей и публикацией выбранной')}
LOCAL = {
    0x6B31: 'SetCountdown', 0x6B3C: 'CheckVector', 0x6B4B: 'RestoreFrame',
    0x6B64: 'AdvanceVector', 0x6B6B: 'ScaleFarVector',
}
LABELS = {('Action', address): name for address, name in LOCAL.items()}
RENAMES = {'Action.Unknown6B16.Entry': 'Action.ProjectWideVectors.Entry'}
RENAMES.update({f'Action.Unknown6B16.Point{address:04X}': 'Action.ProjectWideVectors.' + name
                for address, name in LOCAL.items()})
CONTRACTS = {('Action', 0x6B16): (
    ['SeedIndex задаёт число доступных FActionWideVector, читаются два контекста и байт выбора по #9BCA',
     'страница 0 выбрана, доступны коэффициенты преобразования и код рисователя страницы 1',
     'стек содержит внешний возврат и доступен для кадров дочерних вызовов, IRQ не вмешиваются'],
    ['при нулевом счётчике публикуются три маркера #80 без обхода',
     'иначе обход всех записей и публикация старших байтов трёх результатов на выбранной итерации',
     'IY и внешний SP восстанавливаются, при отрисовке выбирается страница 1 с возвратом на страницу 0'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, R, рабочие компоненты, выходы преобразования, состояние рисователя, 7FFD при отрисовке и временный CPU-стек'],
    ['близкая запись определяется верхними словами от −60 до 59, дальняя сдвигается на четыре бита',
     'дочерние процедуры могут оставить частично обновлённые выходы при переполнении',
     'сквозная модель проверяет физические списки от нуля до шести записей и обе ветки, точный набор побочных записей и R отдельно не сверялись'],
)}
COMMENTS = {
    0x6B16: (['Установка исходного маркера во всех трёх публикуемых байтах.'], None),
    0x6B21: (['Проверка числа записей перед запуском обхода.'], None),
    0x6B25: ([], 'выход, если список широких векторов пуст'),
    0x6B27: (['Сравнение двух пар контекста перед выбором номера публикации.'], None),
    0x6B2D: ([], 'переход, если обе пары контекста совпали'),
    0x6B31: (['Расчёт обратного счётчика до выбранной записи.'], None),
    0x6B3C: (['Проверка диапазона верхних слов текущего вектора.'], None),
    0x6B3F: ([], 'переход, если хотя бы одно верхнее слово вне диапазона от −60 до 59'),
    0x6B42: (['Сохранение рамки обхода перед преобразованием и отрисовкой близкой записи.'], None),
    0x6B4B: (['Восстановление рамки обхода после обеих веток.'], None),
    0x6B50: ([], 'переход, если счётчик до публикуемой записи ещё не равен нулю'),
    0x6B52: (['Публикация старших байтов трёх результатов преобразования.'], None),
    0x6B64: (['Переход к следующей физической записи.'], None),
    0x6B6B: (['Сохранение рамки обхода и подготовка уменьшенных компонент.'], None),
}


def name_operands(region, address, operation):
    if region != 'Action' or address != 0x6B16:
        return operation
    operation = operation.replace('IY+#', 'IY + #')
    for index in range(3):
        for byte in range(4):
            operation = operation.replace(f'(IY + #{4 * index + byte:02X})',
                                          f'(IY + @FActionWideVector.Component{index}.Byte{byte})')
        for offset, field in ((0, 'Low'), (1, 'Middle')):
            operation = operation.replace(f'(#{0x9B1E + 3 * index + offset:04X})',
                                          f'(@ActionComponentWork.Component{index}.{field})')
        operation = operation.replace(f'(#{0x9B87 + index:04X})', f'(@ActionWideProjectionLoopState.Published{index})')
    for operand, alias in (('(#688B)', '(@ControlsParameterTablesState.SeedIndex)'),
                           ('(#9BCA)', '(@ActionWideProjectionLoopState.SelectedIndex)'),
                           ('#9B27', '@ActionWideVectors.Vector00'),
                           ('(#D9B7)', '(@ActionPatchedVectorState.Output0 + 1)'),
                           ('(#D7C5)', '(@ActionPatchedVectorState.Output1 + 1)'),
                           ('(#D7A3)', '(@ActionPatchedVectorState.Output2 + 1)')):
        operation = operation.replace(operand, alias)
    return operation.replace('LD DE, #000C', 'LD DE, FActionWideVector')

"""Подготовка AF43 и публикация его результата после восстановленного CPU-стека."""
FUNCTIONS = {
    0x6A6E: ('PrepareBodyTransform', 'Подготовка компонент тела и передача арифметическому преобразованию AF43'),
    0x6AB0: ('PublishTransformedBody', 'Публикация знаковых компонент, подготовка проекции и рисование преобразованного тела'),
}
LOCAL = {0x6AC5: 'StoreX', 0x6AE2: 'StoreY', 0x6AF9: 'StoreDepth', 0x6B08: 'SelectControls'}
LABELS = {('Action', address): name for address, name in LOCAL.items()}
CONTINUATIONS = {}
RENAMES = {'Action.Unknown'+format(address, '04X')+'.Entry': 'Action.'+name+'.Entry'
           for address, (name, _) in FUNCTIONS.items()}
RENAMES.update({'Action.Unknown6AB0.Point'+format(address, '04X'): 'Action.PublishTransformedBody.'+name
                for address, name in LOCAL.items()})
CONTRACTS = {('Action', 0x6A6E): (
    ['ActionTransformWorkVector.Value задаёт три знаковые 24-битные компоненты, B берётся из BC после девяти LDI',
     'в окне C000 выбран банк 0 с кодом умножения и коэффициентами AF43, IX сохраняется, настоящий CPU-стек содержит внешний возврат',
     'действуют ограничения ComputePatchedVector и MultiplySignedScaled, повторный вход и вмешательство IRQ исключены'],
    ['девять байтов перенесены в записи проекции, младшие байты очищены, Input0..2 получают исходные старшие слова',
     'SavedSP записан, IY указывает RestoreBodyStack, на входе PublishTransformedBody SP восстановлен и P/V сохраняет итог AF43',
     'HL и DE соответствуют ComputePatchedVector, B равен старшему байту разности (входной BC-9) AND FFFF, C=0',
     'AF и AF\' соответствуют ComputePatchedVector, HL\', DE\', BC\' и IX сохранены, IY=6AAD',
     'SP равен входному, I, IM, IFF и страница сохранены, портовых записей и записей по CPU-стеку нет',
     'записанные выходные слова сохраняются и при переполнении, управление достигает PublishTransformedBody без снятия внешнего возврата',
     'младшие семь битов R увеличены на 36 плюс M1 пути ComputePatchedVector по модулю 128, bit7 сохранён'],
    ['HL, DE, BC, AF, AF\', IY, R, компоненты проекции, Input0..2, от нуля до трёх Output0..2, SavedIX и SavedSP'],
    ['переход к AF43 выполняется без CALL, арифметический SP не используется для обращений к CPU-стеку',
     '35 собственных M1 и один M1 RestoreBodyStack дополняют число выборок фактического пути ComputePatchedVector',
     '8846 проходов проверены до входа PublishTransformedBody, отдельная модель проверяет его последующее поведение']),
    ('Action', 0x6AB0): (
        ['настоящий CPU-стек уже восстановлен, P/V задаёт результат AF43, три выхода AF43 находятся в банке 0',
         'младшие байты компонент проекции подготовлены, 7FFD доступен для переключения, CPU-стек допускает двадцать временных байтов'],
        ['при P/V=1 выполняется немедленный RET с сохранением регистров, RAM и страницы, SP=входной SP+2',
         'иначе старшие знаковые байты выходов записаны в First.X, First.Y и First.SignSource до преобразований',
         'знаковые слова преобразованы к знаку и модулю, вторая компонента предварительно отрицается по модулю 65536',
         'при FirstMode=2 Pattern=00FF, иначе Pattern=0000, 7FFD получает 11 и 10, A=10, F соответствует проекции и рисованию'],
        ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, IY, R, записи проекции, Pattern, CEF9, рабочая запись круга, растр, маски, изменяемые операнды, поля первого значка, верхние слова компонент, 7FFD и до двадцати временных байтов CPU-стека'],
        ['37727 сценариев включают все входные AF с P/V=1, настоящую проекцию и оба профиля рисунка',
         'проверены регистры кроме R, RAM и OUT, содержимое внутренней рамки проекции имеет отдельное ограничение']),
}
COMMENTS = {
    0x6A6E: (['Копирование трёх физических 24-битных компонент в рабочие записи проекции.'], None),
    0x6A86: (['Запись старших слов компонент в три изменяемых входных операнда AF43.'], None),
    0x6A98: (['Сохранение настоящего SP до использования регистра как накопителя.'], None),
    0x6A9C: (['Очистка младших байтов компонент проекции перед публикацией результатов.'], None),
    0x6AA6: (['Установка продолжения, которое восстановит CPU-стек после любого выхода AF43.'], None),
    0x6AB0: ([], 'выход, если AF43 обнаружил знаковое переполнение, пропустить публикацию и рисование'),
    0x6AB1: (['Сохранение знакового старшего байта X и преобразование слова в знак и модуль.'], None),
    0x6ABA: ([], 'переход, если X неотрицателен, записать исходное слово'),
    0x6AC8: (['Сохранение знакового старшего байта Y до инверсии направления и упаковки.'], None),
    0x6AD7: ([], 'переход, если инвертированный Y неотрицателен, записать его без дополнительного отрицания'),
    0x6AE5: (['Сохранение знакового старшего байта глубины и преобразование её слова.'], None),
    0x6AEE: ([], 'переход, если глубина неотрицательна, записать исходное слово'),
    0x6AFC: (['Проверка FirstMode для выбора сплошной заливки.'], None),
    0x6B04: ([], 'переход, если FirstMode не равен 2, сохранить нулевой рисунок'),
    0x6B08: (['Подключение CONTROL и вызов проекции с выбранным рисунком.'], None),
    0x6B10: (['Возврат ACTION после проекции и возможного рисования.'], None),
}


def name_operands(region, address, operation):
    if region != 'Action' or address not in FUNCTIONS:
        return operation
    fields = {'6AAE': 'ActionRestoreBodyStackState.SavedSP', '9B81': 'ActionGlyphIndicatorState.Control.FirstMode',
              '9B8A': 'ActionGlyphIndicatorState.First.X', '9B8B': 'ActionGlyphIndicatorState.First.Y',
              '9B8C': 'ActionGlyphIndicatorState.First.SignSource'}
    for index, (base, source, output) in enumerate(zip((0x9B1E, 0x9B21, 0x9B24), ('AF48', 'AF56', 'AF69'), ('D9B6', 'D7C4', 'D7A2'))):
        fields[format(base, '04X')] = 'ActionComponentWork.Component'+str(index)+'.Low'
        fields[format(base+1, '04X')] = 'ActionComponentWork.Component'+str(index)+'.Middle'
        fields[source] = 'ActionPatchedVectorState.Input'+str(index)
        fields[output] = 'ActionPatchedVectorState.Output'+str(index)
    for literal, field in fields.items():
        operation = operation.replace('(#'+literal+')', '(@'+field+')')
    return (operation.replace('LD HL, #9B6F', 'LD HL, @ActionTransformWorkVector.Value')
            .replace('LD DE, #9B1E', 'LD DE, @ActionComponentWork.Component0')
            .replace('LD IY, #6AAD', 'LD IY, @Action.RestoreBodyStack.Entry')
            .replace('LD A, #11', 'LD A, @ActionBankPage.Controls').replace('LD A, #10', 'LD A, @ActionBankPage.Runtime')
            .replace('CALL #CEFA', 'CALL @Controls.ProjectAndDrawBody.Entry'))

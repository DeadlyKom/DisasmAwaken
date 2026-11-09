"""Клавиатурный обход и вычисление смещений следующего кадра."""
FUNCTIONS = {
    0x6E6C: ('UpdateMotionFromControls', 'Обработка управления и расчёт трёх смещений из знакового слова'),
    0x6F1D: ('ScanActionKeys', 'Обход 27 клавиатурных условий и программные вызовы обработчиков'),
}
LOCAL = {0x6E72: 'ScaleMotion', 0x6E82: 'StoreFirst', 0x6E95: 'StoreSecond',
         0x6EA8: 'StoreThird', 0x6F28: 'ScanNext'}
LABELS = {('Action', address): name for address, name in LOCAL.items()}
RENAMES = {'Action.Unknown6E6C.' + name: 'Action.UpdateMotionFromControls.' + name
           for name in ('Entry', 'ScaleMotion', 'StoreFirst', 'StoreSecond', 'StoreThird')}
RENAMES.update({'Action.Unknown6F1D.Entry': 'Action.ScanActionKeys.Entry',
                'Action.Unknown6F1D.Point6F28': 'Action.ScanActionKeys.ScanNext'})
CONTRACTS = {
    ('Action', 0x6E6C): (
        ['SignedWord, коэффициенты C20..C22 и состояние управления доступны, банк 0 выбран, пары направления согласованы как 0000 либо ED44',
         'входные порты и обработчики удовлетворяют договору ScanActionKeys, стек находится в общей RAM'],
        ['при MotionOpcode=3A после двух первых вызовов Component0..2 получают произведения SignedWord на эффективные коэффициенты C20..C22',
         'для пар 0000 коэффициент не меняется, для ED44 берётся его восьмибитное отрицание, исходное 80 остаётся 80',
         'при MotionOpcode=3A IX содержит StoreThird, SP восстанавливается, окончательный RET снимает внешний возврат',
         'при MotionOpcode=C9 после двух первых вызовов следует RET без пересчёта Component0..2, IX и регистры остаются от вызываемых процедур'],
        ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, IY, R, управление и три слова результата'],
        ['хвост с исходным опкодом 3A проверен для всех 65536 значений слова, сквозной вариант без клавиш проверен отдельно',
         'входные и выходные эффекты отдельных клавиатурных обработчиков определяются их договорами',
         'произвольный опкод не покрывается договором, ToggleFreeFlightMode записывает только 3A или C9',
         'ToggleViewDirection создаёт согласованные пары направления, задний хвост отдельно проверен на всех 65536 словах'],
    ),
    ('Action', 0x6F1D): (
        ['доступны 27 входных условий и соответствующие слова целей, на стеке внешний возврат',
         'B задаётся строкой порта, младший байт порта равен #FE, доступен байт режима по #A85F',
         'при допуске обработчик должен вернуть управление на RestoreKeyScanFrame либо выполнить свой явный переход'],
        ['при ненулевом результате AND сканирование продолжается, при нулевом вызывается выбранный обработчик',
         'программный вызов сохраняет HL, DE, BC и IX, возвратная рамка восстанавливается в RestoreKeyScanFrame',
         'после последнего условия хвост LatchControlsAndDecay завершает обработку'],
        ['HL, DE, BC, AF, IX, R и стек, далее изменения зависят от обработчика и хвоста затухания'],
        ['27-е слово цели физически пересекается с кодом, отдельная запись не добавлена',
         'двадцать шесть отдельных целей описаны, последний шаг использует перекрытое слово C0C9, условие FD,02 проверено с настоящим первым обработчиком в исходном банке 0'],
    ),
}
COMMENTS = {
    0x6E6C: (['Обработка слова около нуля и опрос клавиатуры перед расчётом смещений.'], None),
    0x6E72: (['Масштабирование слова первым коэффициентом третьей строки.'], None),
    0x6E85: (['Масштабирование того же слова вторым коэффициентом.'], None),
    0x6E98: (['Масштабирование того же слова третьим коэффициентом.'], None),
    0x6F1D: (['Подготовка указателей условий и целей, первый шаг сдвигает адрес цели на два.'], None),
    0x6F28: (['Проверка окончания 27 входных условий.'], None),
    0x6F29: ([], 'переход, если все условия просмотрены, завершить затуханием'),
    0x6F2B: (['Чтение порта выбранной строки и проверка маски допуска.'], None),
    0x6F39: ([], 'переход, если маскированный результат ненулевой, пропустить обработчик'),
    0x6F3B: (['Создание рамки и программного возврата перед JP (HL).'], None),
}


def name_operands(region, address, operation):
    if region != 'Action':
        return operation
    if address == 0x6E6C:
        for index, (source, destination, continuation) in enumerate(zip(
                ('CBD8', 'CBEE', 'CC09'), ('E5B3', 'E5D2', 'E5ED'), ('6E82', '6E95', '6EA8'))):
            operation = operation.replace(f'(#{source})', f'(@ActionPatchedVectorCoeffs.C2{index})')
            operation = operation.replace(f'(#{destination})', f'(@ActionScaledVectorState.Component{index})')
            operation = operation.replace('#' + continuation, '@Action.UpdateMotionFromControls.' + LOCAL[int(continuation, 16)])
        return operation.replace('(#A78F)', '(@ActionPanelGaugesState.SignedWord)')
    if address == 0x6F1D:
        return (operation.replace('LD IX, #9D4C', 'LD IX, @ActionKeyScanInputs.Index00.RowSelect')
                .replace('LD DE, #7015', 'LD DE, @ActionKeyHandlerPointers.Index00 - 2')
                .replace('LD DE, #6F4E', 'LD DE, @Action.RestoreKeyScanFrame.Entry')
                .replace('(IX+#00)', '(IX + @FKeyScanInput.RowSelect)')
                .replace('(IX-#01)', '(IX - @ActionKeyScanConst.PrevMaskBack)'))
    return operation

LOCAL.update({28277: 'NegateFirst', 28296: 'NegateSecond', 28315: 'NegateThird'})
LABELS.update({("Action",address):name for address,name in {28277: 'NegateFirst', 28296: 'NegateSecond', 28315: 'NegateThird'}.items()})

for address in (0x6E75,0x6E88,0x6E9B):COMMENTS[address]=(['Пара изменяемого кода, 0000 даёт две NOP, ED44 даёт NEG загруженного коэффициента.'],None)

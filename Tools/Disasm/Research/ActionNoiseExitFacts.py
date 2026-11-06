"""Шумовой цикл 6054 перед возвратом к загрузчику станции."""
FUNCTIONS = {0x6054: ('ShowNoiseBeforeReload', 'Вывод шумовых кадров и ожидание клавиши перед загрузкой станции')}
LOCAL = {0x606C: 'DrawFrame', 0x60A3: 'PollDuringDelay'}
LABELS = {('Action', address): name for address, name in LOCAL.items()}
RENAMES = {
    'Action.Unknown6054.Entry': 'Action.ShowNoiseBeforeReload.Entry',
    'Action.Unknown6054.Point606C': 'Action.ShowNoiseBeforeReload.DrawFrame',
    'Action.Unknown6054.Point60A3': 'Action.ShowNoiseBeforeReload.PollDuringDelay',
}
CONTRACTS = {('Action', 0x6054): (
    ['банк 0 выбран, банк 1 содержит CONTROL и запись очереди #F2A5, ROM 1 доступен',
     'стек в общей RAM, для каждого HALT требуется пробуждение, клавиатура читается через порт #00FE'],
    ['в очередь передан элемент #F2A5, курсор AY установлен на #EE4D',
     'после не менее ста кадров любой нулевой бит из младших пяти ведёт к AAC4 при восстановленном SP',
     'I получает #3F, IY инициализируется #5C3A, перед передачей выбрана страница 0'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, IY, I, IFF, R, буфер, экран, очередь, AY и временные слова стека'],
    ['начало чтения ROM равно #0500 плюс байт R, на кадр копируются 3072 байта',
     'модель проверяет реальное копирование, вывод, AY и ввод клавиши, HALT пробуждается явно, IRQ не исполняются'],
)}
COMMENTS = {
    0x6054: (['Постановка элемента текста в очередь CONTROL.'], None),
    0x605C: (['Выбор звукового потока и подготовка режима ожидания.'], None),
    0x606C: (['Копирование очередного фрагмента ROM в линейный буфер.'], None),
    0x607A: (['Ожидание пробуждения перед выводом готового кадра.'], None),
    0x607D: (['Вывод буфера и шага текста в CONTROL, затем обновление AY в ACTION.'], None),
    0x6091: (['Проверка окончания обязательной задержки.'], None),
    0x6092: ([], 'переход, если обязательные кадры ещё не закончились'),
    0x6095: (['Проверка клавиши после обязательной задержки.'], None),
    0x609E: ([], 'переход, если младшие пять битов равны единице, ждать ещё кадр'),
    0x60A3: (['Опрос клавиатуры во время задержки, результат не выбирает следующий путь.'], None),
}


def name_operands(region, address, operation):
    if region == 'Action' and address == 0x6054:
        return operation.replace('CALL #ECA2', 'CALL @Controls.ConsumeTextQueue.Entry')
    return operation

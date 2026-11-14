"""Числовые запросы полётной строки «Бортовой компьютер»."""
FUNCTIONS = {0xACAB: ('QueueDiagnosticCounters', 'Постановка диагностических строк Status и Deads и трёх чисел в текстовую очередь')}
LOCAL = {}
CONTRACTS = {('Action', 0xACAB): (
    ['HL, DE, BC и AF числовых аргументов не задают, входные значения A и DE не являются параметрами',
     'доступны числовой ActionFlightStatus.Value.Code и слово ActionArrivalState.RankScore',
     'строки ACD6..ACE9 доступны, Controls банка 1 и его очередь соответствуют договору QueueTextItem',
     '7FFD разблокирован, на стеке внешний возврат и доступны восемнадцать байтов ниже входного SP, IRQ не вмешиваются'],
    ['HL сохраняется',
     'DE=#0200 OR LOW(исходный ActionArrivalState.RankScore), это последний переданный числовой запрос независимо от его приёма',
     'BC сохраняется',
     'AF содержит A=#10 и исходный F',
     "HL', DE', BC' сохраняются",
     "AF' содержит A'=#11 и исходный F'",
     'IX и IY сохраняются, I, IM и IFF сохраняются',
     'шесть запросов имеют порядок StatusText, число Value.Code, DeadsText, число HIGH(RankScore), число LOW(RankScore), NewLine',
     'каждый запрос независимо принимается либо молча отклоняется производителем, общего статуса приёма нет',
     'OUT 7FFD получает #11, #10 шесть раз, конечная конфигурация #10, прежняя страница не восстанавливается',
     'SP после RET равен входному SP+2, максимальная глубина временных записей восемнадцать байтов, R меняется и отдельно не доказан'],
    ["DE, A, A', R, очередь и её курсор, paging и восемнадцать временных байтов CPU-стека"],
    ['первый текст равен Status, двоеточие, пробел и LF, второй начинается CR и содержит Deads, двоеточие, пробел и LF',
     'последний запрос передаёт отдельные CR и LF, постановка указателей не равна фактическому выводу текста',
     '1088 сценариев проверили настоящие вызовы, все регистры кроме R/T, RAM вне стека и порядок запросов',
     'штатная таблица клавиш вызывает этот вход для строки «Бортовой компьютер», переход и возврат проверены',
     'остаточные значения временных слов стека, IRQ и нативный вывод этой процедурой не проверены'])}
COMMENTS = {
    0xACAB: (['Сохранение DE перед постановкой первого текстового указателя.'], None),
    0xACAC: (['Выбор исходной строки Status с завершающим LF.'], None),
    0xACB3: (['Чтение первого диагностического байта и постановка его как числа.'], None),
    0xACB9: (['Сохранение числового DE вокруг постановки второй строки.'], None),
    0xACBA: (['Выбор исходной строки CR, Deads и LF.'], None),
    0xACC1: (['Постановка старшего байта ранга отдельным числом после Deads.'], None),
    0xACC7: (['Постановка младшего байта ранга отдельным числом.'], None),
    0xACCD: (['Сохранение последнего числового DE вокруг постановки CR и LF.'], None),
    0xACCE: (['Выбор двухбайтового завершения диагностического вывода.'], None),
}


def name_operands(region, function_address, operation):
    if region == 'Action' and function_address == 0xACAB:
        operation = operation.replace('CALL #6040', 'CALL @Action.QueueTextItemBank1.Entry')
        operation = operation.replace('CALL #6000', 'CALL @Action.QueueNumberBank1.Entry')
    if region == 'Action' and function_address == 0xACAB:
        operation = operation.replace('LD DE, #ACD6', 'LD DE, @ActionDiagnosticMessages.StatusText')
        operation = operation.replace('LD DE, #ACDF', 'LD DE, @ActionDiagnosticMessages.DeadsText')
        operation = operation.replace('LD DE, #ACE8', 'LD DE, @ActionDiagnosticMessages.NewLine')
        operation = operation.replace('(#9BCD)', '(@ActionFlightStatus.Value.Code)')
        operation = operation.replace('(#9BCF)', '(@ActionArrivalState.RankScore + 1)')
        operation = operation.replace('(#9BCE)', '(@ActionArrivalState.RankScore)')
    return operation

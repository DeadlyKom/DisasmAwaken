"""6C7E, межбанковый вызов рисования шахматным рисунком."""
FUNCTIONS = {0x6C7E: ('DrawBankedProjectedBody', 'Проекция и рисование тела в банке CONTROL с шахматным рисунком')}
LOCAL = {}; LABELS = {}; CONTINUATIONS = {}
RENAMES = {'Action.Unknown6C7E.Entry': 'Action.DrawBankedProjectedBody.Entry'}
LOCATION = {0x6C7E: 'банк 5, перенесённое ядро ACTION 6000..7F8E'}
CONTRACTS = {('Action', 0x6C7E): (
    ['Component0..2 содержат исходные данные проекции, 7FFD не заблокирован',
     'банк 1 содержит CONTROL, CPU-стек в общей RAM допускает двадцать временных байтов, IRQ не вмешиваются'],
    ['HL, DE, BC, F, альтернативные и индексные пары соответствуют ProjectAndDrawBody, A=10',
     'Pattern=FFAA, CEF9=0, исходные частичные записи при отказе проекции сохраняются',
     '7FFD получает 11 и 10, верхний банк возвращён к ACTION, SP=входной SP+2'],
    ['эффекты ProjectAndDrawBody, A, регистр 7FFD и ещё одно слово вызова под рамкой рисователя'],
    ['4959 сценариев проверяют настоящий порт, исходные страницы, обе формы рисования и отказ проекции',
     'внутренние значения рамки проекции и R полного прохода остаются вне проверки']),
}
COMMENTS = {
    0x6C7E: (['Выбор AA с XOR-чередованием FF, соседние строки используют AA и 55.'], None),
    0x6C81: (['Подключение CONTROL для проекции и рисования.'], None),
    0x6C89: (['Возврат верхнего окна ACTION с сохранением F рисователя.'], None),
}
CONST_BLOCK = ('\n                ; Шахматный рисунок проецируемого тела\n'
               '                module ActionBodyPattern\n'
               + 'Checker'.ljust(16) + 'equ #FFAA'.ljust(64) + '; младший AA, XOR FF меняет фазу на 55\n'
               + '                endmodule\n\n')


def name_operands(region, address, operation):
    if region != 'Action' or address not in FUNCTIONS:
        return operation
    return (operation.replace('LD DE, #FFAA', 'LD DE, @ActionBodyPattern.Checker')
            .replace('LD A, #11', 'LD A, @ActionBankPage.Controls')
            .replace('LD A, #10', 'LD A, @ActionBankPage.Runtime')
            .replace('CALL #CEFA', 'CALL @Controls.ProjectAndDrawBody.Entry'))

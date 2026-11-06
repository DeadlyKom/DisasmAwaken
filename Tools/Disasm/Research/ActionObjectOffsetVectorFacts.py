"""Три применения масштабированного умножителя к одному слову DE."""
FUNCTIONS = {0x6D06: ('ApplyObjectOffsetVector', 'Расчёт трёх базовых слов записи по коэффициентам смещения')}
LOCAL = {0x6D17: 'Store0', 0x6D25: 'Store1', 0x6D32: 'Store2'}
STATE_FIELDS = tuple((f'Coefficient{index}', address, 'операнд LD A,n для очередного масштабированного умножения')
                     for index, address in enumerate((0x6D0E, 0x6D1C, 0x6D2A)))
CONTRACTS = {('Action', 0x6D06): (
    ['DE содержит знаковое слово масштаба, код ACTION и таблицы общей RAM доступны, CPU-стек допускает шесть временных байтов'],
    ['Base0..2 получают результаты трёх настоящих MultiplySignedScaled с одним исходным DE',
     'HL, DE, BC, AF и AF prime соответствуют последнему произведению, IX восстановлен, IYL получает значение фазовой таблицы',
     'SP=входной SP+2, I, IM, IFF и страница сохраняются'],
    ['регистры вычислителя, IYL, три операнда коэффициентов, Base0..2 и шесть временных байтов CPU-стека'],
    ['73728 сценариев, включая все исходные DE, сверяют регистры, R и стек, дети исполняются настоящими байтами'],
)}
COMMENTS = {
    0x6D06: (['Сохранение IX записи и слова масштаба перед расчётом трёх коэффициентов.'], None),
    0x6D0D: (['Расчёт первого базового слова настоящим MultiplySignedScaled с продолжением через IX.'], None),
    0x6D17: (['Запись первого базового слова и повторное использование исходного масштаба.'], None),
    0x6D25: (['Запись второго базового слова и расчёт третьего без дополнительного сохранения DE.'], None),
    0x6D32: (['Запись третьего базового слова и восстановление указателя записи.'], None),
}


def name_operands(region, address, operation):
    if region != 'Action' or address != 0x6D06:
        return operation
    for index, literal in enumerate(('E5B0', 'E5CF', 'E5EA')):
        operation = operation.replace('(#'+literal+')', '(@ActionRecordUpdateState.Base'+str(index)+')')
    return (operation.replace('JP #D12C', 'JP @Action.MultiplySignedScaled.Entry')
            .replace('CALL #B044', 'CALL @Action.BuildObjectOffsetCoefficients.Entry'))

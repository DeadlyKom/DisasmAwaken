"""Выбор порога и развилка между эффектом и диспетчером записи."""
FUNCTIONS = {0xF792: ('CheckRecordEffectThreshold', 'Выбор порога запуска большого эффекта для текущей записи')}
LOCAL = {0xF7B5: 'CompareValue'}
LABELS = {('Action', 0xF7B5): 'CompareValue'}
RENAMES = {
    'Action.UnknownF792.Entry': 'Action.CheckRecordEffectThreshold.Entry',
    'Action.UnknownF792.PointF7B5': 'Action.CheckRecordEffectThreshold.CompareValue',
}
CONTINUATIONS = {0xF792: 0xF7BF}
LOCATION = {0xF792: 'код ACTION банка 0'}
CONTRACTS = {('Action',0xF792): (
    [
        'HL, DE, BC и AF входных числовых аргументов не задают, IX указывает текущую FActionRecord',
        'читаются LinkedIndex, LinkFlags, EffectReserve и байты AntiMissilePs1 и AntiMissilePs2',
        'OtherLinkLimit и Link1ABaseLimit задают текущие байты двух изменяемых операндов LD C,n, исходно оба 0A',
        'для фактически выбранного пути эффекта действуют условия PrepareLargeEffect и ResumeAfterRecordEffect',
        'точный регистровый результат описан без вмешательства IRQ',
    ],
    [
        'на прямом переходе StoreRemainder HL и DE сохранены, B сохранён, C содержит выбранный порог, AF задаётся SUB EffectReserve,C',
        'на прямом переходе альтернативные и индексные регистры, I, IM, IFF и paging сохраняются, SP не меняется',
        'при EffectReserve меньше порога вызывается PrepareLargeEffect, далее ResumeAfterRecordEffect продолжает обход записей',
        'на пути эффекта итоговые регистры и память определяются договорами этих двух процедур',
        'выбор порога до прямого StoreRemainder либо CALL даёт 9, 13, 17, 21 или 22 M1 по пяти путям, сам CALL добавляет один M1',
        'младшие семь битов R увеличиваются на соответствующее число M1 по модулю 128, bit7 сохраняется до входа эффекта',
    ],
    [
        'BC в части C, AF и R на прямой ветви, эффекты PrepareLargeEffect и ResumeAfterRecordEffect на ветви вызова',
    ],
    [
        'при LinkedIndex, отличном от 1A, выбирается OtherLinkLimit, поле 02 ApplyParameterSet записывает операнд F798',
        'при LinkedIndex=1A и сброшенном бите 3 выбирается Link1ABaseLimit, поле 00 пишет операнд F79C',
        'при LinkedIndex=1A и установленном бите 3 наличие PS1 выбирает 1E, иначе наличие PS2 выбирает 3C, иначе 14',
        'любой байт оборудования, отличный от FF, считается наличием, PS1 имеет приоритет над PS2',
        'на выбранном изменяемом пути порог 00 не допускает эффект, порог FF допускает значения EffectReserve от 00 до FE',
        '136192 сценария выполняют реальный ApplyParameterSet и выбор ветви, тело эффекта в этой серии не исполняется',
        'прежняя сквозная серия подтверждает эффект класса 16 при исходных 0A/0A, полный R/T пути эффекта, IRQ и нативный запуск не доказаны',
    ],
)}
COMMENTS = {
    0xF797: (['Чтение изменяемого OtherLinkLimit, исходный операнд равен 0A.'], None),
    0xF79B: (['Чтение изменяемого Link1ABaseLimit для связи 1A, исходный операнд равен 0A.'], None),
    0xF792: (['Проверка индекса связи перед выбором ветви порога.'], None),
    0xF799: ([], 'переход, если индекс связи отличается от #1A, использовать OtherLinkLimit'),
    0xF79D: (['Проверка бита 3 LinkFlags.'], None),
    0xF7A1: ([], 'переход, если бит 3 LinkFlags сброшен, использовать Link1ABaseLimit'),
    0xF7A3: (['Проверка первого и второго байтов выбора порога.'], None),
    0xF7A9: ([], 'переход, если первый байт отличается от #FF, использовать #1E'),
    0xF7B1: ([], 'переход, если второй байт отличается от #FF, использовать #3C'),
    0xF7B5: (['Сравнение байта записи с выбранным порогом.'], None),
    0xF7B9: ([], 'переход, если байт не меньше порога, продолжить диспетчеризацию'),
}


def name_operands(region, address, operation):
    if region != 'Action' or address != 0xF792:
        return operation
    operation = operation.replace('BIT 3,', 'BIT @ActionLinkFlagsConst.AntimissileBit,')
    for offset, name in (('0B', 'LinkedIndex'), ('0C', 'LinkFlags'), ('13', 'EffectReserve')):
        operation = operation.replace('IX+#' + offset, 'IX + @FActionRecord.' + name)
    return operation

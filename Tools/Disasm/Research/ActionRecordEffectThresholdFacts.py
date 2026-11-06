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
CONTRACTS = {('Action', 0xF792): (
    ['IX указывает текущую запись, читаются LinkedIndex, LinkFlags, Unknown13 и два байта по #9C1A и #9C1B'],
    ['C выбирает порог #0A, #1E, #3C или #14',
     'при Unknown13 не меньше порога управление передано F7E6 с AF от SUB',
     'иначе вызывается PrepareLargeEffect и затем исполняется ResumeAfterRecordEffect'],
    ['BC, AF до сравнения, после вызова действует договор обработки эффекта'],
    ['прямой переход F7E6 сохраняет SP, путь эффекта восстанавливает SP перед продолжением'],
)}
COMMENTS = {
    0xF792: (['Проверка индекса связи перед выбором повышенного порога.'], None),
    0xF799: ([], 'переход, если индекс связи отличается от #1A, использовать #0A'),
    0xF79D: (['Проверка бита 3 LinkFlags.'], None),
    0xF7A1: ([], 'переход, если бит 3 LinkFlags сброшен, использовать #0A'),
    0xF7A3: (['Проверка первого и второго байтов выбора порога.'], None),
    0xF7A9: ([], 'переход, если первый байт отличается от #FF, использовать #1E'),
    0xF7B1: ([], 'переход, если второй байт отличается от #FF, использовать #3C'),
    0xF7B5: (['Сравнение байта записи с выбранным порогом.'], None),
    0xF7B9: ([], 'переход, если байт не меньше порога, продолжить диспетчеризацию'),
}


def name_operands(region, address, operation):
    if region != 'Action' or address != 0xF792:
        return operation
    for offset, name in (('0B', 'LinkedIndex'), ('0C', 'LinkFlags'), ('13', 'Unknown13')):
        operation = operation.replace('IX+#' + offset, 'IX + @FActionRecord.' + name)
    return operation

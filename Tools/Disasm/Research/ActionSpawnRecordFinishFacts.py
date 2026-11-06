"""Инициализация хвоста создаваемой записи перед диспетчером класса."""
FUNCTIONS = {0x7DD4: ('FinishSpawnRecord', 'Заполнение параметров новой записи и передача диспетчеру класса')}
LOCAL = {0x7DD8: 'InitParameters', 0x7E0F: 'StoreLimit', 0x7E42: 'CheckClassSix',
         0x7E5D: 'StoreState', 0x7E7A: 'StoreReuse', 0x7E89: 'ReadHeader', 0x7E97: 'StoreScale'}
LABELS = {('Action', address): name for address, name in LOCAL.items()}
RENAMES = {'Action.Unknown7DD4.Entry': 'Action.FinishSpawnRecord.Entry'}
RENAMES.update({f'Action.Unknown7DD4.Point{address:04X}': 'Action.FinishSpawnRecord.' + name
                for address, name in LOCAL.items()})
CONTRACTS = {('Action', 0x7DD4): (
    ['IX указывает создаваемую запись, класс, модель и начальное состояние уже заданы',
     'доступны потоки случайных слов 12, 13 и состояние потока 3, OBJECT3D находится в странице 4'],
    ['Entry обнуляет байт 07, InitParameters заполняет поля по классу, потоку и R',
     'ReadHeader может вызываться отдельно, байт 25 получает 1 при показателе 4, иначе 2',
     'передача в DispatchRecordClass без нового возврата, настоящий SP сохранён, выбрана страница 0'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', R, поля записи, потоки, временные слова и 7FFD'],
    ['пересечение масок #55 и #2A равно нулю, поле 11 на основном пути получает #20',
     'последовательные проверки класса #06 и #07 используют тот же A, специальные записи между ними и StoreState недостижимы'],
)}
COMMENTS = {
    0x7DD4: (['Сброс первого байта смещения перед инициализацией.'], None),
    0x7DD8: (['Продвижение потока 12, непересекающиеся маски оставляют постоянный #20.'], None),
    0x7E01: (['Получение параметров из потока 13 и проверка верхней границы.'], None),
    0x7E0B: ([], 'переход, если кандидат меньше #64'),
    0x7E26: ([], 'переход, если класс отличается от #08, сохранить общие поля'),
    0x7E47: ([], 'переход, если класс отличается от #06'),
    0x7E4B: ([], 'переход, если тот же класс отличается от #07, после предыдущей проверки переход всегда выполняется'),
    0x7E5D: (['Сохранение начального состояния и выбор байта повторного использования по R.'], None),
    0x7E70: ([], 'переход, если класс отличается от #08, оставить исходную выборку'),
    0x7E76: ([], 'переход, если бит 6 второго чтения R сброшен, оставить исходную выборку'),
    0x7E89: (['Чтение заголовка модели для выбора записываемого масштаба.'], None),
    0x7E94: ([], 'переход, если показатель отличается от 4, записать 2'),
}


def name_operands(region, address, operation):
    if region != 'Action' or address != 0x7DD4:
        return operation
    fields = {'0B': 'LinkedIndex', '0C': 'LinkFlags', '0F': 'TargetIndex', '12': 'ClassCode', '18': 'ReuseByte'}
    for offset in ('06', '07', '08', '09', '0A', '0D', '0E', '10', '11', '13',
                   '14', '15', '16', '17', '20', '21', '22', '24', '25'):
        fields[offset] = 'Unknown' + offset
    for offset, name in fields.items():
        operation = operation.replace('IX+#' + offset, 'IX + @FActionRecord.' + name)
    return operation.replace('(#EBDB)', '(@ActionRandomStreams.Stream3.LowWord)').replace(
        '(#EBDD)', '(@ActionRandomStreams.Stream3.FoldByte)')

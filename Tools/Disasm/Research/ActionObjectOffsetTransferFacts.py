"""Общий хвост обработчиков, подготовка операндов смещений и аргументов 6D06."""
FUNCTIONS = {0xF0F8: ('PrepareObjectOffsetTransform', 'Проверка маркера записи и подготовка смещений для вычислителя 6D06')}
LOCAL = {0xF11D: 'StoreCounter', 0xF132: 'LoadPhase'}
STATE_FIELDS = (('Offset0', 0xB045, 'операнд первого LD A,n вычислителя B044'),
                ('Offset1', 0xB04F, 'операнд второго LD A,n, исходный байт плюс 128'),
                ('Offset2', 0xB05C, 'операнд третьего LD A,n'))
MODIFIED_WRITERS = ((0xF101, 0xB045, 0xB044, 1), (0xF109, 0xB04F, 0xB04E, 1), (0xF10F, 0xB05C, 0xB05B, 1))
CONTRACTS = {('Action', 0xF0F8): (
    ['IX указывает FActionRecord, банк 0 выбран, код общей RAM доступен для записи'],
    ['при старшем байте первой компоненты 80 выполняется RET, AF=8042, прочие регистры и RAM сохранены',
     'иначе Offset0..2 получают байты 07, 08 плюс 128 и 09, E содержит старый счётчик 10',
     'счётчик обновляется до кандидата INC только при кандидате ниже порога 0F, иначе записывается прежнее значение',
     'D содержит байт 24 после условного сброса, SP сохранён, управление передано 6D06'],
    ['DE, AF, R, три изменяемых операнда и два поля записи'],
    ['если класс меньше 16 и состояние не 13, байт 24 обнуляется, на остальных путях сохраняется',
     '196608 сценариев сверяют регистры и R, исходные записи и переход до первой инструкции 6D06'],
)}
COMMENTS = {
    0xF0F8: (['Проверка маркера отсутствующей записи перед обновлением операндов.'], None),
    0xF0FD: ([], 'выход, если старший байт первой компоненты равен 80'),
    0xF0FE: (['Подготовка трёх байтов смещений вычислителя, второй сдвинут на 128 по модулю байта.'], None),
    0xF112: (['Расчёт кандидата следующего счётчика с сохранением старого значения в E.'], None),
    0xF11A: ([], 'переход, если байтовый кандидат меньше порога 0F, записать его'),
    0xF120: (['Проверка класса и состояния перед сбросом фазового счётчика.'], None),
    0xF125: ([], 'переход, если класс не меньше 16, сохранить фазовый счётчик'),
    0xF12C: ([], 'переход, если состояние равно 13, сохранить фазовый счётчик'),
    0xF132: (['Подготовка D для вычислителя и хвостовая передача с прежним CPU-стеком.'], None),
}


def qualify_mutations(modified, flow, functions, pieces):
    for item in modified:
        if item['region'] == 'Action' and item['writer'] in (0xF101, 0xF109, 0xF10F):
            item.update(target_bank=2, target_source_classified=False)


def name_operands(region, address, operation):
    if region != 'Action' or address != 0xF0F8:
        return operation
    operation = operation.replace('IX+#', 'IX + #')
    for literal, field in (('01', 'Components.Component0.High'), ('07', 'Unknown07'), ('08', 'Unknown08'), ('09', 'Unknown09'),
                           ('0A', 'Unknown0A'), ('0F', 'TargetIndex'), ('10', 'Unknown10'), ('12', 'ClassCode'), ('24', 'Unknown24')):
        operation = operation.replace('IX + #'+literal, 'IX + @FActionRecord.'+field)
    for index, literal in enumerate(('B045', 'B04F', 'B05C')):
        operation = operation.replace('(#'+literal+')', '(@ActionObjectOffsetTransferState.Offset'+str(index)+')')
    return operation.replace('JP #6D06', 'JP @Action.ApplyObjectOffsetVector.Entry')

"""Общие факты двух обработчиков байтового смещения."""


def build(entry, rising):
    name = 'AdvanceObjectOffsetRise' if rising else 'AdvanceObjectOffsetFall'
    description = 'Увеличение байта смещения и переход к обратному ходу по таймеру' if rising else 'Уменьшение байта смещения и возврат сохранённого состояния по таймеру'
    contracts = {('Action', entry): (
        ['IX указывает FActionRecord, байты 07, 17 и 16 доступны, банк 0 выбран'],
        ['байт 07 изменён на '+('+2' if rising else '−2')+' по модулю 256, таймер 17 уменьшен по модулю 256',
         ('при нулевом результате таймера состояние 15 и новый таймер 30 записаны' if rising else 'при нулевом результате таймера состояние восстановлено из байта 16'),
         'F соответствует DEC таймера с Carry изменения смещения, PC=F0F8, SP сохраняется'],
        ['AF, R и поля смещения, таймера и состояния'],
        ['таймер 0 оборачивается в FF, изменение состояния выполняется при исходном таймере 1',
         '11 M1 на обычном пути и 16 при переходе состояния, регистры и записи сверены во всех 65536 парах смещения и таймера'],
    )}
    comments = {
        entry: (['Изменение байта смещения на два с сохранением байтового оборачивания.'], None),
        entry+8: (['Уменьшение таймера хода, нулевой результат завершает фазу.'], None),
        entry+15: ([], 'переход, если таймер после уменьшения ненулевой, продолжить общий обработчик'),
        entry+18: (['Смена состояния после истечения таймера.'], None),
    }
    return {entry: (name, description)}, contracts, comments


def name_operands(region, address, operation):
    if region != 'Action' or address not in (0xEF7D, 0xEF9A):
        return operation
    operation = operation.replace('IX+#', 'IX + #')
    for literal, field in (('07', 'OffsetPhase0'), ('0A', 'StateCode'), ('16', 'SavedStateCode'), ('17', 'PhaseMoveTimer')):
        operation = operation.replace('IX + #'+literal, 'IX + @FActionRecord.'+field)
    return operation.replace('#F0F8', '@Action.PrepareObjectOffsetTransform.Entry')

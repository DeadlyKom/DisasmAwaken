"""Общие факты двух обработчиков байтового смещения."""
from ActionObjectOffsetTransferFacts import CONTRACTS as OFFSET_TRANSFER_CONTRACTS


def build(entry, rising):
    name = 'AdvanceObjectOffsetRise' if rising else 'AdvanceObjectOffsetFall'
    description = 'Увеличение байта смещения и переход к обратному ходу по таймеру' if rising else 'Уменьшение байта смещения и возврат сохранённого состояния по таймеру'
    common = OFFSET_TRANSFER_CONTRACTS['Action', 0xF0F8]
    common_out = [line.replace('на активной ветви R учитывает', 'на активной ветви общий хвост добавляет к R')
                  for line in common[1][1:]]
    own_transition = ('при исходном PhaseMoveTimer=1 StateCode получает 15, PhaseMoveTimer получает 1E'
                      if rising else 'при исходном PhaseMoveTimer=1 StateCode получает полный SavedStateCode, PhaseMoveTimer остаётся нулевым')
    contracts = {('Action', entry): (
        [common[0][0],
         'OffsetPhase0 и PhaseMoveTimer доступны для записи на всех путях, StateCode доступен при истечении, SavedStateCode читаем для обратного хода',
         *common[0][1:]],
        ['при маркере Component0.High=80 после собственного префикса выполняется внешний RET, AF=8042, SP=входной SP+2',
         'на маркере сохраняются HL/DE/BC, все альтернативные регистры, IX и IY, собственные фазовые и таймерные записи не отменяются',
         'полный маркерный путь даёт 15 M1 при исходном PhaseMoveTimer не равном 1, иначе 20 M1',
         *common_out,
         'OffsetPhase0 получает wrap8(старое'+(' + 2' if rising else ' - 2')+'), PhaseMoveTimer уменьшается по модулю 256',
         own_transition,
         'F0F8 читает уже обновлённые фазу и StateCode, его масштаб и результаты относятся к этому состоянию записи',
         'собственный префикс до F0F8 занимает 11 M1 без истечения и 16 при исходном таймере 1, на активном пути прибавляется полный общий хвост'],
        [common[2][0]+', OffsetPhase0, PhaseMoveTimer и условно StateCode',
         'на маркере вычислитель не вызывается, собственные записи префикса всё равно выполнены, они не являются откатом'],
        ['код состояния 15 и таймер 1E шестнадцатеричные, таймер 1E равен 30 в десятичной системе',
         'исходный таймер 0 становится FF и не выбирает смену состояния, истечение соответствует только исходной единице',
         'флаги DEC собственного таймера относятся к границе F0F8, окончательный AF задаётся маркером либо полным вычислителем',
         *[line.replace('ранний маркер возвращается до фазовых записей', 'маркер внутри F0F8 возвращается до записи общих фазовых операндов') if 'ранний маркер' in line else ('отдельная проверка F0F8, ' + line if '196608 прежних' in line else line) for line in common[3]],
         'собственные 65536 пары фазы и таймера каждого входа ранее проверены до F0F8, новая полная композиция двух входов прошла 16384 случая до RET',
         'общий сброс OffsetScaleHigh зависит от StateCode после собственного перехода, это существенно при SavedStateCode=13',
         'полное произведение входов, точные T, IRQ и нативный запуск не доказаны'],
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

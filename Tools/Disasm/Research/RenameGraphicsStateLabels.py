"""Внутренние входы отсечения, преобразования базиса и управления состоянием."""
from PublishInternalLabels import publish


def main():
    mappings, notes = {}, {}
    key = ('Voxel', 'RotateBasisVectors')
    labels = {
        'PointE52E': ('RotateFirst', 'ненулевой первый угол, смешивание компонент 0 и 1'),
        'PointE636': ('CheckSecond', 'проверка второго угла перед смешиванием компонент 1 и 2'),
        'PointE664': ('RotateSecond', 'ненулевой второй угол'),
        'PointE76C': ('CheckThird', 'проверка третьего угла перед смешиванием компонент 0 и 2'),
        'PointE798': ('RotateThird', 'ненулевой третий угол')}
    stages = (
        (('E566', 'E58F', 'E5B8', 'E5E1', 'E60A', 'E633'), (0, 1)),
        (('E69C', 'E6C5', 'E6EE', 'E717', 'E740', 'E769'), (1, 2)),
        (('E7D0', 'E7F9', 'E822', 'E84B', 'E874', 'E89D'), (0, 2)))
    notes[key] = []
    for stage, (points, components) in enumerate(stages, 1):
        for index, point in enumerate(points):
            name = f'Stage{stage}V{index // 2}C{components[index % 2]}'
            labels['Point' + point] = (name, f'запись компоненты {components[index % 2]} вектора {index // 2} на этапе {stage}')
            notes[key].append((f'JP PO, @Voxel.RotateBasisVectors.{name}', (
                'переход, если сумма произведений не дала знакового переполнения, сохранить компоненту',
                'переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту')))
    for target, ordinal in (('RotateFirst', 'первый'), ('RotateSecond', 'второй'), ('RotateThird', 'третий')):
        notes[key].append((f'JP NZ, @Voxel.RotateBasisVectors.{target}',
                           f'переход, если {ordinal} угол ненулевой, выполнить соответствующее преобразование'))
    mappings[key] = labels
    key = ('Voxel', 'ClipSprite')
    labels = {
        'PointECBC': ('CheckPositiveX', 'проверка неотрицательного X относительно окна'),
        'PointECC1': ('CheckRight', 'расчёт и проверка правой границы'),
        'PointECCB': ('TrimRight', 'сокращение ширины по правой границе'),
        'PointECD1': ('BeginVertical', 'восстановление исходного Y из операнда'),
        'PointECF1': ('CheckPositiveY', 'проверка неотрицательного Y относительно окна'),
        'PointECF6': ('CheckBottom', 'расчёт и проверка нижней границы'),
        'PointED00': ('TrimBottom', 'сокращение высоты по нижней границе'),
        'PointED06': ('BeginSteps', 'выбор видимого начала и шагов ресурса'),
        'PointED0F': ('CheckTopTrim', 'проверка признака верхнего отсечения'),
        'PointED19': ('BufferAddress', 'адрес видимого начала в попарном буфере'),
        'PointED30': ('StoreParityOp', 'запись JR NC либо JR C по чётности левого края'),
        'PointED5C': ('WideStride', '32-байтовый шаг строки широкого ресурса'),
        'PointED5E': ('SkipTopRows', 'расчёт пропущенных строк исходного ресурса'),
        'PointED7C': ('CheckLeftTrim', 'проверка горизонтального среза ресурса'),
        'PointEDC6': ('ApplyLeftSkip', 'добавление целой части горизонтального среза к источнику'),
        'PointEDD0': ('SaveStack', 'сохранение CPU-стека перед размещением шага в SP'),
        'PointEE0D': ('FinishRowStep', 'выделение байтов рассчитанного шага по строкам'),
        'PointEE13': ('StoreRowStep', 'запись старшего байта шага и подготовка правой маски'),
        'PointEE26': ('PartialMask', 'нулевая маска последней неполной пары'),
        'PointEE27': ('StoreRightMask', 'запись масок обоих вариантов последней пары'),
        'PointEE36': ('PairEntryIndex', 'перевод числа пропущенных пар в смещение развёрнутого кода'),
        'PointEE53': ('SaveMaskPatch', 'запоминание места временного изменения левой маски'),
        'PointEE67': ('StoreHalfOp', 'выбор операции полустроки и начальной палитры')}
    for index, point in enumerate(('ED90', 'ED99', 'EDA2', 'EDAB', 'EDB4', 'EDBD'), 1):
        labels['Point' + point] = (f'LeftSkipShift{index}', 'сдвиг накопителя горизонтального среза')
    for index, point in enumerate(('EDEF', 'EDF4', 'EDF9', 'EDFE', 'EE03', 'EE08'), 1):
        labels['Point' + point] = (f'RowStepShift{index}', 'сдвиг произведения целого шага Y на длину строки')
    mappings[key] = labels
    mappings[('Action', 'UpdateObjects')] = {
        'PointF72F': ('CheckEnd', 'проверка первого байта при уже найденном втором байте ограничителя'),
        'PointF735': ('NextRecord', 'переход к следующей физической записи'),
        'PointF759': ('CheckLinks', 'выбор обновления по LinkFlags')}
    mappings[('Action', 'UpdateFrame')] = {
        'PointA867': ('BeginScene', 'создание объектов и начало подготовки кадра'),
        'PointA8B2': ('StepGaugePhase', 'накопитель фазы третьей шкалы'),
        'PointA8C8': ('UpdateRecords', 'обновление объектов, движения и эффектов'),
        'PointA919': ('ApplyEventCost', 'списание стоимости события из первой шкалы'),
        'PointA928': ('CheckBlink', 'проверка бита события мигания'),
        'PointA93E': ('StoreBlink', 'запись выбранного атрибута мигания'),
        'PointA948': ('ClearBlink', 'обычный атрибут при отсутствии события мигания'),
        'PointA94D': ('CheckDrain', 'проверка события списания сорока единиц'),
        'PointA965': ('StepRegenPhase', 'накопитель фазы восстановления первой шкалы'),
        'PointA97E': ('BeginEffects', 'обновление звука и параметров модели банка 4'),
        'PointAA96': ('StorePanelAttr', 'запись атрибута панели и последующий вывод'),
        'PointAAC4': ('ReloadStation', 'передача межбанковому загрузчику станции')}
    key = ('StationBoot', 'StartStation')
    mappings[key] = {
        'Point414C': ('SumLengths', 'суммирование длин предыдущих упакованных экранов'),
        'Point4153': ('LocateScreen', 'расчёт положения выбранного экрана в секторах'),
        'Point41BD': ('StoreLineAddr', 'запись разнесённых байтов адреса экранной строки'),
        'Point41D2': ('CountLineAddr', 'продолжение после коррекции экранной адресации'),
        'Point41D8': ('ColumnGroup', 'начало группы повторений номера столбца'),
        'Point41DA': ('RepeatColumn', 'запись восьми одинаковых индексов столбца'),
        'Point4212': ('ApplyJoystick', 'сочетание результата опроса с настройкой джойстика'),
        'Point4228': ('ProbeMouseIdle', 'второй опрос порта мыши после первого результата'),
        'Point4232': ('CombineMouse', 'объединение результатов двух опросов и настройки мыши'),
        'Point4260': ('BindItemIndex', 'привязка последовательного индекса к callback элемента'),
        'Point4278': ('PrepareWorld', 'подготовка мирового ключа и возврат к станционному циклу')}
    notes[key] = [
        ('JR Z, @StationBoot.StartStation.LocateScreen', 'переход, если все предыдущие длины просуммированы, вычислить позицию экрана'),
        ('JP NZ, @StationBoot.StartStation.CountLineAddr', 'переход, если следующая строка не первая в знакоместе, адрес готов'),
        ('JR C, @StationBoot.StartStation.CountLineAddr', 'переход, если сложение E с #20 дало перенос, следующая треть уже выбрана'),
        ('JR NZ, @StationBoot.StartStation.StoreLineAddr', 'переход, если не записаны все 256 индексов строк, продолжить таблицу'),
        ('JR C, @StationBoot.StartStation.ColumnGroup', 'переход, если записаны не все 32 группы столбцов, начать следующую'),
        ('JR NZ, @StationBoot.StartStation.ApplyJoystick', 'переход, если младшие пять битов порта #1F ненулевые, оставить признак опроса равным одному'),
        ('JR Z, @StationBoot.StartStation.ProbeMouseIdle', 'переход, если порт #FBDF вернул #FF, сохранить первый признак равным одному'),
        ('JR Z, @StationBoot.StartStation.CombineMouse', 'переход, если порт #FFDF вернул #FF, сохранить второй признак равным одному'),
        ('JR Z, @StationBoot.StartStation.PrepareWorld', 'переход, если встретился маркер #80 списка элементов, закончить привязку индексов')]
    mappings[('Station', 'DrawGlyph')] = {
        'PointAEF0': ('BuildRouteIdx', 'расчёт индекса таблицы FGlyphRoute после учёта границы знакоместа')}
    notes[('Station', 'DrawGlyph')] = [
        ('JP NZ, @Station.DrawGlyph.BuildRouteIdx', 'переход, если следующая байтовая колонка не нулевая, не увеличивать вертикальную часть индекса')]
    publish('GraphicsStateInternalLabels', 'Внутренние входы графики и управления состоянием', mappings, notes)


if __name__ == '__main__':
    main()

"""Разряды арифметических операций VOXAL и управление финальным экраном."""
from PublishInternalLabels import publish


def main():
    mappings, notes = {}, {}
    key = ('Voxel', 'Multiply7BitWord')
    points = ('F939', 'F93E', 'F943', 'F948', 'F94D', 'F952')
    mappings[key] = {f'Point{point}': (f'NextBit{5 - index}', f'сдвиг накопителя перед разрядом {5 - index}')
                     for index, point in enumerate(points)}
    notes[key] = [(f'JR NC, @Voxel.Multiply7BitWord.NextBit{5 - index}',
                   f'переход, если бит {6 - index} исходного A нулевой, слагаемое BC пропускается')
                  for index in range(6)]
    notes[key].append(('RET NC', 'выход, если бит 0 исходного A нулевой, произведение уже готово'))
    key = ('Voxel', 'SignedSeededProduct')
    labels = {'PointE8AF': ('CheckBCSign', 'проверка знака второго множителя'),
              'PointE8BA': ('SplitMagnitude', 'разделение разрядов модуля второго множителя')}
    upper = ('E8CF', 'E8D7', 'E8DF', 'E8E7', 'E8EF', 'E8F7', 'E8FF', 'E907')
    lower = ('E91B', 'E926', 'E931', 'E93C', 'E947', 'E952')
    for index, point in enumerate(upper):
        labels['Point' + point] = (f'UpperShift{index + 1}', 'сдвиг первой стадии после условного сложения')
    for index, point in enumerate(lower):
        labels['Point' + point] = (f'LowerShift{index + 1}', 'сдвиг второй стадии с входным накопителем IY')
    mappings[key] = labels
    notes[key] = [('JR Z, @Voxel.SignedSeededProduct.CheckBCSign',
                   'переход, если первый множитель неотрицателен, его модуль уже готов'),
                  ('JR Z, @Voxel.SignedSeededProduct.SplitMagnitude',
                   'переход, если второй множитель неотрицателен, его модуль уже готов'),
                  ('RET P', 'выход, если знаки исходных множителей совпадают, отрицание результата не требуется')]
    notes[key] += [(f'JR NC, @Voxel.SignedSeededProduct.UpperShift{index + 1}',
                    f'переход, если разряд {13 - index} модуля BC нулевой, слагаемое DE пропускается')
                   for index in range(8)]
    notes[key] += [(f'JR NC, @Voxel.SignedSeededProduct.LowerShift{index + 1}',
                    f'переход, если разряд {5 - index} модуля BC нулевой, слагаемое DE пропускается')
                   for index in range(6)]
    key = ('Voxel', 'Divide7BitFixed')
    integer = ('F978', 'F97F', 'F986', 'F98D', 'F994', 'F99B', 'F9A2')
    stored = ('F97D', 'F984', 'F98B', 'F992', 'F999', 'F9A0', 'F9A7')
    fraction = ('F9AF', 'F9B6', 'F9BD', 'F9C4', 'F9CB', 'F9D2', 'F9D9', 'F9E0')
    labels = {}
    notes[key] = []
    for index, (point, target) in enumerate(zip(integer, stored)):
        labels['Point' + point] = (f'IntegerBit{6 - index}', 'пробное вычитание для целого разряда частного')
        labels['Point' + target] = (f'StoreInt{6 - index}', 'запись инвертированного разряда целого частного')
        if index < 6:
            notes[key].append((f'JR C, @Voxel.Divide7BitFixed.IntegerBit{6 - index}',
                               f'переход, если бит {6 - index} числителя установлен, начать деление с этого разряда'))
        notes[key].append((f'JR NC, @Voxel.Divide7BitFixed.StoreInt{6 - index}',
                           'переход, если пробное вычитание E не дало заёма, сохранить новый остаток'))
    for index, point in enumerate(fraction):
        labels['Point' + point] = (f'StoreFrac{7 - index}', 'запись инвертированного дробного разряда частного')
        notes[key].append((f'JR NC, @Voxel.Divide7BitFixed.StoreFrac{7 - index}',
                           'переход, если пробное вычитание E не дало заёма, сохранить новый остаток'))
    mappings[key] = labels
    mappings[('Final', 'InitializeFinal')] = {
        'Point607A': ('BeginFramePair', 'ожидание IRQ перед парой экранов'),
        'Point60D5': ('DelaySecond', 'задержка перед выводом второго экрана')}
    key = ('Final', 'ReadSpeedKeys')
    mappings[key] = {'Point6134': ('DecreaseDelay', 'уменьшение задержки по Q'),
                     'Point613D': ('IncreaseDelay', 'увеличение задержки по A'),
                     'Point6144': ('StoreDelay', 'запись нового значения в операнд цикла')}
    notes[key] = [('JP NC, @Final.ReadSpeedKeys.DecreaseDelay', 'переход, если нажата Q, уменьшить задержку'),
                  ('JP NC, @Final.ReadSpeedKeys.IncreaseDelay', 'переход, если нажата A, увеличить задержку'),
                  ('RET Z', '')]
    # Для одинаковых RET Z нужны отдельные контекстные пояснения до общей публикации.
    notes[key].pop()
    key = ('Final', 'BuildDisplayChain')
    mappings[key] = {'Point61E2': ('CharacterRow', 'начало знакоместного ряда'),
                     'Point61E5': ('BitmapLine', 'генерация очередной пиксельной строки'),
                     'Point61FE': ('CheckFirstSync', 'проверка места синхронизации после десятого ряда'),
                     'Point620B': ('CountRows', 'счётчик оставшихся знакоместных рядов')}
    notes[key] = [('JP NZ, @Final.BuildDisplayChain.CheckFirstSync',
                   'переход, если осталось не семь рядов, пропустить место синхронизации после восемнадцатого'),
                  ('JP NZ, @Final.BuildDisplayChain.CountRows',
                   'переход, если осталось не пятнадцать рядов, пропустить место синхронизации после десятого')]
    mappings[('ActionBoot', 'InitializeRandomStates')] = {
        'Point4316': ('WarmRandom', 'начальное число шагов генератора от одного до четырёх')}
    publish('ArithmeticFinalInternalLabels', 'Внутренние входы арифметики VOXAL и финала', mappings, notes)


if __name__ == '__main__':
    main()

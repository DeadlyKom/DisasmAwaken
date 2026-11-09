"""Начальная настройка режима, шаг потока 14 и уменьшение старших слов."""
FUNCTIONS = {0x6727: ('TransitionBodyMode', 'Переключение режима тела и изменение старших слов рабочего вектора')}
LOCAL = {0x6742: 'CheckRandom', 0x6765: 'LowerWords'}
LABELS = {('Action', address): name for address, name in LOCAL.items()}
RENAMES = {
    'Action.Unknown6727.Entry': 'Action.TransitionBodyMode.Entry',
    'Action.Unknown6727.Point6742': 'Action.TransitionBodyMode.CheckRandom',
    'Action.Unknown6727.Point6765': 'Action.TransitionBodyMode.LowerWords',
}
CONTRACTS = {('Action', 0x6727): (
    ['FirstMode, Stream14 и три старших слова вектора доступны, банк 0 выбран',
     'стек в общей RAM, генератору доступны четыре временных байта, IRQ не вмешиваются'],
    ['Entry возвращается сразу при режиме 2, иначе устанавливает режим 1 и сбрасывает Stream14 перед CheckRandom',
     'CheckRandom продвигает Stream14 и только на слове #8746 выставляет режим 2 и три слова #6000, затем передаёт управление на #688A',
     'LowerWords вычитает #0030 из трёх старших слов и передаёт управление на #679B'],
    ['HL, BC, AF, HL\', DE\', BC\', R, поля режима, SpawnLowLimit, состояние потока, вектор и временные слова по достигнутому пути'],
    ['младшие байты компонент не затрагиваются, старшие слова изменяются по модулю #10000',
     '66816 сценариев сверяют локальные границы, а оба продолжения описаны отдельно'],
)}
COMMENTS = {
    0x6727: (['Проверка режима перед начальным сбросом потока.'], None),
    0x672C: ([], 'выход, если уже включён режим 2'),
    0x672D: (['Установка режима 1 и начального состояния потока 14.'], None),
    0x6742: (['Продвижение потока и проверка слова перехода в режим 2.'], None),
    0x6748: ([], 'переход, если старший байт слова отличается от #87'),
    0x674E: ([], 'переход, если младший байт слова отличается от #46'),
    0x6751: (['Установка режима 2 и трёх начальных старших слов.'], None),
    0x6765: (['Вычитание #0030 из старших слов с сохранением младших байтов.'], None),
}


def name_operands(region, address, operation):
    if region != 'Action' or address != 0x6727:
        return operation
    aliases = {'9B81': 'ActionGlyphIndicatorState.Control.FirstMode',
               'EBF6': 'ActionRandomStreams.Stream14.LowWord',
               'EBF8': 'ActionRandomStreams.Stream14.FoldByte',
               '7B6B': 'ActionApplyParametersState.SpawnLowLimit'}
    for index in range(3):
        aliases[f'{0x9B70 + 3 * index:04X}'] = f'ActionTransformWorkVector.Value.Component{index}.LowWord + 1'
    for operand, alias in aliases.items():
        operation = operation.replace(f'(#{operand})', f'(@{alias})')
    return operation

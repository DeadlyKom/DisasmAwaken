"""Сечение с вертикальной границы и одним неподвижным горизонтальным краем."""
FUNCTIONS = {0xD404: ('DrawCornerCircleSlice', 'Рисование одного сечения с вертикальным и горизонтальным отсечением')}
LOCAL = {0xD40E: 'InsideXEntry', 0xD411: 'BuildSection', 0xD43A: 'BuildLeftMask', 0xD459: 'PrepareLeft', 0xD46A: 'BuildRightMask'}
LABELS = {('Controls', address): name for address, name in LOCAL.items()}
CONTINUATIONS = {}
RENAMES = {
    'Controls.UnknownD404.Entry': 'Controls.DrawCornerCircleSlice.Entry',
    **{'Controls.UnknownD404.Point'+format(address, '04X'): 'Controls.DrawCornerCircleSlice.'+name
       for address, name in LOCAL.items()},
}
CONTRACTS = {('Controls', 0xD404): (
    ['BC задаёт WorkX в B и WorkY в C, Carry в F prime получен из горизонтального сравнения D236',
     'Entry принимает состояние угловой ветви D2DA, InsideXEntry принимает состояние ветви D2AA между порогами квадратов',
     'Radius 9..255 и Flags берутся из записи проекции, IX задаёт рисунок, банк 1 выбран, CPU-стек допускает четырнадцать временных байтов'],
    ['HL, DE, BC, AF и альтернативные пары соответствуют выбранной половине либо одному из двух возвратов до её вызова',
     'SquareDiff=(Radius²−WorkY²−входной Carry из F prime) AND FFFF, SectionRadius содержит целый корень',
     'Entry восстанавливает WorkX и задаёт порог ноль, InsideXEntry сохраняет WorkX и задаёт порог WorkX−119 по модулю байта',
     'на ранних возвратах растр, SavedSP и Direction сохраняются, на остальных путях применяется контракт выбранной половины',
     'IXH, IY, I, IM, IFF и страница сохраняются, SP=входной SP+2, порты не записываются'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', IXL, R, рабочие поля, растр, условные операнды и четырнадцать временных байтов CPU-стека"],
    ['XPlus выбирает неподвижную сторону, YMinus выбирает начальную строку 0 и ход вниз, иначе строку 95 и ход вверх',
     'на правом пути возврат происходит после построения маски при столбце 31, на левом до построения маски при X<8',
     'крайние допустимые исходным кодом столбцы и нулевой корень сохранены, проверено 30941 сценариев с настоящими детьми',
     'регистры кроме R, восемь банков и кратность непиксельных записей сверены, IRQ не вмешиваются'],
)}
COMMENTS = {
    0xD404: (['Восстановление исходного горизонтального смещения угловой ветви прибавлением порога 120.'], None),
    0xD40E: (['Расчёт порога A prime для сечения с исходным горизонтальным смещением.'], None),
    0xD411: (['Сохранение порога и восстановление Carry горизонтальной проверки для вычисления корня.'], None),
    0xD41A: (['Сохранение радиуса сечения и подготовка начальных Y prime и отрицательного X prime.'], None),
    0xD427: (['Проверка XPlus перед выбором неподвижной стороны.'], None),
    0xD429: ([], 'переход, если XPlus сброшен, подготовить левое отсечение'),
    0xD42B: (['Расчёт левого криволинейного края как 128 плюс WorkX минус SectionRadius.'], None),
    0xD436: ([], 'переход, если YMinus установлен, построить маску на строке 0'),
    0xD444: (['Проверка номера байтового столбца левого края перед выбором правой границы.'], None),
    0xD446: ([], 'выход, если левый край уже в правом столбце 31'),
    0xD452: ([], 'вызов, если YMinus установлен, рисовать правое отсечение вниз'),
    0xD455: ([], 'вызов, если YMinus сброшен, рисовать правое отсечение вверх'),
    0xD459: (['Расчёт правого криволинейного края и проверка допуска относительно пикселя 8.'], None),
    0xD461: ([], 'выход, если правый край расположен левее пикселя 8'),
    0xD466: ([], 'переход, если YMinus установлен, построить маску на строке 0'),
    0xD46A: (['Подготовка правой маски и неподвижного левого столбца 1.'], None),
    0xD47E: ([], 'вызов, если YMinus установлен, рисовать левое отсечение вниз'),
    0xD481: ([], 'вызов, если YMinus сброшен, рисовать левое отсечение вверх'),
}


def name_operands(region, address, operation):
    if region != 'Controls' or address not in FUNCTIONS:
        return operation
    return (operation.replace('(#D17F)', '(@ControlsBodyProjection.Value.Flags)')
            .replace('(#D182)', '(@ControlsCircleWork.Value.WorkX)')
            .replace('(#D185)', '(@ControlsCircleWork.Value.SectionRadius)')
            .replace('(#D18C)', '(@ControlsCircleWork.Value.Mode)')
            .replace('ADD A, #78', 'ADD A, @ControlsHorizontalCircleConst.OffsetLimit')
            .replace('SUB #77', 'SUB @ControlsHorizontalCircleConst.ReleaseBias')
            .replace('BIT 0, E', 'BIT @ControlsProjectConst.XPlusBit, E')
            .replace('BIT 1, ', 'BIT @ControlsProjectConst.YMinusBit, '))

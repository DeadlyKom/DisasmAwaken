"""Вертикальное сечение D485, включая касательный возврат после оборачивания квадрата."""
FUNCTIONS = {0xD485: ('DrawVerticalCircleSlice', 'Рисование вертикально отсечённого кругового сечения с двумя криволинейными краями')}
LOCAL = {0xD4A1: 'SetBoundary'}
LABELS = {('Controls', 0xD4A1): 'SetBoundary'}
CONTINUATIONS = {}
RENAMES = {
    'Controls.UnknownD485.Entry': 'Controls.DrawVerticalCircleSlice.Entry',
    'Controls.UnknownD485.PointD4A1': 'Controls.DrawVerticalCircleSlice.SetBoundary',
}
CONTRACTS = {('Controls', 0xD485): (
    ['BC задаёт B=OffsetX в 0..119 и C=WorkY, входной Carry установлен',
     'Radius в 9..255 не меньше WorkY, Radius²−WorkY² меньше (120−OffsetX)²',
     'CenterX равен 128±OffsetX согласно XPlus, YMinus выбирает направление, IX задаёт рисунок и чередование',
     'банк 1 выбран, на CPU-стеке внешний возврат и место для четырнадцати временных байтов, IRQ не вмешиваются'],
    ['HL, DE, BC содержат конечные адреса и маски половины, AF восстановлен от проверки YMinus',
     "HL', DE', BC' содержат конечное состояние половины, AF', IXH и IY сохранены, IXL чередуется после каждой строки",
     'SquareDiff=(Radius²−WorkY²−1) AND FFFF, SectionRadius содержит целый корень, CenterY равен 0 либо 95',
     'при равенстве Radius и WorkY SectionRadius=FF, края расположены в обратном порядке, растр и SavedSP сохранены',
     'SP=входной SP+2, I, IM, IFF и страница сохранены, порты не записываются'],
    ["HL, DE, BC, AF, HL', DE', BC', IXL, R, рабочие поля круга, растр и условные операнды ядра, четырнадцать временных байтов CPU-стека"],
    ['проверено 136370 сценариев, включая 118619 касаний, регистры кроме R, все банки и кратность непиксельных записей',
     'полный диспетчер, R и кратность пиксельных записей остаются за пределами этого договора'],
)}
COMMENTS = {
    0xD485: (['Чтение радиуса и флагов из записи проекции после сравнения квадратов вызывающим кодом.'], None),
    0xD489: (['Расчёт корня разности квадратов с исходным заёмом, равенство радиуса и смещения даёт обёрнутую разность FFFF.'], None),
    0xD490: (['Подготовка начального Yprime из WorkY и отрицательного Xprime из радиуса сечения.'], None),
    0xD49A: (['Проверка YMinus для выбора начальной строки и последующего направления.'], None),
    0xD49D: ([], 'переход, если YMinus установлен, начать на верхней строке 0'),
    0xD4A1: (['Запись граничной строки в CenterY для обоих построителей масок.'], None),
    0xD4A5: (['Расчёт левого края как CenterX минус SectionRadius по модулю байта.'], None),
    0xD4B0: (['Расчёт правого края как CenterX плюс SectionRadius на той же граничной строке.'], None),
    0xD4BF: (['Проверка YMinus перед выбором половины, рисователь восстанавливает AF для второй проверки.'], None),
    0xD4C4: ([], 'вызов, если YMinus установлен, рисовать вниз от строки 0'),
    0xD4C7: ([], 'вызов, если YMinus сброшен, рисовать вверх от строки 95'),
}


def name_operands(region, address, operation):
    if region != 'Controls' or address not in FUNCTIONS:
        return operation
    return (operation.replace('(#D17F)', '(@ControlsBodyProjection.Value.Flags)')
            .replace('(#D183)', '(@ControlsCircleWork.Value.CenterY)')
            .replace('(#D184)', '(@ControlsCircleWork.Value.CenterX)')
            .replace('(#D185)', '(@ControlsCircleWork.Value.SectionRadius)')
            .replace('BIT 1, ', 'BIT @ControlsProjectConst.YMinusBit, '))

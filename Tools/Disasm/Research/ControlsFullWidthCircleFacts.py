"""Полноширинная середина круга и сечение от вертикальной границы."""
FUNCTIONS = {
    0xD340: ('DrawFullWidthCircle', 'Заливка внутренних полос и двух остаточных половин широкого круга'),
    0xD38C: ('DrawFullWidthCircleSlice', 'Заливка внутренней полосы от вертикальной границы и одной остаточной половины'),
}
LOCAL = {0xD34A: 'InsideXEntry', 0xD34E: 'BuildSection', 0xD396: 'InsideXEntry', 0xD399: 'BuildSection', 0xD3C3: 'StartAtBottom'}
LABELS = {('Controls', address): name for address, name in LOCAL.items()}
CONTINUATIONS = {}
RENAMES = {}
for entry, (name, _) in FUNCTIONS.items():
    prefix = 'Controls.Unknown'+format(entry, '04X')
    RENAMES[prefix+'.Entry'] = 'Controls.'+name+'.Entry'
    end = 0xD38C if entry == 0xD340 else 0xD3DA
    for address, label in LOCAL.items():
        if entry < address < end:
            RENAMES[prefix+'.Point'+format(address, '04X')] = 'Controls.'+name+'.'+label

CONTRACTS = {}
for entry in FUNCTIONS:
    whole = entry == 0xD340
    CONTRACTS['Controls', entry] = (
        ['BC задаёт WorkX в B и WorkY в C, состояние соответствует выбранному входу из D236',
         'Radius 9..255 и Flags заданы проекцией, XPlus выбирает активную сторону остаточной половины',
         ('CenterY находится в строках 0..95, начальный DE содержит Radius и Flags' if whole else
          'YMinus задаёт старт на строке 0 или 95, радиус и флаги перечитываются из проекции'),
         'IX задаёт рисунок и чередование, банк 1 выбран, CPU-стек допускает четырнадцать временных байтов, IRQ не вмешиваются'],
        ['HL, DE, BC, AF и альтернативные пары содержат состояние последнего прохода, выход с активным EXX сохраняет перестановку',
         'SquareDiff и SectionRadius получают разность квадратов и её целый корень, Entry восстанавливает WorkX, InsideXEntry сохраняет его',
         'полосы меняют только внутренние столбцы 1..30, последующая половина продолжает рисунок со следующей строки',
         'IXH, IY, I, IM, IFF и страница сохраняются, SP=входной SP+2, порты не записываются'],
        ["HL, DE, BC, AF, HL', DE', BC', AF', IXL, R, растр, рабочие поля, операнды полос и ядер, четырнадцать временных байтов CPU-стека"],
        ['порог A prime нулевой при Entry, при InsideXEntry равен WorkX−119 по модулю байта',
         'радиус полного внутреннего участка вычисляется по горизонтальному плечу 120+WorkX',
         ('первый проход идёт вверх от CenterY, второй вниз, фаза IXL между ними сохраняется' if whole else
          'число строк полосы равно SectionRadius−WorkY, направление начинается от соответствующей вертикальной границы'),
         'половина получает B=0, C=FF и байтовые края 1 и 31, за пределами растра её начальная проверка возвращает без пикселей',
         '7016 сценариев на четыре входа сверяют регистры кроме R, все банки и непиксельные записи'],
    )

COMMENTS = {
    0xD340: (['Восстановление исходного WorkX и установка нулевого порога снятия отсечения.'], None),
    0xD34A: (['Расчёт порога снятия отсечения по исходному горизонтальному смещению.'], None),
    0xD34E: (['Сохранение порога и расчёт длины полноширинной полосы по дальнему горизонтальному плечу.'], None),
    0xD358: (['Подготовка длины полосы для прохода вверх от строки центра.'], None),
    0xD35F: (['Подготовка двух неподвижных байтовых краёв на строке после полосы.'], None),
    0xD370: (['Восстановление длины полосы и строки центра для второго прохода вниз.'], None),
    0xD37A: (['Подготовка остаточной нижней половины с текущей фазой рисунка.'], None),
    0xD38C: (['Восстановление WorkX угловой ветви и установка нулевого порога.'], None),
    0xD396: (['Расчёт порога для вертикального сечения с исходным горизонтальным смещением.'], None),
    0xD399: (['Сохранение порога, чтение проекции и расчёт радиуса полноширинной части.'], None),
    0xD3A7: (['Расчёт оставшейся длины полосы от вертикальной границы, проверка направления YMinus.'], None),
    0xD3AB: ([], 'переход, если YMinus сброшен, начинать от нижней строки 95'),
    0xD3B1: (['Подготовка остаточной нижней половины после полосы.'], None),
    0xD3C3: (['Начало верхнего прохода от нижней границы растра.'], None),
    0xD3C8: (['Подготовка остаточной верхней половины после полосы.'], None),
}
for left, right, direction in ((0xD36A, 0xD36D, 'вверх'), (0xD385, 0xD388, 'вниз'),
                               (0xD3BC, 0xD3BF, 'вниз'), (0xD3D3, 0xD3D6, 'вверх')):
    COMMENTS[left] = ([], 'вызов, если XPlus сброшен, продолжить левое отсечение '+direction)
    COMMENTS[right] = ([], 'вызов, если XPlus установлен, продолжить правое отсечение '+direction)


def name_operands(region, address, operation):
    if region != 'Controls' or address not in FUNCTIONS:
        return operation
    return (operation.replace('(#D17F)', '(@ControlsBodyProjection.Value.Flags)')
            .replace('(#D182)', '(@ControlsCircleWork.Value.WorkX)')
            .replace('(#D183)', '(@ControlsCircleWork.Value.CenterY)')
            .replace('(#D185)', '(@ControlsCircleWork.Value.SectionRadius)')
            .replace('ADD A, #78', 'ADD A, @ControlsHorizontalCircleConst.OffsetLimit')
            .replace('LD A, #78', 'LD A, @ControlsHorizontalCircleConst.OffsetLimit')
            .replace('SUB #77', 'SUB @ControlsHorizontalCircleConst.ReleaseBias')
            .replace('BIT 0, A', 'BIT @ControlsProjectConst.XPlusBit, A')
            .replace('BIT 1, E', 'BIT @ControlsProjectConst.YMinusBit, E'))

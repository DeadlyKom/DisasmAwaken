"""Две половины с одним горизонтальным отсечением, входы D3DA и D3E4."""
FUNCTIONS = {0xD3DA: ('DrawHorizontallyClippedCircle', 'Рисование двух половин круга с одним исходно неподвижным горизонтальным краем')}
LOCAL = {0xD3E4: 'InsideEntry', 0xD3E7: 'SelectSide', 0xD3F8: 'PrepareLeft'}
LABELS = {('Controls', address): name for address, name in LOCAL.items()}
CONTINUATIONS = {}
RENAMES = {
    'Controls.UnknownD3DA.Entry': 'Controls.DrawHorizontallyClippedCircle.Entry',
    **{'Controls.UnknownD3DA.Point'+format(address, '04X'): 'Controls.DrawHorizontallyClippedCircle.'+name
       for address, name in LOCAL.items()},
}
CONTRACTS = {('Controls', 0xD3DA): (
    ['BC задаёт рабочее горизонтальное смещение в B, DE задаёт XPlus в бите 0 E',
     'Entry принимает 0<Radius−WorkX<240, InsideEntry принимает OffsetX<120, OffsetX+Radius>=120 и Radius−OffsetX<120',
     'физическая запись содержит исходный Radius 9..255 и Flags, WorkX соответствует B, CenterY находится в строках 0..95',
     'IX задаёт рисунок и чередование, банк 1 выбран, на CPU-стеке внешний возврат и восемь временных байтов, IRQ не вмешиваются'],
    ['HL, DE, BC и AF содержат результат верхней половины, ранние выходы с активным EXX сохраняют переставленные пары',
     "HL', DE', BC' содержат сопряжённое состояние верхней половины, A' задаёт порог, F' зависит от сравнений с ним",
     'IXH и IY сохранены, IXL продолжает чередование через обе половины, Direction=0, SavedSP=входной SP−2',
     'WorkX при Entry восстановлен прибавлением 120 по модулю байта, при InsideEntry сохранён',
     'SP=входной SP+2, I, IM, IFF и страница сохранены, порты не записываются'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', IXL, R, растр, WorkX, Direction, SavedSP, SavedB на левом пути, операнды ядер и восемь временных байтов CPU-стека"],
    ['порог A prime равен нулю у Entry и OffsetX−119 по модулю байта у InsideEntry',
     'XPlus выбирает неподвижный правый край, при сброшенном XPlus неподвижен левый край',
     'подготовка перед верхней половиной заново задаёт адреса, маски, Cprime и Eprime, сохраняя IXL и A prime',
     'верхняя половина принимает исходный внешний возврат через хвостовой JP',
     '50808 сценариев подтверждают регистры кроме R, восемь банков, пиксельные интервалы и кратность непиксельных записей'],
)}
COMMENTS = {
    0xD3DA: (['Восстановление горизонтального смещения из внешней ветви прибавлением порога 120.'], None),
    0xD3E1: (['Установка порога снятия отсечения для внешней ветви.'], None),
    0xD3E4: (['Расчёт порога снятия отсечения по исходному горизонтальному смещению внутренней ветви.'], None),
    0xD3E7: (['Сохранение порога в A prime и выбор неподвижной стороны по XPlus.'], None),
    0xD3EA: ([], 'переход, если XPlus сброшен, подготовить неподвижный левый край'),
    0xD3EC: (['Подготовка правого отсечения и рисование от центра вниз.'], None),
    0xD3F2: (['Повторная подготовка правого отсечения для верхней половины, текущая фаза рисунка сохраняется.'], None),
    0xD3F5: (['Хвостовая передача верхней половине с исходным внешним возвратом.'], None),
    0xD3F8: (['Подготовка левого отсечения и рисование от центра вниз.'], None),
    0xD3FE: (['Повторная подготовка левого отсечения для верхней половины, текущая фаза рисунка сохраняется.'], None),
    0xD401: (['Хвостовая передача верхней половине с исходным внешним возвратом.'], None),
}
CONST_BLOCK = ('\n                ; Порог и поправка горизонтального сечения\n'
               '                module ControlsHorizontalCircleConst\n'
               + 'OffsetLimit'.ljust(16) + 'equ #78'.ljust(64) + '; порог внешнего горизонтального смещения\n'
               + 'ReleaseBias'.ljust(16) + 'equ #77'.ljust(64) + '; вычитаемое при подготовке порога A prime\n'
               + '                endmodule\n\n')


def name_operands(region, address, operation):
    if region != 'Controls' or address not in FUNCTIONS:
        return operation
    return (operation.replace('(#D182)', '(@ControlsCircleWork.Value.WorkX)')
            .replace('ADD A, #78', 'ADD A, @ControlsHorizontalCircleConst.OffsetLimit')
            .replace('SUB #77', 'SUB @ControlsHorizontalCircleConst.ReleaseBias')
            .replace('BIT 0, E', 'BIT @ControlsProjectConst.XPlusBit, E'))

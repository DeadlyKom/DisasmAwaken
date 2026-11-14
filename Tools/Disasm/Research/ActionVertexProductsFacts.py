"""Девять произведений ACTION с падением исполнения в ProjectRenderVertexGroup."""
FUNCTIONS={0xD5F9:('PrepareRenderVertexProducts','Подготовка трёх пар координат и трёх глубин табличным произведением матрицы и входных компонентов')}
LOCAL={}
FALLTHROUGH=True
UNCLASSIFIED_PREFIX_PATH='Source/Resources/17_ACTION/Unclassified028_BeforeVertexProducts.bin'
MODIFIED_WRITERS=((0xD609,0xD69D,0xD69B,1),(0xD61A,0xD6A0,0xD69E,1),(0xD62B,0xD6A3,0xD6A1,1),
    (0xD63C,0xD69C,0xD69B,1),(0xD64D,0xD69F,0xD69E,1),(0xD65E,0xD6A2,0xD6A1,1),
    (0xD66F,0xD6E2,0xD6E0,1),(0xD680,0xD6E1,0xD6E0,1),(0xD691,0xD6DF,0xD6DE,1))
CONTRACTS={('Action',0xD5F9):(
    ['D содержит третью локальную компоненту signed8, половина получается арифметическим сдвигом с округлением вниз',
     'BC содержит первую компоненту signed8 в B и вторую signed8 в C, половины округляются вниз',
     'девять операндов ActionRenderMatrixState.Coeff11..Coeff33 подготовлены ComposeRenderMatrix',
     'исходная таблица ActionProjectionSquares находится по 9800 и сохраняет все 256 исходных значений',
     'код ACTION банка 0 доступен на запись, IRQ не вмешиваются, SP сохраняется до продолжения в генераторе',
     'IXL и параметры перспективы задают договор следующей ProjectRenderVertexGroup'],
    ['HL=#9800+s для последнего произведения P(Coeff32,D), где s его индекс суммы по формуле Note',
     'DE сохраняет входной D, E содержит T(d) последнего произведения, d его индекс разности',
     'BC сохраняется',
     'AF содержит A=P(Coeff32,D) и F последнего SUB T(s)-T(d), N=1, PV=0, S и Carry совпадают и означают отрицательную разность, Z означает A=0',
     "HL', DE', BC', AF' сохраняются",
     'IX и IY сохраняются, SP, I, IM, IFF и paging сохраняются до границы D694',
     'R получает ровно 127 M1, один от LD H,98 и девять раз по 14, бит 7 R сохраняется',
     'PackedFirst содержит P(Coeff21,B) младшим байтом и P(Coeff11,B) старшим',
     'PackedSecond содержит P(Coeff23,C) младшим байтом и P(Coeff13,C) старшим',
     'PackedThird содержит P(Coeff22,D) младшим байтом и P(Coeff12,D) старшим',
     'DepthFirst, DepthSecond и DepthThird получают P(Coeff31,B), P(Coeff33,C) и P(Coeff32,D)',
     'управление последовательно переходит в ProjectRenderVertexGroup без CALL и без RET, его дальнейшие эффекты не включены в состояние границы D694'],
    ['HL, E, AF, R и девять существующих байтов операндов генератора до продолжения, дальнейшие изменения задаёт ProjectRenderVertexGroup'],
    ['результаты этого договора относятся к границе D694, а не к возврату полного вызова',
     'P(a,b)=wrap8(T(wrap8(floor(signed8(a)/2)-floor(signed8(b)/2)+b))-T(wrap8(floor(signed8(a)/2)-floor(signed8(b)/2))))',
     'T(i)=floor(min(i,255-i)^2/127), аргументы не переставляются, обычное умножение или округление к нулю неэквивалентно',
     'физический порядок столбцов 1, 3, 2 сохранён, все девять произведений вычисляются независимо без накопления',
     '72704 сценария проверяют все пары примитива, независимые срезы коэффициентов и компонентов, точные флаги, R, всю RAM и кратность записей',
     'T имеет значения 0..127, математическая разность лежит в -127..127, код 80 невозможен у любого из девяти произведений',
     'проверка останавливается перед генератором, полный проход объекта доказывается отдельно'])}
COMMENTS={0xD5F9:(['-----------------------------------------','Строка первой упакованной оси','Подготовка страницы исходной таблицы квадратов, столбцы используются в порядке 1, 3, 2.'],None)}
for address,row,column,factor,target in (
    (0xD5FB,1,1,'B','PackedFirst старший байт'),(0xD60C,1,3,'C','PackedSecond старший байт'),(0xD61D,1,2,'D','PackedThird старший байт'),
    (0xD62E,2,1,'B','PackedFirst младший байт'),(0xD63F,2,3,'C','PackedSecond младший байт'),(0xD650,2,2,'D','PackedThird младший байт'),
    (0xD661,3,1,'B','DepthFirst'),(0xD672,3,3,'C','DepthSecond'),(0xD683,3,2,'D','DepthThird')):
    before=[]
    if address in (0xD62E,0xD661):
        before+=['-----------------------------------------','Строка '+('второй упакованной оси' if row==2 else 'глубины')]
    before+=['Расчёт P(Coeff'+str(row)+str(column)+', '+factor+'), арифметические половины и два чтения таблицы сохраняют исходное округление.']
    COMMENTS[address]=(before,None)
    COMMENTS[address+14]=(['Сохранение результата в '+target+' существующего операнда генератора.'],None)


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0xD5F9:
        operation=operation.replace('LD H, #98','LD H, @ActionProjectionClipConst.SquarePage')
        for address,label in ((0xD69D,'PackedFirst+1'),(0xD6A0,'PackedSecond+1'),(0xD6A3,'PackedThird+1'),
            (0xD69C,'PackedFirst'),(0xD69F,'PackedSecond'),(0xD6A2,'PackedThird'),
            (0xD6E2,'DepthFirst'),(0xD6E1,'DepthSecond'),(0xD6DF,'DepthThird')):
            operation=operation.replace('(#'+format(address,'04X')+')','(@ActionVertexGroupState.'+label+')')
    return operation

"""Девять произведений ACTION с падением исполнения в ProjectRenderVertexGroup."""
FUNCTIONS={0xD5F9:('PrepareRenderVertexProducts','Подготовка трёх пар координат и трёх глубин табличным произведением матрицы и входных компонентов')}
LOCAL={}
FALLTHROUGH=True
UNCLASSIFIED_PREFIX_PATH='Source/Resources/17_ACTION/Unclassified028_BeforeVertexProducts.bin'
MODIFIED_WRITERS=((0xD609,0xD69D,0xD69B,1),(0xD61A,0xD6A0,0xD69E,1),(0xD62B,0xD6A3,0xD6A1,1),
    (0xD63C,0xD69C,0xD69B,1),(0xD64D,0xD69F,0xD69E,1),(0xD65E,0xD6A2,0xD6A1,1),
    (0xD66F,0xD6E2,0xD6E0,1),(0xD680,0xD6E1,0xD6E0,1),(0xD691,0xD6DF,0xD6DE,1))
CONTRACTS={('Action',0xD5F9):(
    ['B, C и D содержат три локальных компонента, каждый байт трактуется как signed8 при арифметическом делении на два',
     'девять операндов ActionRenderMatrixState.Coeff11..Coeff33 подготовлены ComposeRenderMatrix',
     'исходная таблица ActionProjectionSquares находится по 9800 и сохраняет все 256 исходных значений',
     'код ACTION банка 0 доступен на запись, IRQ не вмешиваются, SP сохраняется до продолжения в генераторе',
     'IXL и параметры перспективы задают договор следующей ProjectRenderVertexGroup'],
    ['HL указывает в страницу 98 по последнему индексу суммирования, E содержит последнее чтение квадрата разности',
     'B, C и D сохраняются, A содержит последнее произведение P(Coeff32,D), F содержит точные флаги вычитания двух табличных байтов',
     'PackedFirst содержит P(Coeff21,B) младшим байтом и P(Coeff11,B) старшим',
     'PackedSecond содержит P(Coeff23,C) младшим байтом и P(Coeff13,C) старшим',
     'PackedThird содержит P(Coeff22,D) младшим байтом и P(Coeff12,D) старшим',
     'DepthFirst, DepthSecond и DepthThird получают P(Coeff31,B), P(Coeff33,C) и P(Coeff32,D)',
     "HL', DE', BC', AF', IX, IY, SP, I, IM, IFF и paging сохраняются до следующего файла, R увеличивается на 127 по модулю младших семи бит",
     'управление последовательно переходит в ProjectRenderVertexGroup без CALL и без RET, его выход является выходом полного вызова'],
    ['HL, E, AF, R и девять существующих байтов операндов генератора до продолжения, дальнейшие изменения задаёт ProjectRenderVertexGroup'],
    ['результаты этого договора относятся к границе D694, а не к возврату полного вызова',
     'P(a,b)=wrap8(T(wrap8(floor(signed8(a)/2)-floor(signed8(b)/2)+b))-T(wrap8(floor(signed8(a)/2)-floor(signed8(b)/2))))',
     'T(i)=floor(min(i,255-i)^2/127), аргументы не переставляются, обычное умножение или округление к нулю неэквивалентно',
     'физический порядок столбцов 1, 3, 2 сохранён, все девять произведений вычисляются независимо без накопления',
     '72704 сценария проверяют все пары примитива, независимые срезы коэффициентов и компонентов, точные флаги, R, всю RAM и кратность записей',
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

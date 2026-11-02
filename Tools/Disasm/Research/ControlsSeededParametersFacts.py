"""Полная подготовка индексов из зерна и координатной области, DE9A."""
FUNCTIONS = {0xDE9A: ('BuildSeededIndices', 'Формирование четырёх индексов из двухсловного зерна, координатной области и числа шагов генератора')}
LOCAL = {0xDEA7:'SaveSeed',0xDEBD:'StepLoop',0xDED4:'StoreHighIndex'}
LABELS = {('Controls',address):name for address,name in LOCAL.items()}
CONTINUATIONS = {}
RENAMES = {'Controls.UnknownDE9A.Entry':'Controls.BuildSeededIndices.Entry',
    **{'Controls.UnknownDE9A.Point'+format(a,'04X'):'Controls.BuildSeededIndices.'+name for a,name in LOCAL.items()}}
CONTRACTS = {('Controls',0xDE9A): (
    ['HL задаёт первое слово зерна X, DE задаёт второе слово Y, BC сохраняется',
     'AF задаёт A как управляющий байт, число шагов K=A+1 в диапазоне 1..256, входной F на выходы не влияет',
     'банк 1 выбран, общее ядро ACTION перенесено в 6000, физический FWordRandomState доступен для записи',
     'на стеке внешний возврат, ещё шесть байтов нужны для сохранения BC и настоящих вложенных вызовов, IRQ не вмешиваются'],
    ['при T=(HIGH X XOR LOW X XOR HIGH Y XOR LOW Y) AND 7 и V=NOT выходного байта последнего StepWordRandom',
     'H=4 при исходном ClassifyCoordinateRegion(X)=OutsideCode, иначе H=V DIV 64, L=((V DIV 4) AND 15)+1',
     'D=HIGH Second после последнего шага, E=V AND 3, BC сохраняется',
     'A=MAX(T-1, 0), F=44 при T=0, F=42 при T=1, F=02 при T>=2',
     "HL', DE', BC' сохраняются, A'=V AND 3, F' соответствует AND этого A' с установленным H и сброшенными N, C",
     'IX, IY, I, IM и IFF сохраняются, SP=входной SP+2',
     'физические First и Second содержат состояние после K шагов, исходное состояние заменяется зерном X, Y перед циклом',
     'R получает 41+M+34*K+(T=0)+2*O M1, M задаёт ClassifyCoordinateRegion(X), O=1 ровно вне трёх областей'],
    ["HL, DE, AF, AF', четыре байта состояния, шесть байтов CPU-стека, R"],
    ['управляющий FF даёт B=0 перед DJNZ и ровно 256 шагов, значение не трактуется как пропуск цикла',
     'возвращаемый A зависит только от исходного зерна, альтернативный AF хранит два младших разряда инвертированного случайного байта',
     'основной A не содержит случайный байт на выходе, его восстанавливает последний EX AF,AF\'',
     'поля H, L, E являются числовыми индексами, независимая флаговая схема им не приписывается',
     'игровые имена областей и конечных параметров ещё не установлены, полный вызывающий UnknownDE10 не доказан'])}
COMMENTS = {
    0xDE9A: (['сохранение BC вызывающего кода перед координатным классификатором и счётчиком шагов'],None),
    0xDE9B: (['временное сохранение входного управляющего A в альтернативном AF'],None),
    0xDE9C: (['вычисление трёхбитной свёртки четырёх байтов исходного зерна'],None),
    0xDEA2: (['вычисление индекса MAX(T-1, 0), исходный ноль требует отдельного обнуления'],None),
    0xDEA3: ([], 'переход, если исходная свёртка T ненулевая, сохранить результат T-1'),
    0xDEA6: (['выбор нулевого индекса при T=0 с исходными флагами XOR'],None),
    0xDEA7: (['сохранение вычисленного индекса и его F в альтернативном AF, восстановление управляющего A'],None),
    0xDEA8: (['обновление физического состояния генератора двумя входными словами зерна'],None),
    0xDEAF: (['вычисление байтового счётчика шагов, нулевой B после FF означает 256 итераций'],None),
    0xDEB1: (['определение числового типа области по исходному первому слову зерна'],None),
    0xDEB4: (['проверка OutsideCode перед выбором особого старшего индекса'],None),
    0xDEBA: ([], 'переход, если тип области не равен OutsideCode, оставить C=0'),
    0xDEBC: (['выбор C=1 вне трёх координатных областей'],None),
    0xDEBD: (['обновление исходного генератора, он сохраняет счётчик B и признак C'],None),
    0xDEC2: (['инверсия выходного байта последнего шага перед выделением числовых индексов'],None),
    0xDEC4: (['вычисление L в диапазоне 1..16 из средних четырёх разрядов инвертированного байта'],None),
    0xDECA: (['вычисление старшего индекса из разрядов 7..6 через два циклических сдвига'],None),
    0xDECF: (['проверка сохранённого признака внешней области, C=1 выделяет особый индекс'],None),
    0xDED0: ([], 'переход, если исходный C=0, использовать вычисленный двухбитный индекс'),
    0xDED2: (['выбор OutsideHigh вместо случайного старшего индекса для внешней области'],None),
    0xDED4: (['сохранение старшего индекса в H'],None),
    0xDED5: (['вычисление младшего индекса E из разрядов 1..0 инвертированного байта'],None),
    0xDED9: (['восстановление индекса зерна и его F, младший индекс и F от AND переходят в альтернативный AF'],None),
    0xDEDA: (['восстановление исходного BC без изменения возвращаемого AF'],None),
}


def name_operands(region,function_address,operation):
    if region=='Controls' and function_address==0xDE9A:
        operation = operation.replace('(#9B15)','(@ActionWordRandomState.Value.First)')
        operation = operation.replace('(#9B17)','(@ActionWordRandomState.Value.Second)')
        operation = operation.replace('CALL #6E2B','CALL @Action.ClassifyCoordinateRegion.Entry')
        operation = operation.replace('CP #03','CP @ActionRegionTypeConst.OutsideCode')
        for value,name in ((7,'HashMask'),(3,'PairMask'),(0x3C,'MiddleMask')):
            operation = operation.replace('AND #'+format(value,'02X'),'AND @ControlsSeededParametersConst.'+name)
        operation = operation.replace('LD A, #04','LD A, @ControlsSeededParametersConst.OutsideHigh')
    return operation

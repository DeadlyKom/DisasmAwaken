"""Коды положения точек с парными разрядами и OR-накоплением исходного сканера."""
FUNCTIONS={0xDEF3:('ClassifyProjectedVertices','Заполнение кодов границ экранных точек и накопление общего кода объекта')}
LOCAL={0xDEFF:'NextPoint',0xDF34:'SecondNegative',0xDF5C:'FirstHigh',0xDF75:'SecondHigh',0xDF9D:'FirstNegative'}
UNCLASSIFIED_SUFFIX_PATH='Source/Resources/17_ACTION/Unclassified028_AfterVertexCodes.bin'
CONTRACTS={('Action',0xDEF3):(
    ['NextOffset содержит 4+5*n, n от 1 до 50, последовательные FRenderProjectedPoint начинаются по 8E00',
     'Second является второй экранной координатой, First первой, старший байт 80 у Second обозначает отказ перспективы',
     'RAM страницы 8E доступна на запись, CPU-стек содержит внешний возврат, дополнительно нужны два байта сохранённого HL',
     'ACTION доступен в банке 0, IRQ не вмешиваются, нулевое и несогласованное число записей вне этого договора'],
    ['HL, DE, IX и IY сохраняются, B=5*n, C содержит стороны последней обработанной точки либо нуль при маркере отказа',
     'для каждой достигнутой точки без маркера ClipCode получает пару тетрад, младшая содержит признаки выхода, старшая их побитовое отрицание',
     'младшие биты 3..0 означают First<0, First>=96, Second<0, Second>=256, противоположные признаки одной оси не совмещаются',
     'если маркера нет, A равен OR всех записанных ClipCode, F равен флагам логического OR этого байта',
     "при полном проходе A'=5*n, F' равен флагам последнего CP B с равными операндами",
     "при маркере 80xx A=0/F=44, AF' хранит накопление предыдущих точек, остальные ещё не достигнутые коды сохраняются",
     "HL', DE', BC' сохраняются, SP после RET равен входному SP+2, I, IM, IFF и paging сохраняются, R меняется, портов нет"],
    ["BC, AF, AF', R, достигнутые ClipCode и два байта CPU-стека"],
    ['для Second исходный код сначала различает старший байт 80 как маркер, затем знак и ненулевой положительный старший байт',
     'граница First=96 проверяется по младшему байту только при нулевом старшем, отрицательное слово получает только отрицательную сторону',
     'перемещение INC L намеренно не переносится в H, договор ограничен записями одной страницы',
     'нулевой результат означает маркер, обычный код всегда содержит хотя бы по одному биту каждой пары и не равен нулю',
     '525288 сценариев проверяют два полных словарных среза, длины 1..50, поздние отказы, регистры, флаги, всю RAM и кратность записей',
     'R, время, пустой буфер, несогласованные смещения, все совместные входы, IRQ и нативный вывод не доказаны'])}
COMMENTS={
    0xDEF3:(['-----------------------------------------','Подготовка прохода одной страницы','Сохранение HL, очистка альтернативного накопителя и расчёт конечного байтового смещения как NextOffset-4.'],None),
    0xDEFF:(['-----------------------------------------','Классификация второй координаты','Очистка сторон текущей точки, чтение старшего байта Second и переход к старшему байту First.'],None),
    0xDF04:(['Проверка полного старшего байта 80 как маркера отказа перспективы до остальных знаковых проверок.'],None),
    0xDF06:([], 'переход, если старший байт Second равен 80, завершить весь проход без отката кодов'),
    0xDF08:([], 'переход, если старший байт Second больше 80, установить отрицательную сторону'),
    0xDF0A:(['Проверка ненулевого положительного старшего байта Second, такая точка лежит за границей 256.'],None),
    0xDF0B:([], 'переход, если положительный Second не меньше 256, установить старшую сторону'),
    0xDF34:(['Установка стороны Second<0, маркер 80xx уже исключён.'],None),
    0xDF5C:(['Установка стороны First>=96, противоположный отрицательный признак здесь не ставится.'],None),
    0xDF75:(['Установка стороны Second>=256.'],None),
    0xDF9D:(['Установка стороны First<0.'],None)}
for address in (0xDF0E,0xDF36,0xDF77):
    COMMENTS[address]=(['Проверка старшего байта First, знак задаёт отрицательную сторону, ненулевое положительное слово старшую.'],None)
for address in (0xDF10,0xDF38,0xDF79):COMMENTS[address]=([], 'переход, если First отрицателен, установить отрицательную сторону')
for address in (0xDF13,0xDF3B,0xDF7C):COMMENTS[address]=([], 'переход, если старший байт положительного First ненулевой, установить сторону First>=96')
for address in (0xDF19,0xDF41,0xDF82):COMMENTS[address]=(['Проверка First>=96 при нулевом старшем байте.'],None)
for address in (0xDF1B,0xDF43,0xDF84):COMMENTS[address]=([], 'переход, если First не меньше 96, установить старшую сторону')
for address in (0xDF1E,0xDF46,0xDF5F,0xDF87,0xDFA0):COMMENTS[address]=(['Расчёт ClipCode, младшая тетрада содержит стороны, старшая побитовое отрицание тех же четырёх признаков.'],None)
for address in (0xDF27,0xDF4F,0xDF68,0xDF90,0xDFA9):COMMENTS[address]=(['Обновление альтернативного OR-накопителя, прежние коды не откатываются при последующем маркере.'],None)
for address in (0xDF2A,0xDF52,0xDF6B,0xDF93,0xDFAC):COMMENTS[address]=(['Проверка конца после текущей записи, INC L сохраняет страницу 8E без переноса.'],None)
for address in (0xDF2E,0xDF56,0xDF6F,0xDF97,0xDFB0):COMMENTS[address]=([], 'переход, если байтовое смещение конца текущей записи не равно 5*n, обработать следующую')


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0xDEF3:
        operation=operation.replace('#DEF0','@Action.AbortProjectedVertexScan.Entry')
        for old,new in (('LD HL, #8E01','LD HL, @ActionVertexGroupConst.WorkPage+1'),
            ('(#D699)','(@ActionVertexGroupState.NextOffset)'),('SUB #04','SUB @ActionObjectVerticesConst.InitialOffset'),
            ('CP #80','CP @ActionPerspectiveConst.RejectedHigh'),('CP #60','CP @ActionVertexCodeConst.FirstLimit'),
            ('XOR #F0','XOR @ActionVertexCodeConst.InverseMask'),
            ('SET 0, C','SET @ActionVertexCodeConst.SecondHighBit, C'),('SET 1, C','SET @ActionVertexCodeConst.SecondNegBit, C'),
            ('SET 2, C','SET @ActionVertexCodeConst.FirstHighBit, C'),('SET 3, C','SET @ActionVertexCodeConst.FirstNegBit, C')):
            operation=operation.replace(old,new)
    return operation


def constants():
    lines=['','                ; Парные признаки границ, младшая тетрада снаружи, старшая её отрицание','                module ActionVertexCodeConst']
    for name,value,note in (('FirstLimit',96,'первая координата допустима от 0 до 95'),('InverseMask',0xF0,'инверсия старшей копии тетрады сторон'),
        ('SecondHighBit',0,'Second не меньше 256'),('SecondNegBit',1,'Second отрицателен'),('FirstHighBit',2,'First не меньше 96'),('FirstNegBit',3,'First отрицателен')):
        lines.append((name.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+note)
    return '\n'.join(lines+['                endmodule',''])


INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionVertexCodeConst',constants()),)

"""Полный одиночный диспетчер ACTION и его собственный общий возврат."""
FUNCTIONS={51521: ('ClipSingleEdge', 'Отсечение одиночного ребра с обменом внутренней первой точки и рамкой трёх возвратов')}
LOCAL={51572: 'PickCase', 51603: 'Finish'}
LABELS={('Action', 51572): 'PickCase', ('Action', 51603): 'Finish'}
ADDITIONAL_SYMBOLS={'Action.ClipSingleEdge.Finish': 51603}
RENAMES={'Action.UnknownC941.Entry': 'Action.ClipSingleEdge.Entry', 'Action.UnknownC941.PointC974': 'Action.ClipSingleEdge.PickCase'}
CONTRACTS={('Action', 51521): (['FirstPoint и SecondPoint содержат signed16 координаты и согласованные парные ClipCode, размеры и исходные поля доступны на запись', 'SeenFlags содержит прежние отметки углов, их старшая тетрада должна сохраняться, входной размер и CornerBlock несущественны', 'для каждого достигнутого деления d ненулевой, U=N при N>=0 либо -N-1, требуется U<abs(d)*65536', 'ACTION находится в банке 0, CPU-стек содержит внешний возврат и допускает три служебных слова с вложенными рамками, IRQ не вмешиваются'], ['если FirstPoint.ClipCode=F0, обе пятибайтовые точки полностью меняются местами, в том числе при двух внутренних точках', 'CornerBlock=1, OutputSize начинается с нуля, SeenFlags обновляется установкой младших отметок без очистки прежних', 'в страницу 90 записано до двух точек в порядке выбранного табличного пути, углы фактически не добавляются', 'при обычном полном выходе A=OutputSize, F от CP размера,4, DE=Finish, HL и BC определяются последней цепочкой помощников', 'при специальном выходе через ExitClipContour HL=CA5B, BC=00C8, AF=C989', "HL', DE', BC', IY, I, IM, IFF и paging сохраняются, AF' и IX соответствуют последним достигнутым помощникам", 'SP после RET равен входному SP+2, R меняется, исходный порядок точек не восстанавливается'], ["HL, DE, BC, AF, AF', IX по помощникам, R, обе точки при обмене, CornerBlock, размер, младшие отметки углов, достигнутые произведения, выходные пары и временные слова CPU-стека"], ['сначала выполняется обмен, затем пересчитывается индекс таблицы, переносить исходную пару зон до обмена на фактический путь нельзя', 'Finish является общим продолжением для трёх подставных возвратов, его POP DE снимают два оставшихся слова перед внешним RET', '24832 сценария исполняют настоящий диспетчер и все помощники, проверены все регистры кроме R, вся физическая RAM и кратность записей', 'числовой эталон композиционный по исходным путям, точное R/T, все совместные входы, независимое геометрическое доказательство, IRQ, сборка и нативный вывод не заявляются'])}
# Полный счёт M1 одиночного ребра, включая собственный диспетчер и оба вида возврата.
CONTRACTS['Action',0xC941][1].append('R получает 25 M1 префикса и выбора таблицы, ещё 17 при перестановке концов, все M1 выбранного Case и его детей, затем 5 M1 Finish либо 9 M1 ExitClipContour, старший бит R сохраняется')
CONTRACTS['Action',0xC941][3].extend([
    'в Case каждый JP/CALL/RET даёт один M1, BIT и SET через CB дают два, стоимость достигнутого помощника учитывается целиком с его RET',
    'сравнения двух 32-разрядных числителей дают 12 M1, разности координат 7, запись второй точки 14, угловой помощник при CornerBlock=1 возвращается за 3 M1',
    'обёртка вычисления и записи пересечения добавляет один M1 CALL к полным числителю и писателю, их стоимости заданы собственными договорами',
    'новая отдельная серия 24832 случая сверяет точный R и полное число M1, все сравниваемые регистры, восемь банков и кратность присваиваний',
    'прежние ограничения R относятся к исходной серии, новая проверка использует исходный JR NZ по C94B, произвольные изменения кода, все совместные входы и точные T не доказаны'])

COMMENTS={51521: (['-----------------------------------------', 'Подготовка одиночного ребра', 'Установка полного запрета фактического вывода углов, прежние отметки SeenFlags не очищаются.'], None), 51526: (['Проверка внутренней первой точки по полному парному коду F0.'], None), 51531: ([], 'переход, если первая точка не имеет внутреннего кода F0, сохранить исходный порядок'), 51533: (['Обмен кодов и обоих слов точек, выполняется также при двух внутренних концах.'], None), 51572: (['-----------------------------------------', 'Выбор обработчика после обмена', 'Обнуление размера и расчёт индекса по текущему порядку двух точек.'], None), 51590: (['Чтение младшего и старшего байтов цели из исходных страниц CF и D0.'], None), 51596: (['Сохранение трёх одинаковых возвратов Finish поверх внешнего адреса, CALL обработчика не используется.'], None), 51603: (['-----------------------------------------', 'Общий возврат одиночного ребра', 'Чтение размера, снятие двух оставшихся подставных слов и проверка двух выходных точек.'], None)}
LOCATION={51521: 'банковое окно ACTION банка 0, адреса C941..C99A'}


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0xC941:
        for address,expression in ((0xCF0B,'FirstPoint+FRenderProjectedPoint.Second'),(0xCF0D,'FirstPoint+FRenderProjectedPoint.First'),(0xCF0F,'FirstPoint+FRenderProjectedPoint.ClipCode'),(0xCF1B,'SecondPoint+FRenderProjectedPoint.Second'),(0xCF1D,'SecondPoint+FRenderProjectedPoint.First'),(0xCF1F,'SecondPoint+FRenderProjectedPoint.ClipCode')):
            operation=operation.replace('(#'+format(address,'04X')+')','(@ActionClipProductsState.'+expression+')')
        operation=operation.replace('(#CF03)','(@ActionClipPointWritersState.CornerBlock)').replace('(#9BA3)','(@ActionClipIntersectionsState.OutputSize)')
        operation=operation.replace('LD A, #01','LD A, @ActionSingleEdgeConst.NoCorners')
        operation=operation.replace('CP #F0','CP @ActionVertexCodeConst.InverseMask').replace('AND #F0','AND @ActionVertexCodeConst.InverseMask').replace('AND #0F','AND @ActionPolygonConst.OutsideMask')
        operation=operation.replace('LD H, #CF','LD H, @ActionPolygonConst.TableLowPage').replace('LD DE, #C993','LD DE, @Action.ClipSingleEdge.Finish').replace('CP #04','CP @ActionSingleEdgeConst.SegmentBytes')
    for point in ('FirstPoint','SecondPoint'):
        operation=operation.replace('@ActionClipProductsState.'+point+'+FRenderProjectedPoint.','@ActionClipPoints.'+point+'.')
    return operation

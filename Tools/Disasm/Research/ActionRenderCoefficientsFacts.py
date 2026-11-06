"""Девять раздельных изменяемых операндов, таблицы и байтовые коррекции установлены по ACTION."""
FUNCTIONS = {0xC99B: ('BuildRenderCoefficients', 'Построение девяти байтовых коэффициентов по трём фазам либо по одной фазе')}
LOCAL = {0xC9CF: 'ThreePhases', 0xCA55: 'StoreCoeff21', 0xCA9E: 'StoreCoeff22', 0xCAD6: 'StoreCoeff31',
         0xCB1F: 'StoreCoeff32', 0xCAB3: 'ScaleCoeff31', 0xCAE3: 'ReadCoeff33Base'}
OUTPUTS = ((0xCB38, 'Coeff11'), (0xCB3A, 'Coeff21'), (0xCB3C, 'Coeff31'), (0xCC25, 'Coeff12'),
           (0xCC27, 'Coeff22'), (0xCC29, 'Coeff32'), (0xCD22, 'Coeff13'), (0xCD24, 'Coeff23'), (0xCD26, 'Coeff33'))
CONTRACTS = {('Action', 0xC99B): (
    ['HL, DE, BC и AF числовых аргументов не задают, входные флаги на результаты не влияют',
     'Phase0, Phase1 и Phase2 по 9B12..9B14 задают три байтовых индекса исходной синусоиды, оборот равен 256',
     'бит 0 младшего байта HeaderWord0 по 9B8D выбирает короткий режим, остальные семь разрядов здесь не проверяются',
     'ACTION доступен в банке 0, страницы 98 и 99 содержат исходные таблицы квадратов и синусоиды',
     'на CPU-стеке находится внешний возврат, дополнительных рамок нет, IRQ не вмешиваются'],
    ['девять раздельных операндов Coeff11..Coeff33 получают значения по точным байтовым формулам ActionRenderCoefficients.md',
     'при бите 0 равном 1 используются только Phase1, HL=9900 OR Phase1, B=Phase1, C и DE сохраняются, AF=7F44',
     'в коротком режиме IX и IY сохраняются, Coeff11=Coeff32=cos Phase1, Coeff12=sin Phase1, Coeff31=-sin Phase1',
     'в коротком режиме Coeff13, Coeff21, Coeff22, Coeff33 равны нулю, Coeff23=127',
     'в общем режиме BC содержит sin Phase0 и cos Phase0, IX содержит P(cos Phase1,cos Phase0) и sin Phase1',
     'в общем режиме IY содержит cos Phase2 и cos Phase1, HL содержит страницу 98 и последний индекс P(P(sin Phase1,sin Phase0),sin Phase2)',
     'в общем режиме D=sin Phase2, E содержит последний квадрат по первому индексу P, A=Coeff32, F относится к последнему сложению либо его коррекции',
     "HL', DE', BC', AF', I, IM и IFF сохраняются, SP после RET равен входному SP+2, портов и дополнительных записей стека нет"],
    ['HL, DE, BC, AF, IX и IY по общему пути, HL, B и AF по короткому пути, девять операндов коэффициентов и R'],
    ['P использует signed8-половины с округлением вниз и два байтовых индекса свёрнутой таблицы, обычным произведением не заменяется',
     'при Overflow сложения либо вычитания выполняется NEG обёрнутого результата, при Overflow NEG выполняется DEC, это не обычное насыщение',
     'режим одной фазы не проверяет нулевые Phase0 и Phase2, их значения просто игнорируются',
     'все девять коэффициентов являются раздельными непосредственными операндами, непрерывная фиктивная структура матрицы не создаётся',
     'записи UpdateFrame при выбранном банке 4 по совпадающим адресам относятся к OBJECT3D и не изменяют этот код банка 0',
     'матрица предварительного просмотра имеет те же числовые примитивы, однако байты и регистры ACTION проверены отдельно по своему образу',
     'композиция CB23 проверена отдельно, преобразование вершин ещё не доказано, этот договор ограничен C99B..CB22'])}
COMMENTS = {
    0xC99B: (['-----------------------------------------', 'Выбор режима коэффициентов',
        'Проверка бита одной фазы в младшем байте HeaderWord0, прочие разряды здесь не интерпретируются.',
        'Младший байт HeaderWord0, разряды 7..0, ? ? ? ? ? ? ? S, маска S равна 01.',
        'S=1 выбирает одну фазу, нулевой байт выбирает общий расчёт, остальные биты неизвестны.'], None),
    0xC9A0: ([], 'переход, если бит одной фазы сброшен, использовать три исходные фазы'),
    0xC9A2: (['Чтение Phase1 для короткого режима, Phase0 и Phase2 не используются.'], None),
    0xC9A6: (['Расчёт четверть-периодного индекса косинуса Phase1 по модулю 256.'], None),
    0xC9AB: (['Сохранение одинакового косинуса в Coeff11 и Coeff32.'], None),
    0xC9B2: (['Чтение исходного синуса Phase1 для Coeff12.'], None),
    0xC9B7: (['Расчёт отрицательного синуса для Coeff31 по модулю 256.'], None),
    0xC9BC: (['Обнуление четырёх коэффициентов короткого режима, единичный Coeff23 равен 127.'], None),
    0xC9CF: (['-----------------------------------------', 'Подготовка трёх фаз', 'Чтение синуса и четверть-периодной выборки Phase0 в B и C.'], None),
    0xC9D6: (['Расчёт индекса косинуса Phase0 с байтовым оборачиванием.'], None),
    0xC9DA: (['Чтение синуса Phase1 в IXL.'], None),
    0xC9E1: (['Расчёт индекса косинуса Phase1, результат выборки сохраняется в IYL.'], None),
    0xC9E8: (['Чтение синуса Phase2 в D и запись его отрицания в Coeff13.'], None),
    0xC9EE: (['Расчёт отрицательного sin Phase2 по модулю 256.'], None),
    0xC9F3: (['Расчёт четверть-периодной выборки Phase2 для IYH.'], None),
    0xC9FA: (['-----------------------------------------', 'Табличные произведения', 'Подготовка страницы квадратов и пары cos Phase2, cos Phase1 для Coeff11.'], None),
    0xC9FE: (['Расчёт P(cos Phase2, cos Phase1) через разность двух свёрнутых квадратов.'], None),
    0xCA0D: (['Расчёт P(sin Phase1, cos Phase2) для Coeff12.'], None),
    0xCA20: (['Расчёт P(sin Phase1, sin Phase0), временное значение сохраняется в IXH.'], None),
    0xCA30: (['Расчёт P(cos Phase1, cos Phase0), затем произведения результата с sin Phase2.'], None),
    0xCA3E: (['Расчёт внешнего произведения с sin Phase2 для Coeff21.'], None),
    0xCA4A: (['Расчёт суммы двух табличных членов Coeff21 и проверка знакового переполнения.'], None),
    0xCA4C: ([], 'переход, если сумма Coeff21 не переполнила signed8, сохранить её напрямую'),
    0xCA4F: (['Отражение обёрнутой суммы Coeff21 через NEG, результат 80 требует отдельного DEC.'], None),
    0xCA51: ([], 'переход, если NEG суммы Coeff21 не переполнился, дополнительный DEC не нужен'),
    0xCA54: (['Коррекция единственного повторного Overflow, байт 80 превращается в 7F.'], None),
    0xCA58: (['Расчёт P(cos Phase2, cos Phase0) для Coeff23.'], None),
    0xCA69: (['Расчёт P(cos Phase1, sin Phase0), временное значение сохраняется в IXH.'], None),
    0xCA79: (['Расчёт P(sin Phase1, cos Phase0) для внешнего произведения Coeff22.'], None),
    0xCA87: (['Расчёт P полученного байта с sin Phase2.'], None),
    0xCA93: (['Расчёт разности двух членов Coeff22 и проверка Overflow.'], None),
    0xCA95: ([], 'переход, если разность Coeff22 не переполнила signed8, сохранить её напрямую'),
    0xCA98: (['Отражение обёрнутой разности Coeff22 через NEG.'], None),
    0xCA9A: ([], 'переход, если NEG разности Coeff22 не переполнился, DEC пропустить'),
    0xCA9D: (['Коррекция повторного Overflow Coeff22, байт 80 превращается в 7F.'], None),
    0xCAA1: (['Расчёт P(sin Phase1, cos Phase0), временное значение для Coeff31 сохраняется в IXH.'], None),
    0xCAB1: (['Расчёт P(cos Phase1, sin Phase0) перед внешним произведением с sin Phase2.'], None),
    0xCABF: (['Расчёт внешнего произведения с sin Phase2 для Coeff31.'], None),
    0xCACB: (['Расчёт разности двух членов Coeff31 и проверка Overflow.'], None),
    0xCACD: ([], 'переход, если разность Coeff31 не переполнила signed8, сохранить её напрямую'),
    0xCAD0: (['Отражение обёрнутой разности Coeff31 через NEG.'], None),
    0xCAD2: ([], 'переход, если NEG разности Coeff31 не переполнился, DEC пропустить'),
    0xCAD5: (['Коррекция повторного Overflow Coeff31, байт 80 превращается в 7F.'], None),
    0xCAD9: (['Расчёт P(cos Phase2, sin Phase0) для Coeff33.'], None),
    0xCAEA: (['Расчёт P(cos Phase1, cos Phase0), последнее временное значение в IXH.'], None),
    0xCAFA: (['Расчёт P(sin Phase1, sin Phase0) перед внешним произведением Coeff32.'], None),
    0xCB08: (['Расчёт внешнего произведения с sin Phase2 для Coeff32.'], None),
    0xCB14: (['Расчёт суммы двух членов Coeff32, её флаги либо флаги коррекции остаются на выходе процедуры.'], None),
    0xCB16: ([], 'переход, если сумма Coeff32 не переполнила signed8, сохранить её напрямую'),
    0xCB19: (['Отражение обёрнутой суммы Coeff32 через NEG.'], None),
    0xCB1B: ([], 'переход, если NEG суммы Coeff32 не переполнился, DEC пропустить'),
    0xCB1E: (['Коррекция повторного Overflow Coeff32, байт 80 превращается в 7F.'], None)}


def name_operands(region, function_address, operation):
    if region != 'Action' or function_address != 0xC99B:
        return operation
    operation = operation.replace('LD HL, #9B8D', 'LD HL, @ActionRenderQueueInsertState.HeaderWord0')
    for address, name in OUTPUTS:
        operation = operation.replace('(#' + format(address, '04X') + ')', '(@ActionRenderCoefficientsState.' + name + ')')
    for index in range(3):
        operation = operation.replace('(#' + format(0x9B12 + index, '04X') + ')', '(@ActionRenderPhases.Value.Phase' + str(index) + ')')
    operation = operation.replace('BIT 0,', 'BIT @ActionRenderCoefficientsConst.OneAxisBit,')
    operation = operation.replace('LD A, #7F', 'LD A, @ActionRenderCoefficientsConst.Unit')
    operation = operation.replace('ADD A, #40', 'ADD A, @BufferPointMotionConst.QuarterCycle')
    operation = operation.replace('LD H, #99', 'LD H, @BufferPointMotionConst.SinePage')
    operation = operation.replace('LD H, #98', 'LD H, @ActionProjectionClipConst.SquarePage')
    return operation

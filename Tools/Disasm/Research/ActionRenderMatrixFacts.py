"""Композиция исходных коэффициентов сцены и модели ACTION, точные четверти не заменяются произведениями."""
FUNCTIONS = {0xCB23: ('ComposeRenderMatrix', 'Композиция исходной матрицы и ориентации с одноосным режимом и точными четвертями')}
LOCATION = {0xCB23: 'код ACTION банка 0, адреса CB23..CEE2'}
LOCAL = {0xCB37: 'Column1', 0xCE06: 'CopyMiddle', 0xCE19: 'QuarterTurns', 0xCE62: 'Quarter0', 0xCE87: 'Quarter1', 0xCEB2: 'Quarter2'}
ROWS = (
    (1, 1, (0xCB3D, 0xCB53, 0xCB6E), 0xCB4D, 0xCB6C, 0xCB87),
    (2, 1, (0xCB8A, 0xCBA0, 0xCBBB), 0xCB9A, 0xCBB9, 0xCBD4),
    (3, 1, (0xCBD7, 0xCBED, 0xCC08), 0xCBE7, 0xCC06, 0xCC21),
    (1, 2, (0xCC2A, 0xCC41, 0xCC5D), 0xCC3B, 0xCC5B, 0xCC77),
    (2, 2, (0xCC7A, 0xCC91, 0xCCAD), 0xCC8B, 0xCCAB, 0xCCC7),
    (3, 2, (0xCCCA, 0xCCE1, 0xCCFD), 0xCCDB, 0xCCFB, 0xCD17),
    (1, 3, (0xCD27, 0xCD38, 0xCD54), None, 0xCD52, 0xCD6E),
    (2, 3, (0xCD71, 0xCD82, 0xCD9E), None, 0xCD9C, 0xCDB8),
    (3, 3, (0xCDBB, 0xCDCC, 0xCDE8), None, 0xCDE6, 0xCE02))
OUTPUTS = ((0xD5FC, 0xD61E, 0xD60D), (0xD62F, 0xD651, 0xD640), (0xD662, 0xD684, 0xD673))
SCENE = ((0xCB3E, 0xCB54, 0xCB6F), (0xCB8B, 0xCBA1, 0xCBBC), (0xCBD8, 0xCBEE, 0xCC09))
CONTRACTS = {('Action', 0xCB23): (
    ['HL, DE, BC и AF числовых аргументов не задают, исходные значения сохраняются только по указанным четверть-периодным путям',
     'ActionPatchedVectorCoeffs.C00..C22 задают девять раздельных исходных байтов сцены',
     'ActionRenderCoefficientsState.Coeff11..Coeff33 задают матрицу ориентации, подготовленную BuildRenderCoefficients',
     'бит 0 младшего байта HeaderWord0 по 9B8D выбирает одноосный режим, Phase1 определяет четверть-периодную ветвь',
     'ACTION доступен в банке 0, страница 98 содержит исходную симметричную таблицу квадратов, IRQ не вмешиваются',
     'на CPU-стеке находится обычный внешний возврат, дополнительных рамок нет'],
    ['девять выходных операндов Coeff11..Coeff33 получают значения по формулам ActionRenderMatrix.md',
     'во всех ветвях IY=9B8D, IXL сохраняется, SP после RET равен входному SP+2',
     'в общем режиме A содержит выходной Coeff33, F относится к его последнему сложению либо коррекции',
     'в одноосном арифметическом режиме A=C21 исходной матрицы, F=18 OR Carry последнего скорректированного сложения',
     'в арифметических ветвях BC содержит первые два элемента последнего вычисленного столбца ориентации, D третий элемент, E последний квадрат P',
     'в арифметических ветвях HL содержит страницу 98 и последний индекс суммы P, IXH последнюю частичную сумму',
     'в точных четвертях H=98, входной L, DE, BC и IX сохраняются, AF задаётся последней копией либо последним NEG',
     'для Phase1=0 A=C22 и F=54, для 64 A=C20 и F от NEG C22, для 128 A=-C22 и F от NEG C22, для 192 A=-C20 и F от NEG C20',
     "HL', DE', BC', AF', I, IM и IFF сохраняются, записи CPU-стека и портовые операции отсутствуют"],
    ['HL, DE, BC, AF, IXH и IY в зависимости от ветви, девять выходных операндов и R'],
    ['общая ветвь корректирует сумму первых двух P, затем отдельно сумму с третьим P, порядок скобок сохраняется',
     'при одноосном режиме средние члены первых двух столбцов не вычисляются, третий столбец точно копируется из второго столбца сцены',
     'при одноосном режиме и Phase1, кратной 64, все табличные произведения обходятся точными перестановками и NEG',
     'NEG исходного 80 оставляет 80, дополнительная коррекция в точных четвертях не выполняется',
     'выходы являются существующими операндами LD A,n внутри следующего расчёта, отдельная матрица в новой RAM не создаётся',
     'преобразование вершин, отсечение и вывод после D5C9 не входят в этот локальный договор'])}
COMMENTS = {
    0xCB23: (['-----------------------------------------', 'Выбор ветви композиции', 'Подготовка страницы квадратов и указателя на частично неизвестный HeaderWord0.'], None),
    0xCB29: (['Проверка бита одной фазы, остальные разряды HeaderWord0 не участвуют в выборе ветви.'], None),
    0xCB2D: ([], 'переход, если бит одной фазы сброшен, вычислить общую композицию'),
    0xCB2F: (['Чтение Phase1 и проверка её младших шести разрядов на кратность четверти оборота.'], None),
    0xCB34: ([], 'переход, если Phase1 кратна 64, переставить столбцы без табличного округления'),
    0xCB37: (['-----------------------------------------', 'Первый столбец результата', 'Чтение раздельных изменяемых Coeff11, Coeff21 и Coeff31 ориентации в B, C и D.'], None),
    0xCC24: (['-----------------------------------------', 'Второй столбец результата', 'Чтение Coeff12, Coeff22 и Coeff32 ориентации для следующих трёх строк.'], None),
    0xCD1A: (['-----------------------------------------', 'Третий столбец либо точная копия', 'Проверка бита одной фазы после первых двух столбцов, BIT сохраняет Carry последней коррекции.'], None),
    0xCD1E: ([], 'переход, если бит одной фазы установлен, точно скопировать второй столбец сцены'),
    0xCD21: (['Чтение Coeff13, Coeff23 и Coeff33 ориентации для общего третьего столбца.'], None),
    0xCE06: (['-----------------------------------------', 'Точная копия среднего столбца', 'Копирование C01, C11 и C21 в третий выходной столбец без приближённого P с единичным коэффициентом.'], None),
    0xCE19: (['-----------------------------------------', 'Точные четверти оборота', 'Копирование второго столбца сцены в третий столбец результата до выбора знаков двух остальных.'], None),
    0xCE2B: (['Чтение полного Phase1, младшие шесть разрядов уже проверены на нуль.'], None),
    0xCE2E: (['Проверка нуля, знака и чётности для различения ровно четырёх возможных фаз.'], None),
    0xCE2F: ([], 'переход, если Phase1 равна 0, взять первый и третий столбцы сцены'),
    0xCE31: ([], 'переход, если Phase1 равна 64, взять отрицательный третий и первый столбцы сцены'),
    0xCE34: ([], 'переход, если Phase1 равна 128, изменить знаки первого и третьего столбцов сцены'),
    0xCE37: (['Phase1 равна 192, первый выходной столбец получает третий столбец сцены, второй получает отрицательный первый.'], None),
    0xCE62: (['Phase1 равна 0, первый выходной столбец получает первый столбец сцены, второй получает третий.'], None),
    0xCE87: (['Phase1 равна 64, первый выходной столбец получает отрицательный третий столбец сцены, второй получает первый.'], None),
    0xCEB2: (['Phase1 равна 128, первый и третий столбцы сцены копируются с отрицанием.'], None)}
for row, column, terms, bit, partial, total in ROWS:
    suffix = str(row) + str(column)
    for index, address in enumerate(terms):
        source = 'C' + str(row - 1) + str(index)
        model = 'Coeff' + str(index + 1) + str(column)
        COMMENTS[address] = (['Расчёт P(' + source + ', ' + model + ') для выходного Coeff' + suffix + '.'], None)
    for address, label, meaning in ((partial, 'Partial' + suffix, 'суммы первых двух произведений'), (total, 'Store' + suffix, 'суммы частичного результата и третьего произведения')):
        LOCAL[address] = label
        COMMENTS[address - 11] = (['Расчёт обёрнутой ' + meaning + ' для Coeff' + suffix + '.'], None)
        COMMENTS[address - 9] = ([], 'переход, если сумма Coeff' + suffix + ' не переполнила signed8, принять её напрямую')
        COMMENTS[address - 6] = (['Отражение обёрнутого результата Coeff' + suffix + ' через NEG.'], None)
        COMMENTS[address - 4] = ([], 'переход, если NEG суммы Coeff' + suffix + ' не переполнился, DEC пропустить')
        COMMENTS[address - 1] = (['Коррекция повторного Overflow Coeff' + suffix + ', байт 80 превращается в 7F.'], None)
    if bit is not None:
        COMMENTS[bit] = (['Проверка, нужен ли средний член для Coeff' + suffix + '.'], None)
        COMMENTS[bit + 4] = ([], 'переход, если бит одной фазы установлен, средний член Coeff' + suffix + ' пропустить')
        LOCAL[terms[2]] = 'Last' + suffix
LABELS = {('Action', a): name for a, name in LOCAL.items()}
RENAMES = {'Action.UnknownCB23.Entry': 'Action.ComposeRenderMatrix.Entry',
           **{'Action.UnknownCB23.Point' + format(a, '04X'): 'Action.ComposeRenderMatrix.' + name for a, name in LOCAL.items()}}


def name_operands(region, function_address, operation):
    if region != 'Action' or function_address != 0xCB23:
        return operation
    for row in range(3):
        for column in range(3):
            operation = operation.replace('(#' + format(SCENE[row][column], '04X') + ')', '(@ActionPatchedVectorCoeffs.C' + str(row) + str(column) + ')')
            operation = operation.replace('(#' + format(OUTPUTS[row][column], '04X') + ')', '(@ActionRenderMatrixState.Coeff' + str(row + 1) + str(column + 1) + ')')
    operation = operation.replace('LD IY, #9B8D', 'LD IY, @ActionRenderQueueInsertState.HeaderWord0')
    operation = operation.replace('(#9B13)', '(@ActionRenderPhases.Value.Phase1)')
    operation = operation.replace('LD H, #98', 'LD H, @ActionProjectionClipConst.SquarePage')
    operation = operation.replace('AND #3F', 'AND @PreviewMatrixComposeConst.QuarterMask')
    operation = operation.replace('BIT 0,', 'BIT @ActionRenderCoefficientsConst.OneAxisBit,')
    operation = operation.replace('(IY+#00)', '(IY + @FRenderHeaderState.ModeBits)')
    return operation


def qualify_mutations(mutations, regions, functions):
    from CheckActionParameterActivation import flat_action
    from InspectZ80 import decoder
    region = next(r for r in regions if r['name'] == 'Action')
    targets = {a for row in OUTPUTS for a in row}
    # Проверка границ всех девяти целевых LD A,n линейным продолжением от известного CALL D5C9.
    decoded = {i.address: i for i in decoder(flat_action()).disassemble(0xD5C9, 0xD690, 'h')}
    for target in targets:
        assert decoded[target - 1].operation == 'LD A,#00' and decoded[target - 1].bytes == bytes((0x3E, 0))
    writers = []
    for instruction in region['instructions']:
        if not 0xCB23 <= instruction['address'] < 0xCEE3:
            continue
        for target in targets:
            if instruction['operation'] == 'LD (#' + format(target, '04X') + '),A':
                writers.append((instruction, target))
    assert len(writers) == 39
    for instruction, target in writers:
        assert not any(m['region'] == 'Action' and m['writer'] == instruction['address'] for m in mutations)
        mutations.append(dict(region='Action', writer=instruction['address'], target=target, target_instruction=target - 1,
            size=1, target_operation='LD A,#00', path='Source/Action/ComposeRenderMatrix.asm', writer_bank=0, target_bank=0,
            target_region='Action', target_slot=17, target_offset=target - 0x6000, target_source_classified=False,
            target_original_hex='3e00', target_instruction_boundary_proof='linear_continuation_from_direct_call_D5C9'))
    mutations.sort(key=lambda m: (m['region'], m['writer'], m['target']))

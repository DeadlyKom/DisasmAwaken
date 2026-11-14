"""Перспектива ACTION с дополненным частным, SLL-единицами и точными частичными выходами."""
FUNCTIONS = {0xD7A0: ('ProjectRenderVertex', 'Перспективная запись одной вершины с исходной нормализацией и косвенным продолжением')}
LOCAL = {0xD7AB: 'DepthShift', 0xD7C6: 'FirstShift', 0xD7DE: 'FirstMagnitude', 0xD99C: 'FirstQuotient',
         0xD9A9: 'FirstNegative', 0xD9AA: 'StoreFirst', 0xD9B8: 'SecondShift', 0xD9CF: 'SecondMagnitude', 0xDB8D: 'SecondQuotient',
         0xDB9F: 'SecondNegative', 0xDBA8: 'RejectFirst', 0xDBB3: 'RejectSecond'}
UNCLASSIFIED_PREFIX_PATH = 'Source/Resources/17_ACTION/Unclassified028_BeforePerspective.bin'
UNCLASSIFIED_SUFFIX_PATH = 'Source/Resources/17_ACTION/Unclassified028_AfterPerspective.bin'
MODIFIED_WRITERS = ((0xD7D0, 0xD9C3, 0xD9C2, 2),)
STATE_FIELDS = (('DepthShiftSkip', 0xD7AC, 'изменяемый JR глубины, допустимое смещение 6-exponent от 0 до 5'),
                ('FirstShiftSkip', 0xD7C7, 'изменяемый JR первой координаты, тот же показатель масштаба'),
                ('SecondShiftSkip', 0xD9B9, 'изменяемый JR второй координаты, тот же показатель масштаба'),
                ('SavedDepth', 0xD9C3, 'операнд LD DE,nn перед делением второй координаты'))
CONTRACTS = {('Action', 0xD7A0): (
    ['HL задаёт адрес косвенного продолжения, DE содержит D как вторую локальную координату и E как первую, BC числового аргумента не задаёт',
     'A задаёт локальную координату глубины, три локальных байта трактуются как signed8',
     'Output2, Output1 и Output0 задают соответственно базы глубины, первой и второй координат',
     'DepthShiftSkip, FirstShiftSkip и SecondShiftSkip содержат одинаковое 6-exponent, exponent от 1 до 6',
     'SP указывает на ClipCode выходного FRenderProjectedPoint, начало записи находится по входному SP-4',
     'записываемые байты и промежуточный SP не должны разрушать код и исходные параметры, обычный CALL/RET здесь не используется',
     'ACTION находится в банке 0, прерывания не вмешиваются в рабочий стек'],
    ['HL, DE и BC сохраняются, управление заканчивается JP (HL) с исходным адресом продолжения',
     'AF содержит A последней достигнутой арифметической ветви, F=(Fbranch AND #C4) OR (Fadd AND #39), N=0, это не общий булев признак',
     "HL' равен конечному SP=(входной SP+5) AND #FFFF",
     "DE' при арифметическом успехе содержит depth, при любом отказе содержит записанное Second с полным старшим кодом 80",
     "BC' при отрицательной глубине сохраняется, при успехе содержит сырой дополненный результат второй оси, при отказе оси содержит её исходную базу, кроме случая magnitude=8000/depth=0100 с младшим C'=1",
     "AF' при отрицательной глубине сохраняется, при отказе оси содержит её сохранённый знаковый контекст, при успехе содержит контекст дополненного деления второй оси",
     'IX и IY сохраняются, I, IM, IFF и paging сохраняются, R изменяется, портов нет',
     'SP увеличен на размер FRenderProjectedPoint, First записан по входному SP-2, Second по входному SP-4, ClipCode по входному SP сохранён',
     'depth=wrap16(signed8(входной A)*2^(exponent-1)+Output2), проверяется только Sign, переполнение отдельно не проверяется',
     'при отрицательной depth First=исходный Output2, Second=#8000 OR LOW(Output2), SavedDepth сохраняется',
     'при неотрицательной depth SavedDepth получает полное слово до проверки первой оси',
     'если depth=0 либо magnitude первой координаты не меньше 128*depth, First=depth, Second=#8000 OR LOW(depth)',
     'при отказе второй оси уже вычисленный First сохраняется, Second=#8000 OR LOW(depth)',
     'при двух принятых осях First и Second получают формулу дополненного частного и центров 48 и 128 из ActionPerspective.md'],
    ["AF, HL', DE', BC', AF', SP, R, четыре байта выходной записи и SavedDepth после допуска глубины"],
    ['Fbranch означает флаги последней достигнутой ветви, Fadd флаги заключительного ADD HL,SP для #0009+(входной SP-4)',
     'произведение локальной координаты на степень двойки и сложение базы оборачиваются до 16 бит, Overflow отдельно не проверяется',
     'обычный положительный частный результат здесь не используется напрямую, сырой BC является дополнением результата по битам',
     'SLL вводит единицы при нормализации, для высокого байта depth не равного нулю это даёт доказанную добавку к числителю',
     'нулевой числитель при depth>=256 имеет отдельный путь BC=0, при depth<256 действует обычный дополненный путь',
     'положительная координата вычитается из центра через SBC с сохранённым Carry своего сложения с базой, Carry не очищается',
     'все отказы записывают полный числовой код 80 в старший байт второго слова, это не независимый флаг одного разряда',
     'исходные смещения JR равны FE и зацикливаются без подготовки, вызывающий блок D5C9 обязан записать 6-exponent',
     'независимая модель проверяет точные регистры и флаги кроме R/T, значение R алгоритмом не читается, время и обновление R отдельно не доказаны',
     'полный генератор группы, использование пятого байта, отсечение граней и нативный вывод не входят в этот договор'])}
COMMENTS = {
    0xD7A0: (['-----------------------------------------', 'Перевод локальной глубины', 'Переход в рабочий набор EXX, основной HL продолжения и DE координат должны сохраниться.'], None),
    0xD7A1: (['Чтение Output2 как базы глубины и знаковое расширение локального A до слова.'], None),
    0xD7AB: (['Выбор числа удвоений, действующий JR получает 6-exponent, исходный FE здесь не является рабочим смещением.'], None),
    0xD7AD: (['Расчёт signed8 локальной глубины, умноженной на 2^(exponent-1), с оборачиванием слова.'], None),
    0xD7B2: (['Сброс входного Carry перед прибавлением базы глубины и проверкой знакового бита суммы.'], None),
    0xD7B5: ([], 'переход, если глубина после оборачивания отрицательна, записать два слова отказа'),
    0xD7B8: (['-----------------------------------------', 'Первая координата', 'Сохранение принятой глубины в DE и чтение исходного E из основного набора.'], None),
    0xD7BC: (['Знаковое расширение первой локальной координаты.'], None),
    0xD7C3: (['Чтение Output1 и выбор масштаба первой координаты через изменяемый JR.'], None),
    0xD7C8: (['Расчёт первой координаты со степенным масштабом.'], None),
    0xD7CD: (['Сброс Carry перед прибавлением Output1, последующий Carry суммы сохраняется для экранного SBC.'], None),
    0xD7D0: (['Сохранение глубины для второй оси, запись не меняет флаги первой суммы.'], None),
    0xD7D4: ([], 'переход, если первая переведённая координата неотрицательна, модуль уже получен'),
    0xD7D7: (['Расчёт абсолютного слова первой координаты, 8000 остаётся 8000, CPL сохраняет Sign и Carry суммы.'], None),
    0xD99D: (['-----------------------------------------', 'Экранное слово первой оси', 'Восстановление знакового контекста и его Carry после деления.'], None),
    0xD99E: (['Чтение центра первой оси, сырой BC обычно является дополнением частного.'], None),
    0xD9A1: ([], 'переход, если первая переведённая координата отрицательна, прибавить сырой BC к центру'),
    0xD9A4: (['Расчёт центра минус сырой BC и Carry исходного сложения первой координаты.'], None),
    0xD9A9: (['Расчёт центра плюс сырой BC для отрицательной первой координаты.'], None),
    0xD9AA: (['Сохранение первого слова до расчёта второй оси, последующий отказ его не отменяет.'], None),
    0xD9AB: (['-----------------------------------------', 'Вторая координата', 'Чтение исходного D из основного набора и возврат к рабочему набору.'], None),
    0xD9AE: (['Знаковое расширение второй локальной координаты.'], None),
    0xD9B5: (['Чтение Output0 и выбор одинакового степенного масштаба второй оси.'], None),
    0xD9BA: (['Расчёт второй координаты со степенным масштабом.'], None),
    0xD9BF: (['Сброс Carry до прибавления Output0, его новый Carry участвует в конечном SBC.'], None),
    0xD9C2: (['Восстановление глубины из ранее записанного SavedDepth.'], None),
    0xD9C5: ([], 'переход, если вторая переведённая координата неотрицательна, модуль уже получен'),
    0xD9C8: (['Расчёт абсолютного слова второй координаты с сохранением Sign и Carry её суммы.'], None),
    0xDB8E: (['-----------------------------------------', 'Экранное слово второй оси', 'Восстановление контекста второй суммы после делителя.'], None),
    0xDB8F: (['Чтение центра второй оси.'], None),
    0xDB92: ([], 'переход, если вторая переведённая координата отрицательна, прибавить сырой BC к центру'),
    0xDB95: (['Расчёт центра минус сырой BC и Carry исходной суммы второй координаты.'], None),
    0xDB97: (['Запись второго слова, начавшаяся на входном SP-4.'], None),
    0xDB98: (['Расчёт следующего рабочего SP после двух PUSH, размер записи плюс четыре уже записанных байта.'], None),
    0xDB9F: (['Расчёт центра плюс сырой BC при отрицательной второй координате и сохранение слова.'], None),
    0xDBA1: (['Расчёт следующего рабочего SP после двух записанных слов.'], None),
    0xDBA8: (['-----------------------------------------', 'Отказ глубины либо первой оси', 'Сохранение исходной базы при отрицательной глубине либо принятой глубины при отказе первой оси.'], None),
    0xDBA9: (['Формирование полного числового кода 80 в старшем байте второго слова, младший байт глубины сохраняется.'], None),
    0xDBAC: (['Расчёт следующего рабочего SP, косвенное продолжение вернётся к основному HL.'], None),
    0xDBB3: (['-----------------------------------------', 'Отказ второй оси', 'Первое слово уже записано, второе получает код 80 и младший байт принятой глубины.'], None),
    0xDBB6: (['Расчёт следующего рабочего SP без отмены первого слова.'], None)}
SHIFTS = (0xD7E5, 0xD7EB, 0xD7F1, 0xD7F7, 0xD7FD, 0xD803, 0xD809, 0xD80F,
          0xD815, 0xD81B, 0xD822, 0xD828, 0xD82E, 0xD834, 0xD83A, 0xD840)
LEADS = (0xD84B, 0xD851, 0xD857, 0xD85D, 0xD863, 0xD869, 0xD86F, 0xD875,
         0xD87B, 0xD882, 0xD888, 0xD88E, 0xD894, 0xD89A, 0xD8A0, 0xD8A6)
SPLITS = (0xD8AE, 0xD8B5, 0xD8BC, 0xD8C3, 0xD8CA, 0xD8D1, 0xD8D8, 0xD8DF,
          0xD8E6, 0xD8ED, 0xD8F4, 0xD8FB, 0xD902, 0xD909, 0xD910)
TRIALS = (0xD924, 0xD92D, 0xD935, 0xD93D, 0xD945, 0xD94D, 0xD955, 0xD95D,
          0xD965, 0xD96C, 0xD973, 0xD97A, 0xD981, 0xD988, 0xD98F, 0xD996)
for prefix, delta, ordinal in (('First', 0, 'первой'), ('Second', 0x1F1, 'второй')):
    COMMENTS[0xD7DE + delta] = (['-----------------------------------------', 'Деление ' + ordinal + ' оси',
        'Сохранение знака и Carry суммы в AF\', проверка старшего байта глубины перед нормализацией.'], None)
    COMMENTS[0xD7E1 + delta] = ([], 'переход, если HIGH(depth)=0, начать деление без вводимых нормализацией единиц')
    for index, (shift, lead) in enumerate(zip(SHIFTS, LEADS), 1):
        LOCAL[lead + delta] = prefix + 'Lead' + format(index, '02d')
        COMMENTS[shift + delta] = (['Расчёт нормализованного числителя ' + ordinal + ' оси, SLL вводит единицу в младший разряд.'], None)
        branch = shift + (5 if index == 10 else 4) + delta
        COMMENTS[branch] = ([], 'переход, если из модуля ' + ordinal + ' оси вышел старший ненулевой разряд, продолжить нормализацию')
        if index < 16:
            COMMENTS[lead + 1 + delta] = (['Проверка накопленного старшего байта числителя относительно HIGH(depth).'], None)
            branch = lead + (3 if index == 9 else 2) + delta
            COMMENTS[branch] = ([], 'переход, если накопленный старший байт не меньше HIGH(depth), разделить числитель на части')
    COMMENTS[0xD847 + delta] = (['Модуль равен нулю при HIGH(depth) не равном нулю, сформировать сырой BC=0 без дополнения.'], None)
    for index, address in enumerate(SPLITS, 1):
        LOCAL[address + delta] = prefix + 'Split' + format(index, '02d')
        COMMENTS[address + delta] = (['Преобразование нормализованного числителя после ' + str(index) + ' сдвигов к пробному остатку и байту частного.'], None)
    LOCAL[0xD917 + delta] = prefix + 'LowDepth'
    COMMENTS[0xD917 + delta] = (['Подготовка первого пробного остатка из старшего байта модуля, младший байт переходит в A.'], None)
    COMMENTS[0xD91B + delta] = (['Проверка переполнения целой части частного с учётом полного depth.'], None)
    COMMENTS[0xD91D + delta] = ([], 'переход, если старший байт модуля не меньше depth, записать отказ ' + ordinal + ' оси')
    for index, address in enumerate(TRIALS):
        bit = 15 - index
        LOCAL[address + delta] = prefix + ('Range15' if index == 0 else 'Bit' + format(bit, '02d'))
        COMMENTS[address + delta] = (['Пробное вычитание depth для разряда ' + str(bit) + ' дополненного частного ' + ordinal + ' оси.'], None)
        if index == 0:
            COMMENTS[address + 2 + delta] = ([], 'переход, если частное требует разряда 15, записать отказ ' + ordinal + ' оси')
        else:
            LOCAL[address + 5 + delta] = prefix + 'Keep' + format(bit, '02d')
            COMMENTS[address + 2 + delta] = ([], 'переход, если пробное вычитание depth не дало займа, оставить уменьшенный остаток')
            COMMENTS[address + 4 + delta] = (['Восстановление отрицательного остатка прибавлением depth, Carry задаёт дополненный разряд.'], None)
            COMMENTS[address + 5 + delta] = (['Формирование дополненного разряда частного из Carry, H и N очищаются инструкцией RLA.'], None)
    COMMENTS[0xD99C + delta] = (['Сохранение младшего байта сырого дополненного частного, нулевой специальный путь оставляет BC=0.'], None)


def name_operands(region, function_address, operation):
    if region != 'Action' or function_address != 0xD7A0:
        return operation
    for address, name in ((0xD7A2, 'ActionPatchedVectorState.Output2'), (0xD7C4, 'ActionPatchedVectorState.Output1'),
                          (0xD9B6, 'ActionPatchedVectorState.Output0'), (0xD9C3, 'ActionPerspectiveState.SavedDepth')):
        operation = operation.replace('(#' + format(address, '04X') + ')', '(@' + name + ')')
    operation = operation.replace('LD HL, #0030', 'LD HL, @ActionPerspectiveConst.FirstCentre')
    operation = operation.replace('LD HL, #0080', 'LD HL, @ActionPerspectiveConst.SecondCentre')
    operation = operation.replace('LD D, #80', 'LD D, @ActionPerspectiveConst.RejectedHigh')
    operation = operation.replace('LD HL, #0009', 'LD HL, FRenderProjectedPoint + FRenderProjectedPoint.ClipCode')
    return operation


def structure_text():
    lines = ['', '                ; Создаваемая перспективой runtime-запись, пятый байт сохраняется',
             '                struct FRenderProjectedPoint']
    for field, declaration, note in (('Second', 'dw #0000', 'второе экранное слово, при отказе high=80 и low=LOW(depth)'),
        ('First', 'dw #0000', 'первое экранное слово либо глубина при раннем отказе'),
        ('ClipCode', 'db #00', 'парные признаки границ заполняет ClassifyProjectedVertices, перспектива байт сохраняет')):
        lines.append((field.ljust(16) + declaration).ljust(80) + '; ' + note)
    return '\n'.join(lines + ['                ends', '                assert FRenderProjectedPoint == #05',
        '                assert FRenderProjectedPoint.Second == #00', '                assert FRenderProjectedPoint.First == #02',
        '                assert FRenderProjectedPoint.ClipCode == #04', ''])


def constant_text():
    lines = ['', '                ; Исходные центры и полный код отказа перспективы ACTION', '                module ActionPerspectiveConst']
    for field, value, note in (('FirstCentre', 48, 'исходный центр первого экранного слова'),
        ('SecondCentre', 128, 'исходный центр второго экранного слова'),
        ('RejectedHigh', 128, 'полный числовой код старшего байта при отказе, не битовая маска')):
        lines.append((field.ljust(16) + 'equ #' + format(value, '02X')).ljust(80) + '; ' + note)
    return '\n'.join(lines + ['                endmodule', ''])


INCLUDE_BLOCKS = (('Includes/Structs/Include.inc', 'struct FRenderProjectedPoint', structure_text()),
                  ('Includes/Const/Include.inc', 'module ActionPerspectiveConst', constant_text()))


def qualify_mutations(mutations, regions, functions, pieces):
    from CheckActionParameterActivation import flat_action
    from InspectZ80 import decoder
    prefix = next(p for p in pieces if p['path'] == UNCLASSIFIED_PREFIX_PATH)
    assert prefix['offset'] <= 0x75C9 < 0x75E4 < prefix['offset'] + prefix['length']
    body = {i.address: i for i in decoder(flat_action()).disassemble(0xD5C9, 0xD5E5, 'h')}
    assert body[0xD5D0].operation == 'LD HL,#9F1D' and body[0xD5D8].operation == 'LD A,#06' and body[0xD5DA].operation == 'SUB (HL)'
    region = next(r for r in regions if r['name'] == 'Action')
    runtime_targets = set(region['roots'])
    for writer, target, instruction in ((0xD5DB, 0xD7AC, 0xD7AB), (0xD5DE, 0xD7C7, 0xD7C6), (0xD5E1, 0xD9B9, 0xD9B8)):
        assert body[writer].operation == 'LD (#' + format(target, '04X') + '),A'
        owner = next(i for i in region['instructions'] if i['address'] == instruction)
        assert owner['operation'] == 'JR #' + format(instruction, '04X') and owner['hex'] == '18fe'
        assert not any(m['region'] == 'Action' and m['writer'] == writer for m in mutations)
        destinations = [instruction + 2 + skip for skip in range(6)]
        runtime_targets.update(destinations)
        mutations.append(dict(region='Action', writer=writer, writer_bank=0, writer_slot=17, writer_offset=writer - 0x6000,
            writer_source_classified=False, writer_original_hex=body[writer].bytes.hex(), path=prefix['path'],
            target=target, target_instruction=instruction, size=1, target_operation=owner['operation'], target_bank=0,
            target_region='Action', target_slot=17, target_offset=target - 0x6000, target_source_classified=True,
            target_path='Source/Action/ProjectRenderVertex.asm', runtime_value='6 - byte[9F1D]',
            contract_values=list(range(6)), runtime_targets=destinations))
    region['roots'] = sorted(runtime_targets)
    mutations.sort(key=lambda m: (m['region'], m['writer'], m['target']))

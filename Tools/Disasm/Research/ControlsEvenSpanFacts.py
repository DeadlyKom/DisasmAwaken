"""Динамический выбор хвоста обратного заполнения чётного числа байтов."""
FUNCTIONS = {
    0xCEA4:('FillEvenSpan','Обратное заполнение 2*A байтов через изменяемый JR в пределах страницы'),
    0xCEB7:('FillEvenSpanHead','Первые 12 записей общего 30-байтового хвоста заполнителя'),
    0xCECF:('FillEvenSpanTail','Последние 18 записей заполнителя, восстановление HL и чтение направления')}
LOCAL = {0xCEB3:'SelectTail',0xCEF4:'ReadDirection'}
for count in range(1,16):
    address = 0xCEF3-4*count
    if address not in FUNCTIONS:
        LOCAL[address] = 'Fill'+str(count*2)
LABELS = {('Controls',address):name for address,name in LOCAL.items()}
RENAMES = {'Controls.UnknownCEA4.Entry':'Controls.FillEvenSpan.Entry',
    'Controls.UnknownCEA4.PointCEB3':'Controls.FillEvenSpan.SelectTail',
    'Controls.UnknownCEB7.Entry':'Controls.FillEvenSpanHead.Entry',
    'Controls.UnknownCECF.Entry':'Controls.FillEvenSpanTail.Entry',
    'Controls.UnknownCECF.PointCEF4':'Controls.FillEvenSpanTail.ReadDirection'}
CONTINUATIONS = {0xCEB7:0xCECF}
CONTRACTS = {
    ('Controls',0xCEA4):(
        ['HL задаёт H страницы назначения, DE задаёт D как правую исключённую границу внутри страницы',
         'AF задаёт A=0..15 как половину длины, IXL содержит байт заполнения',
         'банк 1 выбран, код, стек и назначение доступны для записи и не перекрываются',
         'на CPU-стеке внешний возврат, для сохранения HL нужны ещё два байта, IRQ не вмешиваются'],
        ['HL=256*входной H+входной D, DE и BC сохраняются',
         'AF содержит A=Direction и F от AND A, Z проверяет нулевой Direction, H=1, N=0, Carry=0',
         'при A=1..15 записаны 2*A байтов IXL справа налево, DEC L не переносит заём в H',
         "HL', DE', BC', AF', IX и IY, I, IM и IFF сохраняются, SP=входной SP+2",
         'R получает 6 M1 при A=0 либо 16+4*A M1 при A=1..15'],
        ['HL, AF, операнд TailOffset, назначение, два байта CPU-стека, R'],
        ['нулевой счётчик не меняет RAM, A=80 также пропускает заполнение из-за нулевого результата ADD A,A',
         'A=10 задаёт исходное смещение FE и зацикливает SelectTail, в этом примечании число шестнадцатеричное',
         'прочие значения A вне договора, допустимость аргументов всех игровых вызывающих процедур отдельно не доказана',
         'изменяемый JR не выбирает CEB5..CEB6, условный прямой вход CEB5 описан в FillSpan31']),
    ('Controls',0xCEB7):(
        ['HL указывает правую исключённую границу внутри страницы, AF задаёт A как байт заполнения',
         'банк 1 выбран, на CPU-стеке слово SavedHL, затем внешний возврат',
         'стек и назначение не перекрываются с кодом, IRQ не вмешиваются'],
        ['HL восстанавливается из SavedHL, DE и BC сохраняются, 30 байтов записаны исходным A справа налево',
         'AF содержит Direction и F от AND A, младший байт адреса оборачивается без изменения H',
         "HL', DE', BC', AF', IX и IY, I, IM и IFF сохраняются, SP=входной SP+4, R получает 64 M1"],
        ['HL, AF, 30 байтов назначения, R'],
        ['(1) этот файл исполняет 12 записей, затем без инструкции JP продолжается (2) FillEvenSpanTail.asm',
         'динамические входы Fill28, Fill26, Fill24, Fill22 и Fill20 уменьшают общее число записей на 2..10']),
    ('Controls',0xCECF):(
        ['HL указывает правую исключённую границу внутри страницы, AF задаёт A как байт заполнения',
         'банк 1 выбран, на CPU-стеке слово SavedHL, затем внешний возврат, IRQ не вмешиваются'],
        ['HL восстанавливается из SavedHL, DE и BC сохраняются, 18 байтов записаны исходным A справа налево',
         'AF содержит Direction и F от AND A, Z установлен только при нулевом Direction',
         "HL', DE', BC', AF', IX и IY, I, IM и IFF сохраняются, SP=входной SP+4, R получает 40 M1"],
        ['HL, AF, 18 байтов назначения, R'],
        ['(2) порядок после (1) FillEvenSpanHead.asm обязателен при последовательном исполнении',
         'Fill16..Fill2 являются динамическими входами с длиной из имени и той же рамкой SavedHL',
         'ReadDirection является самостоятельным входом без SavedHL, только читает Direction и выполняет RET',
         'ReadDirection сохраняет HL, DE, BC и всю RAM, изменяет AF и R на три M1, SP увеличивается на два'])}
COMMENTS = {
    0xCEA4:(['выбор правой исключённой границы в L без изменения H страницы назначения'],None),
    0xCEA5:(['проверка удвоенной длины, A=0 и A=80 дают нулевой результат'],None),
    0xCEA6:([], 'переход, если удвоенная длина равна нулю, прочитать Direction через ReadDirection без сохранения HL'),
    0xCEA8:(['сохранение указателя с выбранным правым краем для общего POP HL после заполнения'],None),
    0xCEA9:(['вычисление смещения JR как 62-4*A, при A=1..15 выбираются хвосты длиной 2*A'],None),
    0xCEAE:(['обновление существующего операнда TailOffset для выбора точки входа в цепочку'],None),
    0xCEB1:(['выбор байта заполнения из IXL перед динамическим переходом'],None),
    0xCEB3:(['переход по изменяемому TailOffset, исходное FE означает цикл без продвижения'],None),
    0xCEB7:(['-----------------------------------------','(1) Начало общего хвоста, 12 записей перед FillEvenSpanTail','-----------------------------------------'],None),
    0xCECF:(['-----------------------------------------','(2) Конец общего хвоста, 18 записей и общий возврат','-----------------------------------------'],None),
    0xCEF3:(['восстановление указателя из SavedHL после последней записи'],None),
    0xCEF4:(['чтение общего Direction для выбора дальнейшего пути вызывающей процедуры'],None),
    0xCEF7:(['проверка нулевого Direction, результат заполнения на Z не влияет'],None),
    0xCEF8:(['-----------------------------------------'],None)}
for count in range(1,16):
    address = 0xCEF3-4*count
    before,right = COMMENTS.get(address,([],None))
    COMMENTS[address] = (before+['динамический вход на '+str(count*2)+' байтов справа налево, заём младшего адреса не изменяет страницу'],right)


def name_operands(region,function_address,operation):
    if region == 'Controls' and function_address in FUNCTIONS:
        operation = operation.replace('(#CEB4)','(@ControlsEvenSpanState.TailOffset)')
        operation = operation.replace('(#D18B)','(@ControlsEvenSpanState.Direction)')
    return operation

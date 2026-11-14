"""Полный DE10 на исходных таблицах, включая конечный EXX и изменяемый операнд ACTION."""
FUNCTIONS = {0xDE10: ('BuildParameterTables', 'Формирование пятнадцати параметров и девяти строковых значений по зерну и исходным таблицам')}
LOCAL = {0xDE25:'SelectTemplates',0xDE3F:'BuildField',0xDE4C:'SubtractSteps',0xDE51:'ScalePositive',
         0xDE56:'AddSteps',0xDE59:'ShiftField',0xDE5B:'ShiftUntilOne',0xDE63:'AddBases',0xDE8E:'WriteRows'}
LABELS = {('Controls',address):name for address,name in LOCAL.items()}
CONTINUATIONS = {}
RENAMES = {'Controls.UnknownDE10.Entry':'Controls.BuildParameterTables.Entry',
    **{'Controls.UnknownDE10.Point'+format(a,'04X'):'Controls.BuildParameterTables.'+name for a,name in LOCAL.items()}}
CONTRACTS = {('Controls',0xDE10): (
    ['HL, DE, BC и AF основных аргументов не задают, первое зерно читается из SeedFirst, второе из SeedSecond, управляющий байт из StepControl',
     "входные HL' и DE' становятся основными выходными HL и DE из-за конечного EXX, остальные альтернативные входы не задают числовых параметров",
     'банк 1 выбран, общее ядро ACTION перенесено, используются исходные таблицы параметров, строк и пятнадцать FParameterCoefficient',
     'физический FWordRandomState, Parameters, ClassLimits и операнд SeedIndex по 688B доступны для записи',
     'на CPU-стеке внешний возврат, ещё восемь байтов нужны вложенной цепочке, стек не перекрывает код, таблицы и рабочие данные, IRQ не вмешиваются'],
    ["HL=входной HL', DE=входной DE', BC=0000 OR C, где C является средним четырёхбитным индексом BuildSeededIndices",
     'Parameters содержит 15 вычисленных байтов, ClassLimits содержит девять записей через RowStride=6, промежутки не меняются',
     'A равен последнему строковому шаблону плюс C по модулю байта, F=28 OR (F этого ADD AND C4)',
     "HL'=7BCD, DE'=RowTemplates+16*G+9, BC'=0006, A' равен последнему Parameters[14], F' от последнего сложения с байтом шаблона параметра",
     'IX=9BB3, IY, I, IM и IFF сохраняются, SP=входной SP+2',
     'SeedIndex содержит индекс свёртки зерна 0..6, физическое состояние генератора соответствует всем K шагам',
     'R учитывает настоящие вызовы и длины исходных циклов, точный счёт каждого пути проверен независимой моделью'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', IX, Parameters, девять ClassLimits, SeedIndex, состояние генератора, восемь байтов CPU-стека, R"],
    ['полная цепочка пишет вне стека только SeedIndex=688B, состояние 9B15..9B18, Parameters=9BA4..9BB2 и ClassLimits=7B97+6*i при i=0..8, стек занимает входной SP-8..SP-1',
     'G равен старшему индексу BuildSeededIndices, но при нулевом индексе свёртки заменяется DefaultGroup=3',
     'в исходной таблице код наклона 01 означает ноль, 02 означает плюс C, FE означает минус C, число SRA задаётся степенью двойки ShiftMask',
     'шаблон параметров G=4 читает байты начала самой таблицы коэффициентов со смещением один, перекрытие сохраняется без копирования',
     '688B является операндом LD A, n по 688A общего ядра ACTION, это настоящая самомодификация',
     'последний EXX не компенсируется перед RET, описанный основной и альтернативный наборы нельзя менять местами',
     'пятнадцать полей имеют имена по доказанным потребителям ApplyParameterSet, полный игровой смысл Unknown11 не установлен',
     'маршруты полей описаны в ActionApplyParameters.md, физический набор находится в Action/Data/ParameterSet.asm',
     'девять ClassLimits меняют операнды CP выбора классов 0..8 ScheduleSpawn, первая граница сравнивает скорректированное значение'])}
COMMENTS = {
    0xDE10: (['загрузка двух слов зерна и числа шагов из существующего контекста'],None),
    0xDE1A: (['формирование числовых индексов настоящей цепочкой классификатора и генератора'],None),
    0xDE1D: (['обновление операнда LD A, n по 688A общего ядра ACTION индексом свёртки зерна'],None),
    0xDE20: (['проверка нулевого индекса свёртки перед выбором группы шаблонов'],None),
    0xDE21: ([], 'переход, если индекс свёртки ненулевой, использовать вычисленную группу H'),
    0xDE23: (['выбор DefaultGroup для нулевого индекса свёртки'],None),
    0xDE25: (['вычисление смещения группы как 16*H, диапазон H=0..4 исключает циклическое переполнение'],None),
    0xDE2D: (['вычисление среднего индекса C=0..15 из исходного L=1..16'],None),
    0xDE2F: (['сохранение группового смещения для последующего строкового шаблона'],None),
    0xDE30: (['вычисление указателя выбранного шаблона параметров без дублирования перекрытых байтов'],None),
    0xDE35: (['сохранение среднего индекса C для последующего перехода в альтернативный BC'],None),
    0xDE36: (['выбор первого кода наклона физической трёхбайтовой записи'],None),
    0xDE39: (['подготовка выхода на 15 последовательных байтов Parameters'],None),
    0xDE3F: (['сохранение счётчика полей в альтернативном AF на время вычисления значения'],None),
    0xDE40: (['проверка знака кода наклона, исходные значения 01, 02 и FE задают ноль, плюс C и минус C'],None),
    0xDE42: ([], 'переход, если код наклона неотрицательный, обработать 01 либо 02'),
    0xDE45: (['вычисление числа вычитаний как модуль отрицательного кода минус один'],None),
    0xDE48: ([], 'переход, если число вычитаний нулевое, продолжить с нулевой величиной'),
    0xDE4A: (['подготовка исходной отрицательной суммы, для FE выполняется одно вычитание C'],None),
    0xDE51: (['вычисление числа сложений как положительный код минус один'],None),
    0xDE52: ([], 'переход, если код наклона равен 01, продолжить с нулевой величиной'),
    0xDE54: (['подготовка исходной положительной суммы, для 02 выполняется одно сложение C'],None),
    0xDE59: (['чтение ShiftMask, позиция единственной единицы задаёт число арифметических сдвигов'],None),
    0xDE5B: (['поиск младшей единицы ShiftMask с одновременным масштабированием знаковой суммы'],None),
    0xDE5D: ([], 'переход, если младший проверяемый разряд ShiftMask установлен, масштабирование закончено'),
    0xDE63: (['выбор поля Base текущего FParameterCoefficient и прибавление его к масштабированной величине'],None),
    0xDE66: (['прибавление байта выбранного группового шаблона к вычисленному полю'],None),
    0xDE69: (['обновление очередного физического байта Parameters'],None),
    0xDE6C: (['переход к следующему шаблонному байту, выходному байту и коду наклона, физический шаг правила равен трём'],None),
    0xDE73: (['восстановление счётчика полей и сохранение последнего значения с его F в альтернативном AF'],None),
    0xDE74: (['проверка числа оставшихся полей после записи очередного результата'],None),
    0xDE75: ([], 'переход, если обработаны ещё не все RecordCount полей'),
    0xDE78: (['восстановление среднего индекса в альтернативный C, затем выбор ранее сохранённой группы строк'],None),
    0xDE7C: (['вычисление указателя строкового шаблона RowTemplates+16*G'],None),
    0xDE81: (['подготовка девяти записей ClassLimits с физическим шагом RowStride'],None),
    0xDE87: (['обновление первой строки без прибавления среднего индекса'],None),
    0xDE8B: (['переход в альтернативный набор для счётчика восьми строк, этот EXX перед RET не компенсируется'],None),
    0xDE8E: (['чтение следующего шаблонного байта через основной указатель и прибавление сохранённого среднего индекса'],None),
    0xDE93: (['обновление очередной строки, ADD HL, BC оставляет S, Z, PV от байтового сложения, но заменяет H, N, C и биты 5, 3'],None),
}


def name_operands(region,function_address,operation):
    if region=='Controls' and function_address==0xDE10:
        for address,name in ((0x9BC1,'SeedFirst'),(0x9BC3,'SeedSecond'),(0x9BC5,'StepControl'),(0x688B,'SeedIndex')):
            operation = operation.replace('(#'+format(address,'04X')+')','(@ControlsParameterTablesState.'+name+')')
        for value,name in ((0xDF25,'ValueTemplates'),(0xDEDC,'RowTemplates'),(6,'RowStride')):
            operation = operation.replace('#'+format(value,'04X'),'@ControlsParameterTablesConst.'+name)
        operation = operation.replace('#DF65','@ControlsParameterCoefficients.Field00.SlopeCode')
        operation = operation.replace('#9BA4','@ControlsParameterTablesState.Parameters')
        operation = operation.replace('#7B97','@ControlsParameterTablesState.ClassLimits')
        operation = operation.replace('LD H, #03','LD H, @ControlsParameterTablesConst.DefaultGroup')
        operation = operation.replace('LD A, #0F','LD A, @ControlsParameterTablesConst.RecordCount')
        operation = operation.replace('LD B, #08','LD B, @ControlsParameterTablesConst.ExtraRows')
    return operation


def shared_mutation(regions,functions):
    """Проверка единственной доказанной записи Controls в перенесённый общий код ACTION."""
    controls = next(region for region in regions if region['name']=='Controls')
    action = next(region for region in regions if region['name']=='Action')
    writer = next(i for i in controls['instructions'] if i['address']==0xDE1D)
    target = next(i for i in action['instructions'] if i['address']==0x688A)
    assert writer['operation']=='LD (#688B),A' and target['operation']=='LD A,#00'
    assert target['slot']==17 and target['offset']==0xAC7
    owner = next(f for f in functions if f['region']=='Controls' and f['address']==0xDE10)
    target_owner = next(f for f in functions if f['region']=='Action'
        and f['address']<=0x688A<f['address']+f['end_offset']-f['offset'])
    return dict(region='Controls',writer=0xDE1D,target=0x688B,target_instruction=0x688A,size=1,
        target_operation=target['operation'],path=owner['path'],writer_bank=1,target_bank=5,
        target_region='Action',target_slot=17,target_offset=0xAC8,target_path=target_owner['path'])

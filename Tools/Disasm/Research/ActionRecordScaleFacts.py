"""Подготовка трёх вычитаемых слов и выбор входа в цепь удвоений по исходному заголовку модели."""
from ActionOffsetRestoreFacts import name_operands as offset_names
FUNCTIONS={0xE55C:('PrepareRecordScale','Сохранение CPU SP, временное деление смещений класса 14 и выбор числа удвоений по заголовку модели')}
LOCAL={0xE58E:'ReadModelScale',0xE59D:'DispatchScale'}
LABELS={('Action',a):n for a,n in LOCAL.items()}
RENAMES={'Action.UnknownE55C.Entry':'Action.PrepareRecordScale.Entry',
    'Action.UnknownE55C.PointE58E':'Action.PrepareRecordScale.ReadModelScale',
    'Action.UnknownE55C.PointE59D':'Action.PrepareRecordScale.DispatchScale'}
LOCATION={0xE55C:'окно ACTION банка 0'}
CONTINUATIONS={}
CONTRACTS={('Action',0xE55C):(
    ['HL, DE, BC и AF не задают числовых аргументов, DE и BC сохраняются',
     'IX - адрес FActionRecord, ClassCode доступен для чтения, ModelOffset содержит чётное смещение исходной таблицы моделей 9E00',
     'таблица 128 указателей и OBJECT3D в банке 4 соответствуют оригиналу, старший байт первого слова модели e лежит в диапазоне 1..5',
     'Active0..2 доступны для чтения и записи, Original0..2 и SavedCpuSP доступны для записи, при ClassCode=14 нужны все три исходных слова',
     '7FFD не заблокирован, в окне C000 выбран банк 0, IRQ не вмешивается, CPU-стек допускает шесть дополнительных байтов и не пересекается с записью и операндами'],
    ['HL=00C8, DE и BC сохраняются, A=6-e, F от SUB 6,e',
     "HL', DE', BC', AF', IX и IY сохраняются, I/IM/IFF сохраняются, SP равен входному SP, RET здесь не выполняется",
     'SavedCpuSP равен входному SP, ShiftSkip=6-e, PC=E59F+6-e, это один из входов E5A0..E5A4',
     'при ClassCode=14 Original0..2 получают исходные Active0..2, активные слова заменяются знаковыми половинами с округлением вниз',
     'при другом классе Active0..2 и Original0..2 сохраняются, запись FActionRecord не меняется',
     'OUT 7FFD получает 14 и 10, итоговый банк 0 с ROM 1, R получает 62 M1 для класса 14 и 41 M1 для другого класса',
     'записаны шесть временных байтов под входным SP, после выхода они не восстановлены'],
    ['HL, AF, R, SavedCpuSP, ShiftSkip, шесть байтов CPU-стека, 7FFD',
     'Active0..2 и Original0..2 только при ClassCode=14'],
    ['значения Active и Original являются существующими операндами исполняемого кода, дополнительная память не выделяется',
     'исходный JR по E59D содержит FE и возвращается на себя, перед исполнением этот байт обязательно заменяется на 6-e',
     'после перехода остаётся e-1 инструкций ADD HL,HL, они расположены уже в UpdateRecordComponents и не выполняются внутри этого договора',
     'последующее значение HL=200*2^(e-1), потребитель вычисляет B=125-H, это не доказательство всего обновления записи',
     '32768 сценариев выполнили настоящий ReadObjectHeaderWord и селектор страниц для всех 128 исходных указателей и всех кодов класса',
     'проверены регистры включая R, все восемь банков RAM и кратность записей, порядок аппаратных шинных циклов не доказан',
     'нечётные индексы, изменённые заголовки, игровые имена классов, IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
    0xE55C:(['-----------------------------------------','Сохранение CPU-стека','Сохранение исходного SP в операнд восстановления, следующий обработчик использует SP для чтения и записи компонент.'],None),
    0xE560:(['Проверка полного кода ClassCode, только HalvedClass требует временно уменьшенных вычитаемых слов.'],None),
    0xE565:([],'переход, если ClassCode отличается от HalvedClass и делить смещения не требуется'),
    0xE567:(['-----------------------------------------','Временные смещения класса 14','Чтение Active0 и сохранение исходного значения в Original0 для RestoreHalvedOffsets.'],None),
    0xE56D:(['Расчёт знаковой половины Active0, отрицательное нечётное слово округляется вниз.'],None),
    0xE571:(['Обновление Active0 для следующего вычитания из Component0.'],None),
    0xE574:(['Чтение Active1 и сохранение исходного значения в Original1.'],None),
    0xE57A:(['Расчёт знаковой половины Active1 с сохранением знакового разряда.'],None),
    0xE57E:(['Обновление Active1 для следующего вычитания из Component1.'],None),
    0xE581:(['Чтение Active2 и сохранение исходного значения в Original2.'],None),
    0xE587:(['Расчёт знаковой половины Active2 с округлением отрицательных нечётных слов вниз.'],None),
    0xE58B:(['Обновление Active2 для следующего вычитания из Component2.'],None),
    0xE58E:(['-----------------------------------------','Выбор числа удвоений','Чтение ModelOffset как байтового смещения таблицы моделей, байтовое смещение используется всеми установленными читателями заголовка.'],None),
    0xE591:(['Чтение первого слова исходной модели с настоящим переключением банка 4 и возвратом к банку 0.'],None),
    0xE594:(['Расчёт числа пропускаемых удвоений, старший байт e исходного заголовка лежит в диапазоне 1..5.'],None),
    0xE597:(['Подготовка начального значения 200, фактические удвоения выполняются после изменяемого JR.'],None),
    0xE59A:(['Обновление смещения ShiftSkip в JR, цель равна адресу следующего байта E59F плюс 6-e.'],None),
    0xE59D:(['-----------------------------------------','Передача в цепь удвоений','Исходный FE заменён на 6-e, исполнение продолжается по E5A0..E5A4 внутри UpdateRecordComponents.asm.'],
        'после изменения ShiftSkip продолжение в выбранной точке цепи удвоений')}


def name_operands(region,address,operation):
    operation=offset_names(region,address,operation)
    if (region,address)!=('Action',0xE55C):return operation
    return operation.replace('(IX+#06)','(IX+FActionRecord.ModelOffset)').replace('(#E59E)',
        '(@ActionRecordScaleState.ShiftSkip)').replace('LD A, #06','LD A, @ActionRecordScaleConst.SkipBase').replace(
        '#00C8','@ActionRecordScaleConst.InitialValue')


def qualify_mutations(records,regions,functions):
    for item in records:
        if item['region']!='Action' or not 0xE55C<=item['writer']<0xE59F:continue
        target=item['target'];item.update(writer_bank=0,writer_offset=item['writer']-0x6000,writer_source_classified=True,
            target_region='Action',target_bank=0,target_slot=17,target_offset=target-0x6000,target_source_classified=True)
        if target==0xE59E:item['target_path']='Source/Action/PrepareRecordScale.asm'
        elif target in (0xE68C,0xE692,0xE698):item['target_path']='Source/Action/RestoreHalvedOffsets.asm'
        else:
            assert target in (0xE605,0xE5B3,0xE5D2,0xE5ED)
            item['target_path']='Source/Action/UpdateRecordComponents.asm'

"""Создание записи класса 20, значения неизвестных полей сохраняют исходные имена."""
FUNCTIONS={0x617D:('CreateRandomClass20Record','Создание записи класса 20 из двух случайных компонент и транспонированного преобразования')}
LOCAL={0x61A1:'PositiveX',0x61A3:'SelectYSign',0x61AB:'PositiveY',0x61AD:'SelectDepth',0x61B9:'Transform'}
CONTRACTS={('Action',0x617D):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX и IY задают сохраняемый контекст до поиска',
     'доступен исходный список FActionRecord с завершающим маркером и условиями FindReusableRecord',
     'подготовлены Stream8 и коэффициенты TransformVectorTransposed, выбрана страница 0, IRQ не вмешиваются',
     'SP содержит внешний возврат, восемь дополнительных байтов стека не пересекают код, записи и таблицы'],
    ['при отказе поиска сохранён результат FindReusableRecord, новая запись не создаётся, поиск может очистить ReuseByte пропущенных слотов',
     'при успехе IY указывает выбранный слот, Stream8 продвинут один раз, его слово даёт две знаковые байтовые компоненты',
     'компонента 0 равна 4*signed8(L) плюс 1024 при L<128 либо минус 1024 иначе, компонента 1 получена так же из H',
     'компонента 2 равна 30000 при байте 6E75=0 либо минус 30000 иначе, режим в данном входе не изменяется',
     'TransformVectorTransposed даёт HL, DE, BC, все три результата записываются в Components даже при частичном выходе преобразования',
     'новая запись получает ModelOffset=C0, фазы 0C, 1D, 37, StateCode=04, ClassCode=14, Unknown13=FA',
     'ReuseByte, LinkFlags и Unknown24 сбрасываются, TargetCodeStep, Unknown10 и TargetIndex получают 02, остальные поля сохраняются',
     "при успехе A=0 и F=44, HL, DE, BC содержат результат преобразования, HL', DE', BC' результат потока 8, AF' результат преобразования",
     'IX, I/IM/IFF и paging сохраняются, SP после внешнего RET увеличен на два, R учитывает оба пути поиска и все дочерние процедуры'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', IY, R, выбранные поля записи, Stream8, операнды и выходы преобразования, CPU-стек"],
    ['класс 14 указан шестнадцатерично и равен 20 десятично, назначение игрового объекта пока не доказано',
     'внутри участка нет проверки существования записи класса 20 и нет записи обратной связи, штатный вызывающий вход не установлен',
     'переполнение преобразования не отклоняет создание, неизменённые выходные компоненты используются согласно договору TransformVectorTransposed',
     'модель исполняет настоящий поиск, поток и транспонированное преобразование, сверяет регистры с R, восемь банков и кратность записей',
     'полное произведение матриц, состояний и полей, аппаратные IRQ, точные T, сборка и нативный запуск не проверялись'])}
COMMENTS={
    0x617D:(['Поиск свободного слота с исходным пропуском ReuseByte=FF на один проход.'],None),
    0x6180:([],'выход, если поиск не нашёл свободного слота, сохранить его результат'),
    0x6181:(['Создание двух знаковых байтов из отдельного случайного потока 8.'],None),
    0x6184:(['Преобразование старшего случайного байта в знаковое слово DE без изменения его значения.'],None),
    0x618C:(['Преобразование младшего случайного байта в знаковое слово HL и увеличение обеих компонент в четыре раза.'],None),
    0x6199:(['Проверка знака первой компоненты перед отступом от нулевой области на 1024.'],None),
    0x619B:([],'переход, если первая компонента неотрицательна, прибавить к ней 1024'),
    0x619D:(['Расчёт отрицательного отступа, сброс бита 2 старшего байта вычитает 1024 из этого диапазона.'],None),
    0x61A1:(['Расчёт положительного отступа, установка бита 2 старшего байта прибавляет 1024.'],None),
    0x61A3:(['Проверка знака второй компоненты перед таким же отступом.'],None),
    0x61A5:([],'переход, если вторая компонента неотрицательна, прибавить к ней 1024'),
    0x61AD:(['Выбор знака третьей компоненты по исходному байту режима, смысл всех его состояний ещё не установлен.'],None),
    0x61B4:([],'переход, если байт режима равен нулю, оставить третью компоненту положительной'),
    0x61B9:(['Преобразование трёх подготовленных компонент с временным транспонированием исходной матрицы.'],None),
    0x61BC:(['Создание физических Components из всех трёх выходных слов, отдельной проверки переполнения нет.'],None),
    0x61CE:(['Обновление фаз, модели, состояния и полного класса новой записи с исходными постоянными.'],None),
    0x61EA:(['Обновление флагов доступности, связи и неизвестного поля 24, остальные поля слота сохраняются.'],None),
    0x61F4:(['Обновление числового шага и двух полей исходными значениями 02 без предположений об их общем смысле.'],None),
}
STATE_MODULE='ActionClass20SpawnState'
STATE_FIELDS=(('DepthSignMode',0x6E75,'00 передний вид и +30000, ED задний вид и -30000, читается первый опкод пары'),)
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionClass20SpawnConst','''
                ; Исходные значения записи класса 20
                module ActionClass20SpawnConst
PositiveDepth   equ #7530                                                       ; положительная третья компонента, 30000
NegativeDepth   equ #8AD0                                                       ; отрицательная третья компонента, -30000
Model           equ #C0                                                         ; смещение модели в таблице заголовков
Phase0          equ #0C                                                         ; исходный код первой фазы
Phase1          equ #1D                                                         ; исходный код второй фазы
Phase2          equ #37                                                         ; исходный код третьей фазы
State           equ #04                                                         ; исходный обработчик движения
Class           equ #14                                                         ; полный класс, 20 десятично
Parameter       equ #FA                                                         ; исходное Unknown13, единицы не установлены
InitialStep     equ #02                                                         ; исходный TargetCodeStep
Unknown10Value  equ #02                                                         ; исходное значение поля Unknown10
TargetValue     equ #02                                                         ; исходное значение TargetIndex без создания связи
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0x617D):return operation
    for offset in range(6):
        operation=operation.replace('(IY+#'+format(offset,'02X')+')','(IY + @FActionRecord.Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')+')')
    for offset,name in ((6,'ModelOffset'),(7,'OffsetPhase0'),(8,'OffsetPhase1'),(9,'OffsetPhase2'),(10,'StateCode'),
                        (12,'LinkFlags'),(15,'TargetIndex'),(16,'Unknown10'),(18,'ClassCode'),(19,'Unknown13'),
                        (24,'ReuseByte'),(36,'Unknown24'),(37,'TargetCodeStep')):
        operation=operation.replace('(IY+#'+format(offset,'02X')+')','(IY + @FActionRecord.'+name+')')
    for address,name in ((0xE9A1,'FindReusableRecord'),(0xEBA3,'NextRandomWord8'),(0xACEA,'TransformVectorTransposed')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    operation=operation.replace('(#6E75)','(@ActionClass20SpawnState.DepthSignMode)')
    operation=operation.replace('LD BC, #7530','LD BC, @ActionClass20SpawnConst.PositiveDepth')
    operation=operation.replace('LD BC, #8AD0','LD BC, @ActionClass20SpawnConst.NegativeDepth')
    for field,value,name in (('ModelOffset','C0','Model'),('OffsetPhase0','0C','Phase0'),
                             ('OffsetPhase1','1D','Phase1'),('OffsetPhase2','37','Phase2'),
                             ('StateCode','04','State'),('ClassCode','14','Class'),('Unknown13','FA','Parameter'),
                             ('TargetCodeStep','02','InitialStep'),('Unknown10','02','Unknown10Value'),('TargetIndex','02','TargetValue')):
        operation=operation.replace('LD (IY + @FActionRecord.'+field+'), #'+value,
                                    'LD (IY + @FActionRecord.'+field+'), @ActionClass20SpawnConst.'+name)
    return operation

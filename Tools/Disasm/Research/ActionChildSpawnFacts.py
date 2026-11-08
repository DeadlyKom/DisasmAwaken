"""E86B, ограниченный запрос записей класса 9 с исходным EXX на раннем возврате."""
FUNCTIONS={0xE86B:('SpawnLinkedClass9Records','Условное создание одной либо двух записей класса 9 с индексом родителя и копией его связи')}
LOCAL={0xE884:'NextChild',0xE8D1:'StoreModel'}
STATE_MODULE='ActionChildSpawnState'
STATE_FIELDS=(('InitialState',0xE8F1,'существующий операнд LD (IY+StateCode),n, начальное состояние дочерних записей'),)
MODIFIED_WRITERS=((0xE870,0xE8F1,0xE8EE,1),)
CONTRACTS={('Action',0xE86B):(
    ['HL, DE и BC задают сохраняемый контекст ранних ветвей, A задаёт начальный StateCode дочерних записей',
     'IX указывает активного родителя FActionRecord, ReuseByte доступен для изменения, от A100 достижим маркер поиска свободной записи',
     'действуют договоры NextRandomWord11, FindReusableRecord и RecordAddressToIndex, записи детей доступны для изменения',
     'ACTION банка 0 выбран, четыре дополнительных байта CPU-стека доступны, IRQ и повторный вход исключены'],
    ['при установленном бите 2 ReuseByte возвращается исходный A и F от индексного BIT с входным Carry, RAM сохраняется',
     'иначе InitialState получает входной A до вызова потока 11, при новом L>=0A выполняется RET, бит 2 родителя остаётся сброшенным',
     'при L<0A бит 2 устанавливается до поиска места, прочитанный R выбирает запрос одной либо двух дочерних записей',
     'каждая найденная запись получает Components родителя плюс одно общее положительное BC-смещение, индекс родителя в Unknown20 и требуемый класс 8 в Unknown21',
     'дочерние ClassCode=9, StateCode=InitialState, SavedStateCode=0D, LinkedIndex копирует текущую связь родителя, остальные поля описаны в документации',
     'после полного создания B=0, C и DE сохраняются от входа, HL равен новому слову потока 11, A равен связи родителя, F=42',
     'при отказе FindReusableRecord возвращает AF=8042 и обменённые через EXX основные и альтернативные пары, оставшийся счётчик находится в альтернативном B',
     'при отказе бит 2 родителя не очищается, уже созданные записи сохраняются, автоматического отката нет',
     "AF', IX, I/IM/IFF и paging сохраняются, IY равен последней найденной записи либо маркеру, SP после внешнего RET увеличен на два",
     'R добавляет 3 M1 при исходно установленном бите 2 и 74 при случайном отказе, точная стоимость остальных путей приведена в документации'],
    ["HL, DE, BC, AF, HL', DE', BC', IY, R, InitialState, поток 11, бит 2 родителя, выбранные записи и до четырёх байтов CPU-стека, SP внешним RET"],
    ['число запрошенных записей зависит от реально прочитанного R, его бит 7 выбирает модель 88 либо 8C, исходные чтения не заменены случайными числами',
     'поиск не резервирует запись отдельным флагом, компоненты ребёнка с итоговым старшим байтом 80 могут снова участвовать в следующем поиске',
     'неуравновешенный EXX на раннем RET Z является исходным поведением, вызывающий код обязан учитывать его',
     '73472 сценария сравнивают реальные дети, точные регистры, флаги, R, восемь банков, значения и кратность всех записей',
     'полное произведение списков и входов, аппаратные IRQ, точные T, сборка и нативный запуск не проверялись'])}
COMMENTS={
    0xE86B:(['Проверка уже инициированного запроса детей по биту 2 родителя, остальные биты ReuseByte не трактуются этим условием.'],None),
    0xE86F:([],'выход, если бит 2 родителя установлен, не менять состояние потока и записей'),
    0xE870:(['Сохранение входного A в общий операнд начального состояния детей до случайного допуска.'],None),
    0xE873:(['Получение нового слова физического потока 11, младший байт определяет допуск.'],None),
    0xE879:([],'выход, если новый L не меньше 0A, не устанавливать бит запроса родителя'),
    0xE87A:(['Обновление бита запроса до поиска места, отказ выделения этот бит не откатывает.'],None),
    0xE87E:(['Расчёт числа запросов, младший бит реально прочитанного R плюс один даёт 1 либо 2.'],None),
    0xE884:(['Поиск следующей доступной записи с сохранением счётчика в альтернативном B через EXX.'],None),
    0xE888:([],'выход, если поиск достиг маркера, оставить пары обменёнными через EXX и сохранить уже созданных детей'),
    0xE889:(['Расчёт байтового индекса родителя и сохранение его как цели ребёнка с требуемым полным классом 8.'],None),
    0xE896:(['Расчёт одного общего смещения, старший байт 1 либо 2 и младший байт 0..127 читаются из разных R.'],None),
    0xE8A1:(['Создание трёх компонент ребёнка, к каждой компоненте родителя прибавляется один и тот же BC по модулю 65536.'],None),
    0xE8C8:(['Выбор байтового смещения модели по биту 7 прочитанного R, старый Carry на выбор не влияет.'],None),
    0xE8CD:([],'переход, если бит 7 прочитанного R установлен, сохранить ModelOffset=88'),
    0xE8D1:(['Обновление выбранной модели и исходных управляющих полей ребёнка.'],None),
    0xE8DC:(['Расчёт OffsetPhase1 из четырёх младших битов следующего прочитанного R.'],None),
    0xE8E3:(['Расчёт OffsetPhase2 из трёх младших битов отдельного чтения R.'],None),
    0xE8EA:(['Заполнение времени, начального состояния, сохранённого состояния и полного класса ребёнка.'],None),
    0xE902:(['Копирование связи родителя, этот байт отличается от индекса родителя в Unknown20.'],None),
    0xE908:(['Завершение исходных полей ребёнка, подстановка FF, управляющий код 50, байт 10 равен 1 и шаг цели 2.'],None),
    0xE918:(['Восстановление основного счётчика запросов и его уменьшение только после полностью записанного ребёнка.'],None),
    0xE91A:([],'переход, если остаётся второй запрос, снова обменять пары и искать доступную запись'),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionChildSpawnConst','''
                ; Исходные параметры создаваемой записи класса 9
                module ActionChildSpawnConst
LowLimit        equ #0A                                                         ; исключающий верхний порог нового младшего байта потока 11
RequiredClass   equ #08                                                         ; полный класс родителя, записываемый в Unknown21 ребёнка
ModelWithBit7   equ #88                                                         ; ModelOffset при установленном бите 7 R
ModelNoBit7     equ #8C                                                         ; ModelOffset при сброшенном бите 7 R
TargetLife      equ #5A                                                         ; исходный байт 0F ребёнка, полная игровая роль зависит от состояния
Phase1Mask      equ #0F                                                         ; четыре младших разряда R для OffsetPhase1
Phase2Mask      equ #07                                                         ; три младших разряда R для OffsetPhase2
TimerByte11     equ #28                                                         ; исходный счётчик байта 11, 40
SavedState      equ #0D                                                         ; состояние проверки выбранной записи после восстановления
ChildClass      equ #09                                                         ; полный класс создаваемых записей
ControlByte13   equ #32                                                         ; исходное управляющее значение байта 13, 50
InitialByte10   equ #01                                                         ; исходное управляющее значение байта 10
TargetStep      equ #02                                                         ; шаг двух фазовых кодов относительно выбранной цели
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xE86B):return operation
    for register,fields in (('IX',{0x18:'ReuseByte',0x0B:'LinkedIndex'}),('IY',{6:'ModelOffset',7:'OffsetPhase0',8:'OffsetPhase1',9:'OffsetPhase2',10:'StateCode',11:'LinkedIndex',12:'LinkFlags',15:'TargetIndex',16:'Unknown10',17:'Unknown11',18:'ClassCode',19:'Unknown13',20:'Unknown14',21:'LinkOverride',22:'SavedStateCode',32:'Unknown20',33:'Unknown21',37:'TargetCodeStep'})):
        for offset,name in fields.items():operation=operation.replace('('+register+'+#'+format(offset,'02X')+')','('+register+' + @FActionRecord.'+name+')')
    for offset in range(6):
        name='Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')
        for register in ('IX','IY'):operation=operation.replace('('+register+'+#'+format(offset,'02X')+')','('+register+' + @FActionRecord.'+name+')')
    for address,name in ((0xEBBF,'NextRandomWord11'),(0xE9A1,'FindReusableRecord'),(0xE6C7,'RecordAddressToIndex')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    operation=operation.replace('(#E8F1)','(@ActionChildSpawnState.InitialState)')
    for old,new in (('BIT 2,','BIT @ActionSelectedRecordProximityConst.ClearedReuseBit,'),('SET 2,','SET @ActionSelectedRecordProximityConst.ClearedReuseBit,'),
                    ('CP #0A','CP @ActionChildSpawnConst.LowLimit'),('AND #0F','AND @ActionChildSpawnConst.Phase1Mask'),('AND #07','AND @ActionChildSpawnConst.Phase2Mask'),
                    ('LD C, #88','LD C, @ActionChildSpawnConst.ModelWithBit7'),('LD C, #8C','LD C, @ActionChildSpawnConst.ModelNoBit7')):
        operation=operation.replace(old,new)
    for field,literal,name in (('Unknown21','08','RequiredClass'),('TargetIndex','5A','TargetLife'),('Unknown11','28','TimerByte11'),
        ('SavedStateCode','0D','SavedState'),('ClassCode','09','ChildClass'),('Unknown13','32','ControlByte13'),
        ('Unknown10','01','InitialByte10'),('TargetCodeStep','02','TargetStep')):
        operation=operation.replace('LD (IY + @FActionRecord.'+field+'), #'+literal,'LD (IY + @FActionRecord.'+field+'), @ActionChildSpawnConst.'+name)
    return operation


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer']==0xE870:
            item.update(writer_slot=17,writer_offset=0x8870,writer_bank=0,target_slot=17,target_offset=0x88F1,
                target_bank=0,target_region='Action',target_path='Source/Action/SpawnLinkedClass9Records.asm',
                target_source_classified=True,writer_source_classified=True)

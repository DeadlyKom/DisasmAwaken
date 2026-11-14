"""60E8, создание связанной ракеты и привязка целевой записи к новому индексу."""
FUNCTIONS={0x60E8:('CreateLinkedMissileRecord','Создание связанной ракеты игрока или персонажа из альтернативных компонент')}
LOCAL={0x60F1:'InitializeSlot'}
STATE_MODULE='ActionClass17SpawnState'
STATE_FIELDS=(('InitialParam',0x612E,'изменяемый операнд начального EffectReserve дочерней записи'),)
MODIFIED_WRITERS=((0x60E8,0x612E,0x612B,1),)
CONTRACTS={('Action',0x60E8):(
    ['HL и DE числовых аргументов не задают, B задаёт копируемый индекс в Phase0OrLink, C обычный индекс целевой записи', "A задаёт начальный EffectReserve, HL', DE', BC' задают три копируемых Components, A' начальный Unknown11", 'доступны исходный список FActionRecord до маркера 8080 и запись по A100+64*C, ограничение индекса не добавляется', 'перенесённый общий код банка 5, ACTION банка 0 и изменяемый InitialParam доступны, шесть дополнительных байтов CPU-стека доступны, IRQ исключены'],
    ['HL при успехе равен 0040, при отсутствии слота сохраняется', 'DE при успехе равен A100+64*C+0B, при отсутствии слота равен 0040', 'BC сохраняется', 'AF при успехе содержит A=индекс ребёнка и F=45 OR (A AND 28), при отсутствии слота A=80/F=42', "HL', DE', BC' сохраняются", "AF' равен 0044 только при успехе, при отказе исходный AF' сохраняется", 'IX сохраняется, IY указывает выделенную запись либо маркер при отказе', 'I, IM, IFF и paging сохраняются, SP после внешнего RET равен входному SP+2', 'R добавляет стоимость FindReusableRecord и ещё 88 M1 при успехе либо 5 при отказе', 'InitialParam получает входной A даже при отсутствии слота, поиск может очистить и пропустить ReuseByte=FF', 'при успехе Components ребёнка получают входные альтернативные HL, DE и BC, ModelOffset=90, OffsetPhase0/1/2=0, StateCode=8', 'при инициализации ребёнка LinkedIndex=0 и LinkFlags=0, Phase0OrLink=B, Phase2OrTarget=C', "Unknown11 получает входной A', ClassCode=11, EffectReserve получает входной A, TargetCodeStep=2, прочие поля сохраняются после действий поиска", 'затем у цели устанавливается бит 1 LinkFlags и её LinkedIndex получает индекс ребёнка, при совпадении цели с ребёнком его конечные LinkFlags=02 и LinkedIndex равен собственному индексу'],
    ["HL, DE, AF, AF', IY, R, InitialParam, выделенная запись, обратная связь цели, шесть временных байтов CPU-стека, SP внешним RET"],
    ['Unknown11 ребёнка класса 17 соответствует авторскому LZS, ноль означает ракету персонажа, неноль ракету игрока, роли поля у других классов не переопределяются', 'авторский T_ROKET=#11 и модель ROKET по смещению #90 подтверждены исходными байтами, общий вход обслуживает ракеты игрока и персонажей', 'в 275 сценариях цель совпала с ребёнком, отдельно сверены окончательные поля после обратной связи и полное число M1 всех 66560 исполнений', 'выделенные записи выровнены на 64 байта, преобразование IY даёт нулевой L и устанавливает Z/PV, успешный SCF сохраняет их, признаком успеха служит Carry', 'C=FF здесь обычный индекс и не выбирает специальную запись A780, диапазон и побочные записи исходной адресной формулы сохранены', 'OffsetScaleLow, MissileRepeatDelay, ReuseByte после очистки поиска и остальные неинициализируемые поля не зануляются дополнительно', '66560 сценариев проверили все 65536 пар B/C, все начальные параметры, занятые слоты, однократный FF-пропуск и отсутствие свободного слота', 'сверены точные регистры, флаги, R, восемь банков, кратность записей и настоящие поисковые и индексные дети', 'полное произведение входов, аппаратные IRQ, время, сборка и нативная игра не проверялись'])}
COMMENTS={
    0x60E8:(['Сохранение начального EffectReserve в исходном операнде до поиска свободной записи.'],None),
    0x60EB:(['Поиск свободного слота с сохранением обеих входных частей BC.'],None),
    0x60F0:([],'выход, если поиск достиг маркера без свободного слота, начальный параметр уже сохранён'),
    0x60F1:(['Копирование трёх Components из альтернативного набора в реальную выделенную запись.'],None),
    0x6105:(['Обновление исходных нулевых фаз, полей связи, модели и состояния дочерней записи.'],None),
    0x611D:(['Сохранение индекса стрелявшего B в Phase0OrLink и индекса цели C в Phase2OrTarget ракеты.'],None),
    0x6123:(['Преобразование альтернативного A в начальный Unknown11, альтернативный AF получает 0044 от XOR.'],None),
    0x6127:(['Обновление полного класса 17, изменяемого начального параметра и шага кодов движения.'],None),
    0x6133:(['Расчёт адреса обычной целевой записи по входному C без особой обработки FF.'],None),
    0x6137:(['Расчёт адреса LinkFlags цели и установка флага ракетной атаки до обновления её LinkedIndex.'],None),
    0x613D:(['Преобразование созданного адреса IY в обычный индекс и запись обратной ссылки у цели.'],None),
    0x6143:(['Установка Carry как результата успешного создания, остальные флаги преобразования индекса сохраняются.'],None),
}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0x60E8):return operation
    for offset in (*range(10),10,11,12,13,15,17,18,19,37):
        if offset<6:name='Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')
        else:name={6:'ModelOffset',7:'OffsetPhase0',8:'OffsetPhase1',9:'OffsetPhase2',10:'StateCode',11:'LinkedIndex',12:'LinkFlags',13:'Phase0OrLink',15:'Phase2OrTarget',17:'Unknown11',18:'ClassCode',19:'EffectReserve',37:'TargetCodeStep'}[offset]
        operation=operation.replace('(IY+#'+format(offset,'02X')+')','(IY + @FActionRecord.'+name+')')
    for address,name in ((0xE9A1,'FindReusableRecord'),(0xE6A7,'RecordIndexToAddress'),(0xE6BE,'RecordIYToIndex')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    return operation.replace('(#612E)','(@ActionClass17SpawnState.InitialParam)').replace('SET 1,','SET @ActionArrivalConst.RocketAttackBit,')


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer']==0x60E8:
            item.update(writer_slot=17,writer_offset=0x60E8-0x6000+0x23D,writer_bank=5,
                target_slot=17,target_offset=0x612E-0x6000+0x23D,target_bank=5,target_region='Action',
                target_path='Source/Action/CreateLinkedMissileRecord.asm',target_source_classified=True,writer_source_classified=True)

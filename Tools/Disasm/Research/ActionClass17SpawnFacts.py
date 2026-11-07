"""60E8, создание класса 17 и привязка целевой записи к новому индексу."""
FUNCTIONS={0x60E8:('CreateClass17LinkedRecord','Создание записи класса 17 из альтернативных компонент и обновление связи целевой записи')}
LOCAL={0x60F1:'InitializeSlot'}
STATE_MODULE='ActionClass17SpawnState'
STATE_FIELDS=(('InitialParam',0x612E,'изменяемый операнд начального Unknown13 дочерней записи'),)
MODIFIED_WRITERS=((0x60E8,0x612E,0x612B,1),)
CONTRACTS={('Action',0x60E8):(
    ['HL и DE числовых аргументов не задают, B задаёт копируемый индекс в Unknown0D, C обычный индекс целевой записи',
     "A задаёт начальный Unknown13, HL', DE', BC' задают три копируемых Components, A' начальный Unknown11",
     'доступны исходный список FActionRecord до маркера 8080 и запись по A100+64*C, ограничение индекса не добавляется',
     'перенесённый общий код банка 5, ACTION банка 0 и изменяемый InitialParam доступны, шесть дополнительных байтов CPU-стека доступны, IRQ исключены'],
    ['InitialParam получает входной A даже при отсутствии свободной записи, поиск может очистить и пропустить ReuseByte=FF',
     'при отсутствии слота A=80/F=42, HL сохраняется, DE=0040, BC сохраняется, IY указывает маркер, остальные поля не заполняются',
     'при успехе IY указывает выделенную запись, её Components получают входные альтернативные HL, DE и BC',
     'ModelOffset=90, OffsetPhase0/1/2=0, StateCode=8, LinkedIndex=0, LinkFlags=0, Unknown0D=B, TargetIndex=C',
     "Unknown11 получает входной A', ClassCode=11, Unknown13 получает входной A, TargetCodeStep=2, прочие поля сохраняются после действий поиска",
     'у целевой записи устанавливается бит 1 LinkFlags, её LinkedIndex получает обычный индекс созданной IY',
     'после успеха HL=0040, DE=A100+64*C+0B, BC сохраняется, A равен индексу ребёнка, Carry=1, остальные F от преобразования IY',
     "HL', DE', BC', IX, I/IM/IFF и paging сохраняются, AF'=0044 только при успехе, при отказе исходный AF' сохраняется",
     'SP после внешнего RET равен входному SP+2, R добавляет стоимость FindReusableRecord и ещё 88 M1 при успехе либо 5 при отказе'],
    ["HL, DE, AF, AF', IY, R, InitialParam, выделенная запись, обратная связь цели, шесть временных байтов CPU-стека, SP внешним RET"],
    ['полный ноль Z не служит признаком неудачи после успеха, индекс ребёнка 0 сохраняет Z от преобразования, успех явно задаётся Carry',
     'C=FF здесь обычный индекс и не выбирает специальную запись A780, диапазон и побочные записи исходной адресной формулы сохранены',
     'Unknown10, Unknown14, ReuseByte после очистки поиска и остальные неинициализируемые поля не зануляются дополнительно',
     '66560 сценариев проверили все 65536 пар B/C, все начальные параметры, занятые слоты, однократный FF-пропуск и отсутствие свободного слота',
     'сверены точные регистры, флаги, R, восемь банков, кратность записей и настоящие поисковые и индексные дети',
     'полное произведение входов, аппаратные IRQ, время, сборка и нативная игра не проверялись'])}
COMMENTS={
    0x60E8:(['Сохранение начального Unknown13 в исходном операнде до поиска свободной записи.'],None),
    0x60EB:(['Поиск свободного слота с сохранением обеих входных частей BC.'],None),
    0x60F0:([],'выход, если поиск достиг маркера без свободного слота, начальный параметр уже сохранён'),
    0x60F1:(['Копирование трёх Components из альтернативного набора в реальную выделенную запись.'],None),
    0x6105:(['Обновление исходных нулевых фаз, полей связи, модели и состояния дочерней записи.'],None),
    0x611D:(['Сохранение входных индексов B и C в разных физических полях ребёнка.'],None),
    0x6123:(['Преобразование альтернативного A в начальный Unknown11, альтернативный AF получает 0044 от XOR.'],None),
    0x6127:(['Обновление полного класса 17, изменяемого начального параметра и шага кодов движения.'],None),
    0x6133:(['Расчёт адреса обычной целевой записи по входному C без особой обработки FF.'],None),
    0x6137:(['Расчёт адреса LinkFlags цели и установка бита 1 до обновления её LinkedIndex.'],None),
    0x613D:(['Преобразование созданного адреса IY в обычный индекс и запись обратной ссылки у цели.'],None),
    0x6143:(['Установка Carry как результата успешного создания, остальные флаги преобразования индекса сохраняются.'],None),
}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0x60E8):return operation
    for offset in (*range(10),10,11,12,13,15,17,18,19,37):
        if offset<6:name='Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')
        else:name={6:'ModelOffset',7:'OffsetPhase0',8:'OffsetPhase1',9:'OffsetPhase2',10:'StateCode',11:'LinkedIndex',12:'LinkFlags',13:'Unknown0D',15:'TargetIndex',17:'Unknown11',18:'ClassCode',19:'Unknown13',37:'TargetCodeStep'}[offset]
        operation=operation.replace('(IY+#'+format(offset,'02X')+')','(IY + @FActionRecord.'+name+')')
    for address,name in ((0xE9A1,'FindReusableRecord'),(0xE6A7,'RecordIndexToAddress'),(0xE6BE,'RecordIYToIndex')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    return operation.replace('(#612E)','(@ActionClass17SpawnState.InitialParam)')


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer']==0x60E8:
            item.update(writer_slot=17,writer_offset=0x60E8-0x6000+0x23D,writer_bank=5,
                target_slot=17,target_offset=0x612E-0x6000+0x23D,target_bank=5,target_region='Action',
                target_path='Source/Action/CreateClass17LinkedRecord.asm',target_source_classified=True,writer_source_classified=True)

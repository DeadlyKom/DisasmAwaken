"""State08, три независимых шага слова, выбранная запись и полный завершающий эффект."""
FUNCTIONS={0xF57F:('ApproachTargetRecordAndResolve','Сближение с выбранной записью, обновление связи и завершение через большой эффект')}
LOCAL={0xF5AD:'EffectCurrent',0xF5B4:'Approach',0xF61B:'Reached',0xF62C:'MarkArrival',0xF655:'CountArrival',0xF65E:'EffectTarget'}
STATE_MODULE='ActionArrivalState'
STATE_FIELDS=(('ArrivalCount',0x9BCE,'существующее слово, увеличивается при ближней цели класса 0, 5, 6 или 7 и ненулевом Unknown11'),)
MODIFIED_WRITERS=((0xF611,0xE5B0,0xE5AF,2),(0xF614,0xE5CF,0xE5CE,2),(0xF617,0xE5EA,0xE5E9,2))
CONTRACTS={('Action',0xF57F):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает текущую FActionRecord',
     'TargetIndex задаёт обычный полный индекс цели, доступны поля целевой записи и три текущих Components',
     'действуют договоры SelectRecordByIndex, RecordIXToIndex, ApproachWordAndAccumulate, QueueTextItemBank1 и большого эффекта',
     'OBJECT3D банка 4, эффект банка 3, Controls банка 1 и исходные списки игровых и эффектных записей доступны',
     'ROM выбрана по фактическому paging, код в общей RAM и ACTION доступны, до 18 дополнительных байтов CPU-стека доступны, IRQ исключены'],
    ['до проверки активности цели у неё устанавливается бит 1 LinkFlags, Unknown15 получает текущий Unknown0D, LinkedIndex индекс текущего IX',
     'при Component0.High цели=80 ненулевой Unknown11 пытается поставить текст F248 в очередь Controls, затем большой эффект выполняется на текущем IX',
     'при доступной цели три Components приближаются настоящим ApproachWordAndAccumulate с общим OR-накопителем в C\'',
     'первая и вторая рассчитанные Components записываются сразу, третья только при ненулевом накопителе остаточных старших байтов',
     'на дальнем пути все три результата сохранены, фазы увеличены на 1, 2 и 3, Base0/1/2 UpdateRecordComponents обнулены, затем внешний RET',
     'на ближнем пути третья рассчитанная компонента не сохраняется, при StateCode цели, отличном от FF, текущая запись помечается для повторного использования',
     'затем у цели устанавливается бит 2 LinkFlags, ненулевой Unknown11 вызывает очередь текста F293',
     'только при таком уведомлении и полном классе цели 0, 5, 6 или 7 ArrivalCount увеличивается на один по модулю 65536',
     'ближний путь вызывает большой эффект на выбранной цели с сохранением исходного IX, потерянный путь на текущей записи',
     "на дальнем пути HL=0, DE адрес цели, BC её третья компонента, A=C' общий накопитель, F от последнего INC OffsetPhase2, остальные альтернативные пары и AF' сохраняются",
     "после эффекта HL, DE, BC, AF, HL', DE', BC', AF', IY и R определяются полным эффектом и игровыми детьми, IX, I/IM/IFF сохраняются",
     'все пути выполняют внешний RET, SP=входной SP+2, дальний путь paging не меняет, очередь и эффект заканчиваются полной страницей 10'],
    ["HL, DE, BC, AF, C', IY, R, поля связи цели, компоненты и фазы текущей записи, операнды, CPU-стек, условно остальные альтернативные пары, очередь, эффектные и игровые записи, ArrivalCount и 7FFD"],
    ['ближняя область задаётся нулём OR свёрнутых старших байтов остатка, это не точное совпадение трёх координат',
     'проверка StateCode цели выполняется через обычный индекс повторно, StateCode=FF пропускает только освобождение текущей записи',
     'бит 2 LinkFlags цели устанавливается и при StateCode=FF, очередь может молча отклонить сообщение, счётчик от успешности приёма не зависит',
     '70256 сценариев включили все полные классы эффекта, все разности первого слова, 26 физических целей, самовыбор, уведомления и полные эффектные списки',
     'сверены точные регистры, флаги, R, восемь банков, кратность записей и настоящие OUT, пути эффекта включают игровые дочерние записи классов ниже 16',
     'ROM в модели синтетическая, значения 0000 и 0100 различаются, реальные игровые сообщения не отрисовывались потребителем очереди',
     'индексы вне физических записей, полное произведение входов, аппаратные IRQ, точные T, сборка и нативная игра не проверялись'])}
COMMENTS={
    0xF57F:(['Поиск обычной целевой записи по TargetIndex, специальной обработки FF здесь нет.'],None),
    0xF585:(['Обновление бита обратной связи, Unknown15 и LinkedIndex цели до проверки её активности.'],None),
    0xF595:(['Проверка полного старшего байта первой компоненты цели, C уже содержит младший байт.'],None),
    0xF59D:([],'переход, если Component0.High цели не равен 80, начать три шага сближения'),
    0xF59F:(['Проверка ненулевого Unknown11 для уведомления о потерянной цели.'],None),
    0xF5A3:([],'переход, если Unknown11 равен нулю, пропустить очередь потерянной цели'),
    0xF5A5:(['Создание запроса текста F248 в очереди банка 1 с сохранением DE, приём не гарантирован.'],None),
    0xF5AD:(['Выбор текущего IX для большого эффекта при недоступной цели.'],None),
    0xF5B4:(['Подготовка первой базовой компоненты и очистка только альтернативного накопителя C\'.'],None),
    0xF5B9:(['Расчёт первой текущей компоненты и немедленная запись результата независимо от итоговой близости.'],None),
    0xF5C8:(['Расчёт второй компоненты относительно цели и немедленная запись результата.'],None),
    0xF5DD:(['Расчёт третьей компоненты с общим накопителем остатка, запись пока отложена.'],None),
    0xF5EC:(['Проверка общего C\' после трёх шагов, DE сохраняет адрес выбранной записи.'],None),
    0xF5F4:([],'переход, если общий накопитель равен нулю, обработать ближнюю область без записи третьего результата'),
    0xF5F6:(['Обновление третьей компоненты только на дальнем пути.'],None),
    0xF5FC:(['Обновление циклических фаз шагами 1, 2 и 3, байтовое оборачивание сохраняется.'],None),
    0xF60E:(['Обновление трёх существующих базовых операндов нулевым словом перед внешним возвратом.'],None),
    0xF61B:(['Повторный поиск адреса StateCode цели по полному TargetIndex текущей записи.'],None),
    0xF627:([],'переход, если StateCode цели равен FF, не освобождать текущую запись'),
    0xF629:(['Обновление текущей записи до кода доступности 8000 с однократным FF-пропуском повторного поиска.'],None),
    0xF62C:(['Обновление бита 2 LinkFlags цели после достижения ближней области.'],None),
    0xF630:(['Проверка Unknown11 перед уведомлением и отдельным учётом выбранных полных классов.'],None),
    0xF634:([],'переход, если Unknown11 равен нулю, пропустить уведомление и счётчик'),
    0xF636:(['Создание запроса текста F293 в очереди Controls банка 1 без признака успешности в регистрах.'],None),
    0xF63E:(['Проверка полного класса цели для увеличения ArrivalCount независимо от принятия текста.'],None),
    0xF643:([],'переход, если полный ClassCode цели равен 0, увеличить счётчик ближних целей'),
    0xF648:([],'переход, если полный ClassCode цели равен 5, увеличить счётчик ближних целей'),
    0xF64D:([],'переход, если полный ClassCode цели равен 6, увеличить счётчик ближних целей'),
    0xF652:([],'переход, если полный ClassCode цели не равен 7, пропустить увеличение счётчика'),
    0xF655:(['Обновление слова ArrivalCount на один по модулю 65536 с сохранением рабочего HL.'],None),
    0xF65E:(['Выбор IX из сохранённого DE для полного большого эффекта и восстановление исходного IX после возврата.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionArrivalConst','''
                ; Исходные индексы битов и сообщения State08
                module ActionArrivalConst
LinkedBit       equ #01                                                         ; бит 1 LinkFlags, обратная связь установлена до проверки активности
ReachedBit      equ #02                                                         ; бит 2 LinkFlags, пройдена ближняя область
MissingText     equ #F248                                                       ; адрес текста Controls банка 1, не адрес кода ACTION
ReachedText     equ #F293                                                       ; адрес текста Controls банка 1
StateOffset     equ #0A                                                         ; смещение StateCode внутри обычной записи, младший байт базы кратен 40
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF57F):return operation
    names={7:'OffsetPhase0',8:'OffsetPhase1',9:'OffsetPhase2',11:'LinkedIndex',12:'LinkFlags',13:'Unknown0D',15:'TargetIndex',17:'Unknown11',18:'ClassCode',21:'Unknown15'}
    for prefix in ('IX','IY'):
        for offset in (*range(6),*names):
            name='Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low') if offset<6 else names[offset]
            operation=operation.replace('('+prefix+'+#'+format(offset,'02X')+')','('+prefix+' + @FActionRecord.'+name+')')
    for address,name in ((0xE69E,'SelectRecordByIndex'),(0xE6B5,'RecordIXToIndex'),(0xE6A7,'RecordIndexToAddress'),
                         (0x6311,'ApproachWordAndAccumulate'),(0x6040,'QueueTextItemBank1'),(0xF394,'MarkRecordForReuse'),(0xEA29,'PrepareLargeEffect')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    for index,address in enumerate((0xE5B0,0xE5CF,0xE5EA)):
        operation=operation.replace('(#'+format(address,'04X')+')','(@ActionRecordUpdateState.Base'+str(index)+')')
    return (operation.replace('(#9BCE)','(@ActionArrivalState.ArrivalCount)')
            .replace('LD DE, #F248','LD DE, @ActionArrivalConst.MissingText')
            .replace('LD DE, #F293','LD DE, @ActionArrivalConst.ReachedText')
            .replace('SET 1,','SET @ActionArrivalConst.LinkedBit,').replace('SET 2,','SET @ActionArrivalConst.ReachedBit,')
            .replace('OR #0A','OR @ActionArrivalConst.StateOffset').replace('CP #80','CP @ActionReuseConst.ReusableHigh'))


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer'] in (0xF611,0xF614,0xF617):
            item.update(writer_slot=17,writer_offset=item['writer']-0x6000,writer_bank=0,
                target_slot=17,target_offset=item['target']-0x6000,target_bank=0,target_region='Action',
                target_path='Source/Action/UpdateRecordComponents.asm',target_source_classified=True,writer_source_classified=True)

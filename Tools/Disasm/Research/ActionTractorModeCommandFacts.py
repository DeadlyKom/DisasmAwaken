"""Команда силового луча, снятие захватов и переход во внутренний вход наведения."""
TAG='ActionTractorModeCommand'
TITLE='команда силового луча'
CASES=3648
FUNCTIONS={0x7439:('ToggleTractorMode','Переключение режима силового луча и запроса наведения со снятием захватов')}
ENDS={0x7439:0x7480}
KEYS={0x7439:0x13}
LOCAL={0x746D:'QueueDisabled',0x7475:'QueueBeamName'}
MUTATIONS=((0x7440,0xA85F,1,0xA85E,'Source/Action/UpdateFrame.asm'),
    (0x744B,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'),
    (0x7453,0x7318,1,0x7317,None))
CONTRACTS={('Action',0x7439):(
    ['HL, DE и BC задают сохраняемый контекст, AF входного аргумента не задаёт',
     'CommandDelay допускает обработку только при нуле, TractorBeam.Value=FF означает отсутствие оборудования',
     'банк 0 выбран, очередь Controls банка 1 удовлетворяет QueueTextItemBank1, paging разблокирован',
     'CPU-стек допускает восемнадцать дополнительных байтов, IRQ не вмешиваются'],
    ['при ненулевой задержке HL, DE и BC сохраняются, A содержит задержку, F соответствует AND A, записи и OUT отсутствуют',
     'при нулевой задержке CommandDelay получает 10 до проверки оборудования',
     'при TractorBeam.Value=FF HL, DE и BC сохраняются, A=0, F=50, остальные поля и paging не меняются',
     'при допуске Mode по 7318 и Request по AA8E независимо получают прежний байт XOR 1, Target0..Target2 получают FF',
     'CursorA получает EDA8, HL=EDA8, DE и BC сохраняются, A и F соответствуют XOR нового Request',
     'порядок четырёх запросов очереди, состояние Mode, F2D9, состояние Request, F214',
     'ненулевой результат каждого переключения выбирает F1E1, нулевой F1F0, приём четырёх запросов независим',
     "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP после RET равен исходному SP+2",
     'восемь OUT 7FFD образуют четыре пары 11,10, итоговая страница 10, прежняя конфигурация не восстанавливается'],
    ['HL, AF, R, CommandDelay, Mode, Request, захваты, CursorA, очередь, paging и восемнадцать временных байтов стека'],
    ['внутренний переход на ToggleTargetRequest.ToggleRequest пропускает его проверку задержки и установку задержки 7',
     'после принятой команды остаётся задержка 10, четыре сообщения могут быть приняты частично',
     'оба переключения сохраняют биты 7..1, произвольный ненулевой байт не превращается обязательно в ноль',
     '3648 сценариев исполняют настоящий общий хвост и очередь, R, такты и остаточные слова временного стека не сверяются'])}
COMMENTS={
 0x7439:(['Проверка задержки перед изменением режима силового луча.'],None),
 0x743D:([],'выход, если CommandDelay ненулевой, оба режима и захваты сохранить'),
 0x743E:(['Обновление задержки до проверки установленного оборудования.'],None),
 0x7443:(['Проверка полного кода TractorBeam.Value, только FF означает отсутствие оборудования.'],None),
 0x7447:([],'выход, если TractorBeam.Value равен FF, сохранить режимы при уже установленной задержке'),
 0x7448:(['Выбор исходного звукового потока принятой команды в банке 0.'],None),
 0x744E:(['Обновление бита 0 существующего операнда Mode, старшие биты сохраняются.'],None),
 0x7456:(['Снятие всех трёх захватов до постановки сообщений.'],None),
 0x7461:([],'переход, если новый Mode равен нулю, поставить сообщение о выключении'),
 0x7463:(['Передача сообщения о включении силового луча с сохранением DE.'],None),
 0x746D:(['Передача сообщения о выключении силового луча с сохранением DE.'],None),
 0x7475:(['Передача названия режима отдельным запросом очереди.'],None),
 0x747D:(['Продолжение во внутреннем входе переключения Request, повторная проверка задержки не выполняется.'],None)}


def name_operands(region,function_address,operation):
    if region!='Action' or function_address!=0x7439:return operation
    replacements={'(#A85F)':'(@ActionMissileLaunchState.CommandDelay)',
        '(#9C24)':'(@ActionShipEquipment.TractorBeam.Value)',
        '(#7318)':'(@ActionTractorModeState.Mode)',
        '(#ECA9)':'(@ActionAyEffectState.CursorA)',
        'LD HL, #EDA8':'LD HL, @ActionMissileCreateConst.ActionSound',
        'CALL #6040':'CALL @Action.QueueTextItemBank1.Entry',
        'JP #72F2':'JP @Action.ToggleTargetRequest.ToggleRequest'}
    for i in range(3):replacements['(#'+format(0x9B1B+i,'04X')+')']='(@ActionMissileTargets.Value.Target'+str(i)+')'
    for address,name in LOCAL.items():replacements['#'+format(address,'04X')]='@Action.ToggleTractorMode.'+name
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    path=root/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    addition='                ; Существующий операнд по 7318, новая память не выделяется\n                module ActionTractorModeState\n'
    addition+='Mode            equ #7318'.ljust(80)+'; ноль выбирает RequestPairedAimLines, ненулевой байт притягивание и сбор Target0\n'
    addition+='                endmodule\n\n'
    pending[path]=text.replace('                endif',addition+'                endif').encode('utf-8')

"""Два подтверждённых входа таблицы клавиш, захваты и байтовый запрос наведения."""
FUNCTIONS={0x72BE:('ClearMissileTargets','Снятие трёх захватов ракет с задержкой повторной команды и сообщением'),
    0x72E2:('ToggleTargetRequest','Переключение младшего бита запроса наведения с двумя сообщениями')}
ENDS={0x72BE:0x72E2,0x72E2:0x7317}
LOCAL={0x72F2:'ToggleRequest',0x7306:'QueueEnabled',0x730E:'QueueModeName'}
COMMON_IN=['HL, DE и BC задают сохраняемый контекст, AF входного аргумента не задаёт',
    'CommandDelay по A85F допускает команду только при нуле, банк 0 выбран',
    'очередь Controls банка 1 соответствует QueueTextItemBank1, paging не заблокирован',
    'на стеке внешний возврат и восемнадцать доступных байтов ниже SP, IRQ не вмешиваются']
COMMON_OUT=['при ненулевой задержке HL, DE и BC сохраняются, A равен задержке, F соответствует AND A, память и paging не меняются',
    'при допуске HL=EDA8, DE и BC сохраняются, CommandDelay=7, CursorA получает поток ActionSound',
    "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP после RET равен входному SP+2",
    'каждый запрос очереди выполняет OUT 7FFD со значениями 11 и 10, итоговая страница 10',
    'отказ заполненной очереди молчаливый, состояние команды всё равно изменяется']
CONTRACTS={
 ('Action',0x72BE):(COMMON_IN,COMMON_OUT+['при допуске Target0, Target1 и Target2 получают FF, передан указатель F354, A=FF и F=54'],
    ['HL, AF, R, CommandDelay, захваты, CursorA, очередь, paging и восемнадцать временных байтов стека'],
    ['сообщение F354 содержит текст о снятии наведённых целей, его фактический вывод требует потребителя очереди',
     '1568 композиционных сценариев проверяют обе команды, остаточные слова стека и R не сверялись']),
 ('Action',0x72E2):(COMMON_IN,COMMON_OUT+['при допуске Request получает прежний байт XOR 1, остальные семь битов сохраняются',
    'A равен новому Request, F соответствует XOR, ненулевой результат выбирает F1E1, нулевой F1F0',
    'после сообщения состояния независимо ставится F214, название режима наведения на цель'],
    ['HL, AF, R, CommandDelay, Request, CursorA, очередь, paging и восемнадцать временных байтов стека'],
    ['Request является проверяемым на ноль байтом, XOR 1 не нормализует произвольный исходный ненулевой байт',
     'внутренний вход QueueEnabled не проверяет задержку и не меняет Request, QueueModeName только ставит вторую строку',
     'переход из клавиатурного обработчика 7439 на 72F2 является отдельным внутренним входом переключения, родительский договор целиком ему не приписывается'])}
COMMENTS={
 0x72BE:(['Проверка задержки перед снятием существующих захватов.'],None),
 0x72C2:([],'выход, если CommandDelay ненулевой, захваты сохранить'),
 0x72C3:(['Обновление задержки принятой команды, повторный запрос допускается после её отсчёта.'],None),
 0x72C8:(['Выбор исходного потока AY-канала A в банке 0.'],None),
 0x72CE:(['Снятие всех трёх захватов независимо от приёма сообщения очередью.'],None),
 0x72D9:(['Сохранение DE вызывающего вокруг передачи указателя сообщения.'],None),
 0x72DA:(['Выбор сообщения о снятии наведённых целей.'],None),
 0x72E2:(['Проверка задержки перед изменением запроса наведения.'],None),
 0x72E6:([],'выход, если CommandDelay ненулевой, Request сохранить'),
 0x72E7:(['Выбор исходного звукового потока принятой команды.'],None),
 0x72ED:(['Обновление задержки принятой команды.'],None),
 0x72F2:(['Обновление только бита 0 Request, остальные разряды не нормализуются.'],None),
 0x72FA:([],'переход, если новый Request ненулевой, поставить сообщение о включении'),
 0x72FC:(['Передача сообщения о выключении с сохранением DE вызывающего.'],None),
 0x7306:(['Передача сообщения о включении с сохранением DE вызывающего.'],None),
 0x730E:(['Передача названия режима отдельным запросом, отказ первой строки не проверяется.'],None)}


def name_operands(region,function_address,operation):
    if region!='Action' or function_address not in FUNCTIONS:return operation
    replacements={'(#A85F)':'(@ActionMissileLaunchState.CommandDelay)',
        '(#AA8E)':'(@ActionAimFollowState.Request)','(#ECA9)':'(@ActionAyEffectState.CursorA)',
        'LD HL, #EDA8':'LD HL, @ActionMissileCreateConst.ActionSound',
        'CALL #6040':'CALL @Action.QueueTextItemBank1.Entry'}
    for i in range(3):replacements['(#'+format(0x9B1B+i,'04X')+')']='(@ActionMissileTargets.Value.Target'+str(i)+')'
    for address,name in LOCAL.items():replacements['#'+format(address,'04X')]='@Action.ToggleTargetRequest.'+name
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation

TAG='ActionTargetCommands'
TITLE='команды захватов и наведения'
CASES=1568
KEYS={0x72BE:0x0B,0x72E2:0x0A}
MUTATIONS=((0x72C5,0xA85F,1,0xA85E,'Source/Action/UpdateFrame.asm'),
    (0x72CB,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'),
    (0x72EA,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'),
    (0x72EF,0xA85F,1,0xA85E,'Source/Action/UpdateFrame.asm'),
    (0x72F7,0xAA8E,1,0xAA8D,'Source/Action/UpdateFrame.asm'))

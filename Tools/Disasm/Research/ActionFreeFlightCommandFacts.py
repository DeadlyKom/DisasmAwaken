"""Свободный полёт, проверка ограничителя и переключение настоящего опкода координатного обновления."""
TAG='ActionFreeFlightCommand'
TITLE='команда свободного полёта'
CASES=66576
FUNCTIONS={0x754C:('ToggleFreeFlightMode','Условная смена опкода координатного обновления с сообщением о свободном полёте')}
ENDS={0x754C:0x7594}
KEYS={0x754C:0x10}
LOCAL={0x757E:'QueueEnabled',0x7588:'StoreOpcode'}
MUTATIONS=((0x7553,0xA85F,1,0xA85E,'Source/Action/UpdateFrame.asm'),
    (0x7568,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'),
    (0x7588,0x6E72,1,0x6E72,'Source/Action/UpdateMotionFromControls.asm'))
CONTRACTS={('Action',0x754C):(
    ['HL, DE и BC задают сохраняемый контекст, AF входного аргумента не задаёт',
     'CommandDelay допускает обработку только при нуле, FreeFlight.Value=FF означает отсутствие оборудования',
     'LimitWord является изменяемым словом ограничителя IncreaseGaugeWord по 7693, это не само SignedWord',
     'банк 0 выбран, очередь Controls банка 1 удовлетворяет QueueTextItemBank1, paging разблокирован',
     'CPU-стек допускает восемнадцать дополнительных байтов, IRQ не вмешиваются'],
    ['при ненулевой задержке HL, DE и BC сохраняются, A равен задержке, F соответствует AND A, записи и OUT отсутствуют',
     'при нулевой задержке CommandDelay получает 20 до остальных проверок',
     'при FreeFlight.Value=FF HL, DE и BC сохраняются, A=0, F=50, остальные состояния и paging не меняются',
     'при LimitWord не 0088 HL=(LimitWord-0088) AND FFFF, DE сохранён, BC=0088, A=(FreeFlight.Value+1) AND FF, F соответствует SBC с нулевым входным Carry',
     'при полном допуске CursorA получает EDA8, HL=EDA8, DE сохранён, BC=0088',
     'MotionOpcode=3A заменяется на C9, любой другой исходный опкод заменяется на 3A, A содержит записанный опкод',
     'итоговый F соответствует CP исходного MotionOpcode,3A, он сохраняется обоими вызовами очереди',
     'для исходного 3A переданы F1E1 и F200, иначе F1F0 и F200, приём двух записей независим',
     "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP после RET равен входному SP+2",
     'при полном допуске OUT 7FFD получает 11,10,11,10, итоговая страница 10, прежняя конфигурация не восстанавливается'],
    ['HL, BC, AF, R, CommandDelay, CursorA, MotionOpcode, очередь, paging и восемнадцать временных байтов стека на соответствующих путях'],
    ['RET по 6E72 пропускает часть UpdateMotionFromControls после двух уже выполненных предшествующих вызовов, а не отключает всё обновление кадра',
     'проверены все 65536 ограничителей и все 256 исходных опкодов, произвольный опкод читается как данные и этой моделью не исполняется',
     '66576 сценариев исполняют настоящие очередь и банковую обёртку, R, такты и остаточные слова временного стека не сверяются'])}
COMMENTS={
 0x754C:(['Проверка задержки перед изменением режима свободного полёта.'],None),
 0x7550:([],'выход, если CommandDelay ненулевой, опкод координатного обновления сохранить'),
 0x7551:(['Обновление задержки до проверок оборудования и ограничителя.'],None),
 0x7556:(['Проверка полного кода FreeFlight.Value, только FF означает отсутствие оборудования.'],None),
 0x755A:([],'выход, если FreeFlight.Value равен FF, прочее состояние сохранить при уже установленной задержке'),
 0x755B:(['Проверка текущего изменяемого LimitWord, разрешено только исходное значение сброса 0088.'],None),
 0x7564:([],'выход, если LimitWord отличается от 0088, сохранить опкод и звуковой поток'),
 0x7565:(['Выбор исходного звукового потока принятой команды.'],None),
 0x756B:(['Проверка фактического опкода начала координатной цепочки.'],None),
 0x7570:([],'переход, если MotionOpcode равен 3A, поставить сообщение о включении свободного полёта'),
 0x7572:(['Передача сообщения о выключении свободного полёта с сохранением DE.'],None),
 0x757A:(['Восстановление исходного LD A,(nn), его двухбайтовый операнд сохраняется.'],None),
 0x757E:(['Передача сообщения о включении свободного полёта с сохранением DE.'],None),
 0x7586:(['Выбор RET вместо первого чтения координатной цепочки, последующие байты не меняются.'],None),
 0x7588:(['Обновление одного существующего опкода UpdateMotionFromControls.'],None),
 0x758B:(['Передача названия режима отдельным запросом, отказ первой записи не проверяется.'],None)}


def name_operands(region,function_address,operation):
    if region!='Action' or function_address!=0x754C:return operation
    replacements={'(#A85F)':'(@ActionMissileLaunchState.CommandDelay)',
        '(#9C28)':'(@ActionShipEquipment.FreeFlight.Value)',
        '(#7693)':'(@ActionControlDecayState.LimitWord)',
        '(#6E72)':'(@ActionGaugeWordKeysState.MotionOpcode)',
        '(#ECA9)':'(@ActionAyEffectState.CursorA)',
        'LD A, #14':'LD A, @ActionFreeFlightConst.Delay',
        'LD A, #C9':'LD A, @ActionFreeFlightConst.ReturnOpcode',
        'CP #3A':'CP @ActionGaugeKeyConst.MotionOpcode',
        'LD A, #3A':'LD A, @ActionGaugeKeyConst.MotionOpcode',
        'LD BC, #0088':'LD BC, @ActionControlDecayConst.ResetWord',
        'LD HL, #EDA8':'LD HL, @ActionMissileCreateConst.ActionSound',
        'CALL #6040':'CALL @Action.QueueTextItemBank1.Entry'}
    for address,name in LOCAL.items():replacements['#'+format(address,'04X')]='@Action.ToggleFreeFlightMode.'+name
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    path=root/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    addition='                ; Исходные параметры команды свободного полёта\n                module ActionFreeFlightConst\n'
    addition+='Delay           equ #14'.ljust(80)+'; задержка повторной команды, двадцать шагов обработчика\n'
    addition+='ReturnOpcode    equ #C9'.ljust(80)+'; RET вместо первого чтения координатной цепочки\n'
    addition+='                endmodule\n\n'
    pending[path]=text.replace('                endif',addition+'                endif').encode('utf-8')

"""Команда возврата к станции и настоящий банковый переход до подготовленного входа 4200."""
TAG='ActionStationReturnCommand'
TITLE='команда возврата к станции'
CASES=1792
FUNCTIONS={0x7606:('RequestStationReturn','Однократная команда возврата к станции с переходом в банковый подготовитель загрузки')}
ENDS={0x7606:0x762A}
KEYS={0x7606:0x12}
LOCAL={}
MUTATIONS=((0x760E,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'),
    (0x7613,0xA85F,1,0xA85E,'Source/Action/UpdateFrame.asm'))
CONTRACTS={('Action',0x7606):(
    ['HL, DE и BC задают сохраняемый на отказе контекст, AF входного аргумента не задаёт',
     'CommandDelay допускает обработку только при нуле, ReturnSystem.Value=FF означает отсутствие оборудования',
     'банк 0 выбран для CursorA, paging разблокирован, Controls банка 1 содержит PrepareStationReload и его CodeSource',
     'общая область состояния HighPairs и области сохранения удовлетворяют PrepareStationReload, IRQ не вмешиваются до DI',
     'на пути отказа на CPU-стеке читаемое слово возврата, на принятом пути старый стек намеренно отбрасывается'],
    ['при ненулевой задержке HL, DE и BC сохраняются, A содержит задержку, F соответствует AND A, записи и OUT отсутствуют',
     'при нулевой задержке CursorA получает EE1B, CommandDelay получает 20 до проверки оборудования',
     'при ReturnSystem.Value=FF HL=EE1B, DE и BC сохраняются, A=0, F=50, paging сохраняется, обычный RET задаёт SP=входной SP+2',
     'при допуске ReturnSystem.Value получает FF до сохранения состояния, OUT 7FFD получает 19, выбран банк 1 и теневой экран',
     'следует JP PrepareStationReload, обычного возврата к клавиатурному диспетчеру нет',
     'на границе PC=4200 получены HL=DE23, DE=4300, BC=0, A=3F, IX и альтернативные регистры сохранены',
     '768 атрибутов базового экрана обнулены, два байта LowPairs переставлены, 512 байтов состояния сохранены в 4000..41FF с уже записанным ReturnSystem.Value=FF',
     '256 байтов следующей стадии перенесены в 4200..42FF, IY=5C3A, SP=5FFF, I=3F, IM=1, IFF сброшен, итоговая страница 19',
     'F и R соответствуют точным формулам PrepareStationReload с входным F от INC кода оборудования, по 5FFD/5FFE остаётся слово 4200'],
    ['HL, DE, BC, AF, IY, SP, I, IM, IFF, R, CommandDelay, CursorA, ReturnSystem.Value, счётчик, атрибуты, блоки сохранения и новый стек на соответствующих путях'],
    ['название оборудования взято из совпавшего авторского описания, его FF расходуется перед переходом и попадает в сохранённый блок',
     'сканер клавиатуры имеет старую рамку, но успешный путь её не восстанавливает, PrepareStationReload заменяет SP',
     '1792 сценария исполняют настоящий банковый переход и три LDIR, сверены точные регистры включая R, все банки RAM и кратность записей',
     'проверка останавливается перед первой инструкцией перенесённого кода 4200, TR-DOS и загрузка STATIONF этой моделью не исполняются'])}
COMMENTS={
 0x7606:(['Проверка задержки перед однократным запросом возврата к станции.'],None),
 0x760A:([],'выход, если CommandDelay ненулевой, состояние сохранить'),
 0x760B:(['Выбор исходного звукового потока до проверки наличия оборудования.'],None),
 0x7611:(['Обновление задержки независимо от последующего отказа по оборудованию.'],None),
 0x7616:(['Проверка полного кода ReturnSystem.Value, только FF запрещает переход.'],None),
 0x761A:([],'выход, если ReturnSystem.Value равен FF, уже выбранные поток и задержку сохранить'),
 0x761B:(['Списание системы возврата до сохранения состояния следующим банковым обработчиком.'],None),
 0x7620:(['Выбор банка 1 с теневым экраном для настоящего подготовителя загрузки станции.'],None),
 0x7627:(['Передача в Controls без рамки CALL, подготовитель заменит CPU-стек и перейдёт в свою копию 4200.'],None)}


def name_operands(region,function_address,operation):
    if region!='Action' or function_address!=0x7606:return operation
    for before,after in {'(#A85F)':'(@ActionMissileLaunchState.CommandDelay)',
        '(#9C27)':'(@ActionShipEquipment.ReturnSystem.Value)',
        '(#ECA9)':'(@ActionAyEffectState.CursorA)',
        'LD HL, #EE1B':'LD HL, @ActionStationReturnConst.Sound',
        'LD A, #14':'LD A, @ActionStationReturnConst.Delay',
        'LD A, #FF':'LD A, @ActionStationReturnConst.SpentEquipment',
        'LD A, #19':'LD A, @ActionStationReturnConst.Page',
        'LD BC, #7FFD':'LD BC, @Hardware.PagingPort',
        'JP #DCE3':'JP @Controls.PrepareStationReload.Entry'}.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    path=root/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    addition='                ; Исходные параметры команды возврата к станции\n                module ActionStationReturnConst\n'
    for name,value,description in (('Sound','#EE1B','исходный поток AY-канала A перед проверкой оборудования'),
        ('Delay','#14','задержка повторной команды, двадцать шагов обработчика'),
        ('SpentEquipment','#FF','полный код списанной системы возврата'),
        ('Page','#19','банк 1, теневой экран, ROM 1, paging не блокируется')):
        addition+=(name.ljust(16)+'equ '+value).ljust(80)+'; '+description+'\n'
    addition+='                endmodule\n\n'
    pending[path]=text.replace('                endif',addition+'                endif').encode('utf-8')

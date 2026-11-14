"""Полный локальный инициализатор 60AE, раздельные банки звука и текста, без списания запаса."""
FUNCTIONS={0x60AE:('CreateMissileForTarget','Проверка существования записи цели, поиск свободного слота, инициализация ракеты и создание обратной связи у цели')}
LOCAL={0x60B8:'LostTarget',0x60C8:'BuildComponents',0x60E6:'FindSlot'}
CONTRACTS={('Action',0x60AE):(
 ['HL и DE числовых аргументов не задают, C код существующей записи цели, B аргумента не задаёт, AF не задаёт условия допуска', 'для создания C относится к допустимой записи исходного массива, процедура сама диапазон C не проверяет', 'действуют договоры RecordIndexToAddress, TransformVectorTransposed, SelectMissileStock, FindReusableRecord и RecordIYToIndex', 'входная конфигурация выбирает банк 0 и не блокирует 7FFD, канал A и Controls банка 1 доступны, CPU-стек допускает восемнадцать дополнительных байтов, IRQ не вмешиваются'],
 ['HL при потерянной цели равен EDA8, при отказе по слоту указывает выбранный счётчик ракет, при успехе равен 0040', 'DE при потерянной цели сохраняется, при отказе по слоту равен 0040, при успехе указывает LinkedIndex цели', 'BC при потерянной цели сохраняется, после подготовки B=1A и C равен входному коду цели', 'AF при потерянной цели равен 8090, при отказе по слоту равен 8042, при успехе A=индекс ребёнка и F=45 OR (A AND 28)', "HL', DE', BC' при потерянной цели сохраняются, после расчёта содержат три компоненты вектора", "AF' при потерянной цели сохраняется, при отказе по слоту A'=01 и F' от вычислителя, при успехе AF'=0044", 'IX сохраняется, IY при потерянной цели сохраняется, при отказе по слоту указывает маркер, при успехе ребёнка', 'I, IM и IFF сохраняются, SP=входной SP+2, Carry=1 только при создании, Z установлен и при успехе, и при отказе по слоту', 'при потерянной цели OUT 7FFD получает 11 и 10, на других путях переключений банков нет', 'потерянная цель задаёт CursorA=EDA8 в банке 0 и передаёт текст F248 очереди банка 1, приём сообщения не гарантирован', 'запас ракет не уменьшается, EffectReserve новой записи получает 0A при выборе Fallback либо 32 при выборе Preferred'],
 ["HL, DE, BC и AF по выбранному пути, HL', DE', BC' и AF' после расчёта, IY после поиска, R, рамка до восемнадцати байтов, состояние геометрии, InitParameter, ReuseByte, поля новой записи, LinkedIndex и LinkFlags цели, CursorA и очередь на пути потерянной цели"],
 ["переданный A'=1 задаёт Unknown11 как авторский LZS ракеты игрока, значение поля у других классов не переопределяется", 'поле Component0.High=80 означает потерянную цель, все другие байты этого поля принимаются без дополнительной проверки', 'вектор расчёта равен 0, 0, 400, выходные компоненты находятся в диапазоне -395..396, знаковое переполнение здесь невозможно', 'неизвестные поля инициализируются исходными константами, их игровой смысл не выдумывается', 'создание не выполняет проверку ненулевого запаса и не списывает его, предварительный допуск и последующее списание относятся к вызывающему коду', 'фактический AY-вывод и движение ракеты не выполняются этой процедурой'])}
COMMENTS={
 0x60AE:(['Поиск адреса цели по входному C, числовой диапазон кода здесь не проверяется.'],None),
 0x60B2:(['Проверка старшего байта первой компоненты, полный код 80 означает отсутствующую запись.'],None),
 0x60B6:([],'переход, если Component0.High цели не равен 80, подготовить новую запись'),
 0x60B8:(['-----------------------------------------','Обработка потерянной цели','Подготовка потока AY-канала A в банке 0, фактический вывод выполнит потребитель ECA8 позднее.'],None),
 0x60BE:(['Сохранение DE перед передачей сообщения о потерянной цели очереди Controls банка 1.'],None),
 0x60C6:(['Формирование Carry=0 отказа независимо от приёма сообщения, AF становится 8090.'],None),
 0x60C8:(['-----------------------------------------','Расчёт трёх компонентов новой записи','Сохранение входных BC и замена альтернативных компонентов исходным вектором 0, 0, 400.'],None),
 0x60D2:(['Расчёт по временно транспонированной матрице с настоящим восстановлением SP.'],None),
 0x60D5:(['Перенос рассчитанных компонентов в альтернативный набор и восстановление входного кода цели в C.'],None),
 0x60D7:(['Сохранение признака ракеты игрока 01 для Unknown11 в альтернативном A, авторский LZS.'],None),
 0x60DA:(['Выбор поля запаса только для параметра новой записи, уменьшения запаса здесь нет.'],None),
 0x60DD:(['Проверка адреса выбранного поля, младший байт 12 соответствует Fallback.'],None),
 0x60E2:([],'переход, если выбран Fallback, оставить параметр EffectReserve равным 0A'),
 0x60E4:(['Выбор начального EffectReserve #32 для поля Preferred.'],None),
 0x60E6:(['-----------------------------------------','Поиск свободного слота','Индекс игрока 1A задаёт стрелявшего в Phase0OrLink ракеты, A100+64*1A указывает авторский PLAYER.'],None),
 0x60E8:(['Обновление операнда инициализации EffectReserve перед поиском, запись сохраняется и при отказе по слотам.'],None),
 0x60EB:(['Сохранение кода цели и значения Phase0OrLink перед итератором.'],None),
 0x60F0:([],'выход, если достигнут маркер без доступного слота, Carry=0, запас и цель не изменены'),
 0x60F1:(['-----------------------------------------','Создание новой записи','Копирование трёх рассчитанных компонентов, альтернативные значения после EXX остаются сохранены.'],None),
 0x6105:(['Инициализация известных по фактическим записям полей, неизвестный игровой смысл сохранён в именах Unknown.'],None),
 0x6123:(['Восстановление значения 01 для Unknown11, в альтернативном AF остаётся 0044.'],None),
 0x612B:(['Инициализация EffectReserve, непосредственный байт заранее изменён выбором поля запаса.'],None),
 0x6133:(['-----------------------------------------','Создание обратной связи у цели','Повторный поиск исходной цели по сохранённому C.'],None),
 0x6138:(['Расчёт адреса LinkFlags, младший байт базы кратен 40, добавление 0C не требует переноса в H.'],None),
 0x613B:(['Установка бита 1 LinkFlags при создании ссылки на новую ракету, остальные разряды сохраняются.'],None),
 0x613D:(['Выбор предыдущего физического поля LinkedIndex у той же цели.'],None),
 0x613F:(['Расчёт кода нового слота из IY с сохранением HL=0040.'],None),
 0x6142:(['Обновление LinkedIndex цели кодом новой записи.'],None),
 0x6143:(['Формирование Carry=1 успешного создания, Z сохраняется от адресного преобразователя.'],None)}


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0x60AE:
        operation=operation.replace('(IY+','(IY + ')
        for address,name in ((0xE6A7,'RecordIndexToAddress'),(0x6040,'QueueTextItemBank1'),(0xACEA,'TransformVectorTransposed'),
                             (0x70ED,'SelectMissileStock'),(0xE9A1,'FindReusableRecord'),(0xE6BE,'RecordIYToIndex')):
            operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
        for address,name in LOCAL.items():operation=operation.replace('#'+format(address,'04X'),'@Action.CreateMissileForTarget.'+name)
        operation=operation.replace('(#ECA9)','(@ActionAyEffectState.CursorA)')
        operation=operation.replace('(#612E)','(@ActionMissileCreateState.InitParameter)')
        operation=operation.replace('LD HL, #EDA8','LD HL, @ActionMissileCreateConst.ActionSound')
        operation=operation.replace('LD DE, #F248','LD DE, @ActionMissileCreateConst.LostText')
        operation=operation.replace('LD BC, #0190','LD BC, @ActionMissileCreateConst.InitialComp2')
        operation=operation.replace('LD A, #0A','LD A, @ActionMissileCreateConst.FallbackParam')
        operation=operation.replace('LD A, #32','LD A, @ActionMissileCreateConst.PreferredParam')
        operation=operation.replace('LD B, #1A','LD B, @ActionMissileCreateConst.PlayerIndex')
        operation=operation.replace('ADD A, #0C','ADD A, FActionRecord.LinkFlags')
        fields={0:'Components.Component0.Low',1:'Components.Component0.High',2:'Components.Component1.Low',
          3:'Components.Component1.High',4:'Components.Component2.Low',5:'Components.Component2.High',
          6:'ModelOffset',7:'OffsetPhase0',8:'OffsetPhase1',9:'OffsetPhase2',10:'StateCode',11:'LinkedIndex',12:'LinkFlags',
          13:'Phase0OrLink',15:'Phase2OrTarget',17:'Unknown11',18:'ClassCode',19:'EffectReserve',37:'TargetCodeStep'}
        for offset,field in fields.items():operation=operation.replace('(IY + #'+format(offset,'02X')+')','(IY + FActionRecord.'+field+')')
        operation=operation.replace('(IY + FActionRecord.ClassCode), #11','(IY + FActionRecord.ClassCode), @ActionMissileCreateConst.MissileClass')
    return operation

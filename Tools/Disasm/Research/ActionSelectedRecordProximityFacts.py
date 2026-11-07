"""State0D, выбранный индекс и полный требуемый класс, резервный выбор и близость."""
FUNCTIONS={0xF04A:('HandleSelectedRecordProximity','Проверка выбранной записи, резервный поиск класса 8 и обработка близости')}
LOCAL={0xF06F:'StepFar'}
CONTRACTS={('Action',0xF04A):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает текущую FActionRecord',
     'Unknown20 задаёт полный байтовый индекс выбранной записи, Unknown21 требуемый полный ClassCode',
     'читаются выбранные Components, ClassCode и ReuseByte, по текущей записи доступны компоненты, фазовые поля и TargetCodeStep',
     'действуют условия SelectRecordByIndex, SelectClass8ForRecord, MaxRecordDeltaHigh и StepCodesTowardRecord',
     'подготовлен ACTION банка 0 и числовые таблицы, 7FFD разблокирован, 18 дополнительных байтов CPU-стека доступны, IRQ не вмешиваются'],
    ['из Unknown20 вычислен IY=A100+64*индекс без ограничения исходными 25 слотами, исходный HL сохранён селектором',
     'при выбранном Component0.High=80 либо несовпадении полного ClassCode с Unknown21 исполнен SelectClass8ForRecord и достигнут F0F8',
     'резервный путь может обновить Unknown20, Unknown21 сохраняется даже после выбора другого класса',
     'при подходящей выбранной записи расстояние A равно максимуму старших байтов трёх модулей обёрнутых разностей',
     'при A<2 в ReuseByte выбранной записи сброшен бит 2, затем текущая запись получает Component0=8000 и ReuseByte=FF с внешним RET',
     'на ближнем пути HL=модуль третьей разности, DE первой, BC сохраняется от входа, A расстояние и F от CP A,2, SP=входной SP+2',
     'при A>=2 исполнен StepCodesTowardRecord с выбранным IY, эффекты соответствуют его договору, PC=F0F8 и SP сохранён',
     'IX, I/IM/IFF сохраняются, без подвода кодов альтернативные регистры и paging сохраняются, при подводе OUT 7FFD получает 11 и 10'],
    ['HL, DE, BC, AF, IY, R, выбранный ReuseByte либо Unknown20 по резервному пути, текущие поля освобождения либо фазового шага, до 18 байтов CPU-стека',
     'HL\', DE\', BC\', AF\', операнды делителя и 7FFD только при подводе кодов, общий хвост F0F8 имеет отдельный договор'],
    ['это исходный адрес State0D, проверяется только полный старший байт доступности 80, младший байт в первой проверке не читается',
     'сравнение класса не является проверкой битовой маски, индекс 00..FF не ограничивается принадлежностью физическому исходному массиву',
     'при IY=IX сначала сбрасывается бит 2, затем тот же ReuseByte получает FF, последнее значение FF сохранено',
     'бит 2 имеет маску 04, его полная игровая роль среди других применений ReuseByte не объявляется установленной',
     '1024 сценария проверили все 256 индексов, четыре профиля, самовыбор, оба резервных результата и обе ветви расстояния',
     'за исходным массивом тест сохраняет оригинальные байты цели, включая находящийся там исполняемый код',
     'сверены все регистры с R, восемь банков RAM, значения и кратность записей и оба OUT, общий F0F8 в этом тесте не исполняется',
     'все возможные данные записей, аппаратные IRQ, точные T, сборка и нативная игра не проверялись'])}
COMMENTS={
    0xF04A:(['Выбор адреса по полному байтовому индексу Unknown20, ограничение числом исходных слотов отсутствует.'],None),
    0xF050:(['Проверка доступности выбранной записи по полному старшему байту первой компоненты.'],None),
    0xF055:([], 'переход, если старший байт выбранной первой компоненты равен 80, выполнить резервный поиск класса 8'),
    0xF058:(['Проверка полного класса выбранной записи относительно требуемого Unknown21.'],None),
    0xF05E:([], 'переход, если полный ClassCode не совпал с Unknown21, выполнить резервный поиск класса 8'),
    0xF061:(['Расчёт максимума старших байтов модулей трёх обёрнутых разностей выбранной и текущей записей.'],None),
    0xF064:(['Проверка близости по общему порогу модулей меньше 512.'],None),
    0xF066:([], 'переход, если максимальный старший байт не меньше двух, подвести фазовые коды к выбранной записи'),
    0xF068:(['Обновление выбранного ReuseByte, сброс только бита 2 с сохранением всех остальных разрядов.'],None),
    0xF06C:(['Освобождение текущей записи с внешним RET, при совпадении указателей её ReuseByte окончательно станет FF.'],None),
    0xF06F:(['Подвод двух фазовых кодов текущей записи через настоящую цепочку геометрии и шага.'],None),
    0xF072:(['Передача общему подготовителю смещений с исходным внешним CPU-стеком.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionSelectedRecordProximityConst','''
                ; Номер точно сбрасываемого разряда, другие значения ReuseByte сохраняются
                module ActionSelectedRecordProximityConst
ClearedReuseBit equ #02                                                         ; бит с маской 04, полный игровой смысл разряда ещё не установлен
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF04A):return operation
    for register,offset,name in (('IX',0x20,'Unknown20'),('IX',0x21,'Unknown21'),
                                 ('IY',1,'Components.Component0.High'),('IY',0x12,'ClassCode'),('IY',0x18,'ReuseByte')):
        operation=operation.replace(f'({register}+#{offset:02X})',f'({register} + @FActionRecord.{name})')
    return (operation.replace('CALL #E69E','CALL @Action.SelectRecordByIndex.Entry')
            .replace('CP #80','CP @ActionReuseConst.ReusableHigh')
            .replace('JP Z, #E97C','JP Z, @Action.SelectClass8ForRecord.Entry')
            .replace('JP NZ, #E97C','JP NZ, @Action.SelectClass8ForRecord.Entry')
            .replace('CALL #EAE9','CALL @Action.MaxRecordDeltaHigh.Entry')
            .replace('CP #02','CP @ActionClass18ProximityConst.NearLimit')
            .replace('RES 2,','RES @ActionSelectedRecordProximityConst.ClearedReuseBit,')
            .replace('JP #F394','JP @Action.MarkRecordForReuse.Entry')
            .replace('CALL #F36B','CALL @Action.StepCodesTowardRecord.Entry')
            .replace('JP #F0F8','JP @Action.PrepareObjectOffsetTransform.Entry'))

"""Полный класс 8 и непосредственное продолжение в создателе с A=2."""
FUNCTIONS={0xE863:('SpawnClass9ForClass8','Допуск полного класса 8 к созданию дочерних записей класса 9 с начальным состоянием 2')}
LOCAL={}
FALLTHROUGH=True
INCLUDE_ORDER=('SpawnClass9ForClass8','SpawnLinkedClass9Records')
UNCLASSIFIED_PREFIX_PATH='Source/Resources/17_ACTION/UnclassifiedE804_BeforeClass8Spawn.bin'
CONTRACTS={('Action',0xE863):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает доступный полный ClassCode записи',
     'при классе 8 действуют все условия SpawnLinkedClass9Records, ACTION банка 0 доступен, четыре байта CPU-стека доступны, IRQ исключены'],
    ['при полном ClassCode не равном 08 возвращаются A=ClassCode и F от CP с 8, остальные регистры и RAM сохраняются',
     'для полного класса 08 A становится 2 и исполняется физическое продолжение SpawnLinkedClass9Records с его точным договором',
     'это состояние 2 детей, StateCode родителя данной загрузкой не присваивается',
     "AF', IX, I/IM/IFF и paging сохраняются, SP после внешнего RET увеличен на два",
     'R добавляет 4 M1 при отказе класса либо 5 к стоимости дочернего создателя, отдельного CALL к нему нет'],
    ["AF, R, при классе 8 остальные рабочие регистры и память по договору SpawnLinkedClass9Records, до четырёх байтов CPU-стека, SP внешним RET"],
    ['код 88 не принимается как класс 8, маскирования старшего бита здесь нет',
     'жёсткий порядок include, (0) SpawnClass9ForClass8.asm, (1) SpawnLinkedClass9Records.asm',
     '16384 сценария проверили все полные классы, два состояния бита запроса, восемь R и четыре младших результата потока по обе стороны порога',
     'реальный создатель исполняется, точные регистры, R, восемь банков и все записи сверены, IRQ, сборка и нативный запуск не выполнялись'])}
COMMENTS={0xE863:(['Проверка полного ClassCode перед специализированным запросом детей, старший бит не маскируется.'],None),
    0xE868:([],'выход, если полный ClassCode отличается от 08, не менять поток и записи'),
    0xE869:(['Подготовка начального StateCode=2 для детей и физическое продолжение по E86B без нового возврата.'],None)}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionClass8SpawnConst','''
                ; Начальное состояние детей специализированного входа класса 8
                module ActionClass8SpawnConst
ChildState      equ #02                                                         ; входной A создателя детей, состояние родителя не изменяется
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xE863):return operation
    return (operation.replace('(IX+#12)','(IX + @FActionRecord.ClassCode)')
            .replace('CP #08','CP @ActionChildSpawnConst.RequiredClass')
            .replace('LD A, #02','LD A, @ActionClass8SpawnConst.ChildState'))

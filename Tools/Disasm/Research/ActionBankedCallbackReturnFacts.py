"""Исходный хвост 6D00 выбирает 10 и снимает внешний возврат."""
FUNCTIONS={0x6D00:('RestoreRuntimePage','Выдача конфигурации 10 в 7FFD и возврат внешнему вызывающему после банкового обработчика')}
LOCAL={}
CONTRACTS={('Action',0x6D00):(
    ['HL, DE, BC сохраняются, AF задаёт сохраняемый F, исходный A не используется', 'на CPU-стеке внешний возврат после уже снятого обработчиком адреса 6D00, нужны ещё четыре временных байта', 'код фиксированного банка 5 и SelectMemoryPage банка 2 доступны, IRQ не вмешиваются'],
    ['HL, DE, BC сохраняются', 'AF - A=10, F сохраняется', "HL', DE', BC', AF' сохраняются", 'IX, IY, I, IM и IFF сохраняются', 'в порт 7FFD выдан 10, при исходной блокировке выбранная конфигурация остаётся прежней', 'SP=входной SP+2, R получает 9 M1 с сохранением бита 7', 'четыре временных байта стека содержат сохранённый BC и адрес 6D05, других записей RAM нет'],
    ['A, R, четыре временных байта CPU-стека, 7FFD при незаблокированном переключении'],
    ['16384 составных сценария с настоящим RET по 6D05 проверяют внешний возврат, все 64 начальные конфигурации и 26 M1 без подмены кода', 'эта целевая RET не доказывает семантику игровых обработчиков, IY диспетчера в этом сценарии остаётся A783 и не восстанавливается из исходного IY', 'входная конфигурация не восстанавливается, выбирается фиксированное значение Runtime', 'это отдельно доказанный возвратный хвост, результат произвольного банкового обработчика не моделируется', '393216 сценариев проверили все BC и AF при шести исходных страницах, точные регистры, RAM, записи и настоящий OUT', 'полное произведение входных регистров, IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
    0x6D00:(['Выбор фиксированной конфигурации ACTION после RET банкового обработчика, прежняя страница не восстанавливается.'],None),
    0x6D02:(['Обновление настоящего порта 7FFD с сохранением F и остальных регистров через SelectMemoryPage.'],None)}
STRUCT_BLOCK='\n                ; Динамические рамки межбанкового диспетчера, новая память не выделяется\n'
for name,fields,size in (
    ('FBankCallbackFrame',(('Continuation','dw #6D00','адрес возвратного хвоста, снимается RET обработчика'),
        ('CallerReturn','dw #0000','внешний возврат, снимается RestoreRuntimePage')),4),
    ('FBankCallbackSelectFrame',(('SavedBC','dw #0000','сохранённый BC внутри SelectMemoryPage'),
        ('ReturnSelect','dw #0000','6CF6 при входе в обработчик либо 6D05 при возврате'),
        ('CallerReturn','dw #0000','внешний возврат исходного диспетчера либо хвоста')),6)):
    STRUCT_BLOCK+='                struct '+name+'\n'
    for label,operation,note in fields:STRUCT_BLOCK+=label.ljust(16)+operation.ljust(64)+'; '+note+'\n'
    STRUCT_BLOCK+='                ends\n                assert '+name+' == #'+format(size,'02X')+'\n\n'
INCLUDE_BLOCKS=(('Includes/Structs/Include.inc','struct FBankCallbackFrame',STRUCT_BLOCK),)
UNCLASSIFIED_SUFFIX_PATH='Source/Resources/17_ACTION/Unclassified017_AfterRuntimePageReturn.bin'


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x6D00):return operation
    return operation.replace('#10','@ActionBankPage.Runtime').replace('CALL #AB1B','CALL @Action.SelectMemoryPage.Entry')

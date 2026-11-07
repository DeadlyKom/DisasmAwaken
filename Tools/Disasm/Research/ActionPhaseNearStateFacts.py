"""State0F, фазовый вызов с игнорированием Carry и обязательный общий хвост близости."""
FUNCTIONS={0xF07C:('UpdatePhaseAndNearVector','Обновление фазового перехода и обязательная обработка близкого широкого вектора')}
LOCAL={}
CONTRACTS={('Action',0xF07C):(
    ['IX указывает FActionRecord, действуют договоры CheckObjectPhaseTransition и UpdateNearVectorPhase',
     'ACTION банка 0 выбран, шесть дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены'],
    ['сначала CheckObjectPhaseTransition может обновить StateCode, SavedStateCode и PhaseMoveTimer',
     'независимо от возвращённого Carry затем исполняется UpdateNearVectorPhase с его точными выходами и возможным StateCode=06',
     'SavedStateCode и PhaseMoveTimer сохраняют результат фазового ребёнка, последующий выбор 06 меняет только StateCode',
     "C, AF', IX, IY, I/IM/IFF и paging сохраняются, PC=F0F8 и SP сохраняется",
     'R добавляет 2 M1 к сумме стоимостей фазовой проверки и общего хвоста, внешнее слово возврата сохраняется'],
    ["HL, DE, B, AF, HL', DE', BC', R, поток 5 и условно поток 0, фазовые поля и операнд порога по договорам детей, до шести байтов CPU-стека"],
    ['исходная цель State0F, Carry фазового ребёнка здесь не проверяется в отличие от State03',
     '1664 сценария родительского входа входят в общий отчёт 75008 сценариев, сверены точные регистры, R, банки и записи',
     'проверка завершается перед F0F8, аппаратные IRQ, сборка и нативный запуск не выполнялись'])}
COMMENTS={0xF07C:(['Обновление фазового перехода, его Carry не запрещает последующий поиск близкого вектора.'],None),
          0xF07F:(['Обязательная передача общего CPU-стека обработчику близких широких векторов.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF07C):return operation
    return operation.replace('CALL #E935','CALL @Action.CheckObjectPhaseTransition.Entry').replace('JR #F087','JR @Action.UpdateNearVectorPhase.Entry')

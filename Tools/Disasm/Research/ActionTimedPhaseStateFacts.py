"""State11, декремент таймера через AF' и безусловные шаги двух фаз."""
FUNCTIONS={0xF3A1:('StepTimedPhasePattern','Обновление таймера и двух фаз с переходом к состоянию 10 при истечении')}
LOCAL={}
CONTRACTS={('Action',0xF3A1):(
    ['HL, DE, BC и AF числовых аргументов не задают, Carry сохраняется декрементом таймера',
     'IX указывает доступные PhaseMoveTimer, OffsetPhase1, OffsetPhase2 и StateCode записи',
     'ACTION банка 0 доступен, внешний CPU-стек сохранён, IRQ не вмешиваются'],
    ['PhaseMoveTimer уменьшается на один по модулю 256, OffsetPhase1 увеличен на четыре, OffsetPhase2 на два на всех путях',
     'только при исходном PhaseMoveTimer=1 таймер после временной записи нуля получает 46, StateCode получает 10',
     'при исходном нуле таймер становится FF, переход состояния не выполняется',
     'A равен результату декремента до возможной перезагрузки таймера, F от этого DEC с входным Carry',
     'AF\' содержит новое OffsetPhase2 и F от ADD прежнего OffsetPhase2,2, исходный AF\' не сохраняется',
     "HL, DE, BC, HL', DE', BC', IX, IY, I/IM/IFF и paging сохраняются, PC=F0F8 и SP сохраняется",
     'R добавляет 18 M1 на обычном пути и 23 при переходе состояния, дополнительных записей CPU-стека нет'],
    ['AF, AF\', R, PhaseMoveTimer, OffsetPhase1, OffsetPhase2 и условно StateCode'],
    ['два EX AF,AF\' сохраняют флаги таймера вокруг расчёта фаз, условный JP использует именно DEC, а не ADD последней фазы',
     '196608 сценариев покрыли все таймеры, фазу 1 и Carry, а также все пары фаз на пути перехода',
     'сверены точные регистры, флаги, R, восемь банков и кратность записей, включая две записи таймера при истечении',
     'общий F0F8 не исполнялся, аппаратные IRQ, сборка и нативный запуск не выполнялись'])}
COMMENTS={
    0xF3A1:(['Обновление таймера состояния, ноль оборачивается в FF, истечение наступает только при исходной единице.'],None),
    0xF3A8:(['Сохранение результата и флагов декремента в AF\' на время расчёта фаз.'],None),
    0xF3A9:(['Расчёт следующего индекса второй фазы с шагом четыре по модулю 256.'],None),
    0xF3B1:(['Расчёт следующего индекса третьей фазы с шагом два, её ADD останется в итоговом AF\'.'],None),
    0xF3B9:(['Восстановление A и флагов таймера перед условием истечения.'],None),
    0xF3BA:([],'переход, если результат декремента таймера ненулевой, сохранить текущее состояние'),
    0xF3BD:(['Обновление таймера исходной длительностью 70 и установка следующего состояния 10.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionTimedPhaseConst','''
                ; Исходные шаги фаз и переход State11 в State10
                module ActionTimedPhaseConst
Phase1Step      equ #04                                                         ; шаг циклического OffsetPhase1
Phase2Step      equ #02                                                         ; шаг циклического OffsetPhase2
ReloadTimer     equ #46                                                         ; длительность следующего состояния, 70 обновлений
NextState       equ #10                                                         ; исходный индекс следующего состояния
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF3A1):return operation
    for literal,name in (('17','PhaseMoveTimer'),('08','OffsetPhase1'),('09','OffsetPhase2'),('0A','StateCode')):
        operation=operation.replace('(IX+#'+literal+')','(IX + @FActionRecord.'+name+')')
    return (operation.replace('ADD A, #04','ADD A, @ActionTimedPhaseConst.Phase1Step')
            .replace('ADD A, #02','ADD A, @ActionTimedPhaseConst.Phase2Step')
            .replace(', #46',', @ActionTimedPhaseConst.ReloadTimer')
            .replace(', #10',', @ActionTimedPhaseConst.NextState')
            .replace('#F0F8','@Action.PrepareObjectOffsetTransform.Entry'))

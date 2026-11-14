"""State11, декремент таймера через AF' и безусловные шаги двух фаз."""
from ActionObjectOffsetTransferFacts import CONTRACTS as OFFSET_TRANSFER_CONTRACTS

_COMMON = OFFSET_TRANSFER_CONTRACTS['Action', 0xF0F8]
_COMMON_OUT = [line.replace('на активной ветви R учитывает', 'на активной ветви общий хвост добавляет к R')
               for line in _COMMON[1][1:]]
_COMMON_NOTES = [line.replace('ранний маркер возвращается до фазовых записей',
                    'маркер внутри F0F8 возвращается до записи общих фазовых операндов')
                 if 'ранний маркер' in line else ('отдельная проверка F0F8, ' + line if '196608 прежних' in line else line)
                 for line in _COMMON[3]]

FUNCTIONS={0xF3A1:('StepTimedPhasePattern','Обновление таймера и двух фаз с переходом к состоянию 10 при истечении')}
LOCAL={}
CONTRACTS={('Action',0xF3A1):(
    ['HL, DE, BC и AF числовых аргументов не задают, входной Carry сохраняется только во временном результате DEC собственного префикса',
     'IX указывает доступные PhaseMoveTimer, OffsetPhase1, OffsetPhase2 и StateCode записи, действуют условия общего F0F8',
     *_COMMON[0][1:]],
    ['при маркере Component0.High=80 после собственного префикса выполняется внешний RET, AF=8042, SP=входной SP+2',
     "на маркере HL/DE/BC, HL'/DE'/BC', IX/IY сохраняются, A' равен wrap8(прежний OffsetPhase2+2), F' от этого ADD",
     'маркер не отменяет собственные фазовые и таймерные записи, на активной ветви последующий полный вычислитель заменяет AF и AF альтернативного набора',
     *_COMMON_OUT,
     'PhaseMoveTimer уменьшается по модулю 256, OffsetPhase1 увеличен на четыре и OffsetPhase2 на два на всех путях',
     'только при исходном PhaseMoveTimer=1 после записи нуля таймер получает 46 и StateCode получает 10',
     'при исходном нулевом таймере записывается FF без смены состояния, фазы всё равно изменяются',
     'общий хвост читает новые фазы и StateCode, сохраняемые слова масштаба обрабатывает по своему полному договору',
     'собственный префикс имеет 18 M1 без истечения и 23 при исходном таймере 1, к ним прибавляется полный общий хвост'],
    [_COMMON[2][0]+', PhaseMoveTimer, OffsetPhase1, OffsetPhase2 и условно StateCode',
     'на маркере изменены AF и AF альтернативного набора, R и собственные поля префикса, вычислитель не вызывается'],
    ["два EX AF, AF' сохраняют флаги DEC до выбора перехода, ADD фаз не выбирает факт истечения таймера",
     "выход AF' от последнего ADD относится только к границе F0F8 и маркерному пути, активный вычислитель его перезаписывает",
     '46, 10, FF и 80 здесь шестнадцатеричные, длительность 46 равна 70 вызовам при отсутствии иных писателей, не доказанным секундам',
     *_COMMON_NOTES,
     '196608 прежних случаев проверяют префикс до F0F8, новая полная композиция добавляет 24576 случаев этого входа до внешнего RET',
     'полная новая композиция двух таймерных входов имеет 49152 случая, проверены регистры включая R, восемь банков, кратность записей и отсутствие OUT',
     'полное произведение фаз, таблиц и аргументов, точные T, IRQ и нативный запуск не доказаны'])}
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

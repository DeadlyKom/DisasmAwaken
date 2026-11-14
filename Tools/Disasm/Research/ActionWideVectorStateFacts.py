"""State01, выбор широкого вектора и дополнительные переходы после шага кодов."""
FUNCTIONS={0xF0BE:('StepSelectedWideVector','Шаг кодов движения к выбранному широкому вектору и проверка следующих состояний')}
LOCAL={0xF0C9:'SelectVector'}
FALLTHROUGH=True
from ActionObjectOffsetTransferFacts import CONTRACTS as OFFSET_TRANSFER_CONTRACTS
_COMMON = OFFSET_TRANSFER_CONTRACTS['Action', 0xF0F8]
_ACTIVE_OUT = [line.replace('на активной ветви R учитывает', 'на активной ветви общий хвост добавляет к R')
    .replace("HL', DE', BC' сохраняются", "HL', DE', BC' сохраняют результаты дочерних процедур")
    .replace('IYH сохраняется', 'IYH сохраняет результат дочерних процедур')
    for line in _COMMON[1][1:]]
CONTRACTS={('Action',0xF0BE):(
    [
     'HL, DE, BC и AF числовых аргументов не задают, альтернативные регистры учитываются договорами дочерних процедур',
     'IX указывает FActionRecord с Components, OffsetPhase1/2, TargetCodeStep, WideTargetIndex, StateCode и ClassCode',
     'WideTargetIndex задаёт индекс строки из трёх dword по 9B27+12*индекс, доступны фактические байты выбранной строки',
     'действуют договоры StepRecordTowardWideVector, CheckLinkedTargetTransition и NextRandomWord2',
     'ACTION банка 0 и таблицы геометрии доступны, 18 дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены',
     'действует договор PrepareObjectOffsetTransform, активной записи доступны фазы, масштабы и предел, результаты и стек не перекрывают код и таблицы',
    ],
    [
     'перед переходами состояния всегда выполнен StepRecordTowardWideVector с IY выбранной строки',
     'CheckLinkedTargetTransition может установить связь и State0E либо выполнить переходы State13/14, Carry немедленно ведёт к общему F0F8',
     'при Carry=0 дополнительный поток 2 вызывается только при ненулевом байте 9B83 и полном ClassCode в диапазоне 1..4',
     'только H нового слова потока 2=41 и L>=5A устанавливают StateCode=0C, это не маскированная проверка класса',
     'все дальнейшие эффекты общего хвоста относятся к полям и регистрам после собственного выбора состояния',
     'при итоговом Component0.High=80 общий хвост возвращает AF=8042 и сохраняет остальные результаты дочерних процедур, R добавляет четыре M1, SP=входной SP+2',
     *_ACTIVE_OUT,
     'на всех путях внешний RET снимает исходный возврат, IX, I/IM/IFF сохраняются, итоговый 7FFD=10',
     'R учитывает все M1 выбора строки и дочерних путей, выбор требует 6+3*(WideTargetIndex+1) M1 до первого CALL, затем прибавляются полные M1 общего хвоста',
     'глубина временного стека до 18 байтов достигается в геометрии, общий вычислитель после возврата детей повторно использует до шести байтов ниже исходного SP',
    ],
    [
     "HL, DE, BC, AF, HL', DE', BC', AF', IY, R, коды движения и условно поля состояний, связи и таймера, состояния потоков, изменяемые операнды дочерних процедур, CPU-стек, 7FFD, три фазовых операнда, Coefficient0..2 и Base0..2",
    ],
    [
     'при WideTargetIndex=FF исходный INC B даёт ноль, DJNZ выполняет 256 сложений, строка находится по A71B, ограничение диапазона не добавлялось',
     'выбор не проверяет границы логического массива, старшие индексы могут читать другие физические данные, их назначение этим не переопределяется',
     'прежние 69632 случая проверяют границу F0F8, новая композиция того же количества исполняет общий подготовитель и вычислитель до внешнего RET',
     'в обеих сериях список кандидатов пуст, другие списки проверены отдельной моделью CheckLinkedTargetTransition до её возврата, полное сочетание этих списков с общим хвостом не проверено',
     'сверены регистры кроме T, точный R, восемь банков, кратность присваиваний и реальные OUT, поля за пределами изменяемых профилей сохраняют исходную подготовку',
     'сохранение альтернативных координатных регистров и IYH общим хвостом относится к результатам дочерних процедур',
     'полное произведение входов, аппаратные IRQ, сборка, точные T и нативный запуск не проверялись',
     *_COMMON[3][:3],
    ])}

# Полные определения символов числовых постусловий общего вычислителя.
from ActionObjectOffsetTransferFacts import CONTRACTS as _FORMULA_OFFSET_CONTRACTS
CONTRACTS['Action', 0xf0be][3].extend(_FORMULA_OFFSET_CONTRACTS['Action', 0xF0F8][3][3:9])

COMMENTS={
    0xF0BE:(['Выбор строки широкого вектора по WideTargetIndex, индекс FF сохраняет исходные 256 итераций DJNZ.'],None),
    0xF0C2:(['Подготовка адреса перед первой строкой и физического размера трёх dword.'],None),
    0xF0C9:(['Расчёт адреса очередной строки прибавлением её исходного размера.'],None),
    0xF0CD:(['Обновление кодов движения через исходное насыщение, банковый корень и оба кодировщика отношения.'],None),
    0xF0D0:(['Проверка случайного выбора связи либо фазовых переходов после изменения кодов движения.'],None),
    0xF0D3:([],'переход, если дочерняя проверка вернула Carry, продолжить общий расчёт смещений'),
    0xF0D6:(['Проверка глобального допуска дополнительного перехода State0C.'],None),
    0xF0DA:([],'переход, если байт допуска равен нулю, продолжить общий расчёт смещений'),
    0xF0DC:(['Проверка полного ClassCode, дополнительный переход разрешён только классам от 1 до 4.'],None),
    0xF0E1:([],'переход, если ClassCode равен нулю, продолжить общий расчёт смещений'),
    0xF0E5:([],'переход, если ClassCode не меньше пяти, продолжить общий расчёт смещений'),
    0xF0E7:(['Обновление отдельного случайного потока 2 после всех предварительных допусков.'],None),
    0xF0EA:(['Проверка точного старшего байта нового слова перед проверкой нижнего порога.'],None),
    0xF0ED:([],'переход, если старший байт нового слова не равен 41, продолжить общий расчёт смещений'),
    0xF0EF:(['Проверка нижней границы младшего байта при уже принятом старшем байте 41.'],None),
    0xF0F2:([],'переход, если младший байт меньше 5A, сохранить состояние и продолжить общий расчёт смещений'),
    0xF0F4:(['Обновление StateCode до 0C после совпадения обоих случайных условий.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionWideStateConst','''
                ; Исходные параметры выбора широкого вектора и перехода State01
                module ActionWideStateConst
BeforeFirst     equ #9B1B                                                       ; адрес перед первой строкой, первое ADD даёт 9B27
VectorStride    equ #000C                                                       ; три dword по четыре байта
ModeByte        equ #9B83                                                       ; глобальный ненулевой допуск, остальные роли отдельно не установлены
FirstExcluded   equ #05                                                         ; верхняя исключённая граница полного ClassCode
RandomHigh      equ #41                                                         ; точное значение H нового слова потока 2
RandomLowMin    equ #5A                                                         ; включённая нижняя граница L
NextState       equ #0C                                                         ; исходный индекс следующего обработчика
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF0BE):return operation
    for literal,name in (('26','WideTargetIndex'),('12','ClassCode'),('0A','StateCode')):
        operation=operation.replace('(IX+#'+literal+')','(IX + @FActionRecord.'+name+')')
    for address,name in ((0x7EB7,'StepRecordTowardWideVector'),(0xE91E,'CheckLinkedTargetTransition'),(0xEBB8,'NextRandomWord2')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    for literal,name in (('LD IY, #9B1B','LD IY, @ActionWideStateConst.BeforeFirst'),
                         ('LD DE, #000C','LD DE, @ActionWideStateConst.VectorStride'),
                         ('(#9B83)','(@ActionWideStateConst.ModeByte)'),
                         ('CP #05','CP @ActionWideStateConst.FirstExcluded'),
                         ('CP #41','CP @ActionWideStateConst.RandomHigh'),
                         ('CP #5A','CP @ActionWideStateConst.RandomLowMin'),
                         (', #0C',', @ActionWideStateConst.NextState'),
                         ('#F0F8','@Action.PrepareObjectOffsetTransform.Entry')):
        operation=operation.replace(literal,name)
    return operation

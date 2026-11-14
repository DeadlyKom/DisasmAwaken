"""Фазовый счётчик и выбор сохранённого состояния по компонентам записи."""
from ActionObjectOffsetTransferFacts import CONTRACTS as OFFSET_TRANSFER_CONTRACTS

_COMMON = OFFSET_TRANSFER_CONTRACTS['Action', 0xF0F8]
_COMMON_OUT = [line.replace('на активной ветви R учитывает', 'на активной ветви общий хвост добавляет к R')
               for line in _COMMON[1][1:] if not line.startswith('OffsetScaleHigh обнулён')]
_COMMON_NOTES = [line.replace('ранний маркер возвращается до фазовых записей',
                    'маркер внутри F0F8 возвращается до записи общих фазовых операндов')
                 if 'ранний маркер' in line else ('отдельная проверка F0F8, ' + line if '196608 прежних' in line else line)
                 for line in _COMMON[3]]

FUNCTIONS = {0xEFB5: ('AdvanceObjectPhaseWait', 'Обновление фазового счётчика и завершение ожидания по классу и компонентам')}
LOCAL = {0xEFCF: 'FoldX', 0xEFD7: 'SaveX', 0xEFE0: 'SaveY', 0xEFE9: 'CompareY', 0xEFED: 'CompareX',
         0xEFF1: 'CheckLimit', 0xEFF6: 'ResumeState'}
STATE_FIELDS = (('PhaseGate', 0xEFBD, 'вращаемый байт в операнде LD A,n, младший бит допускает инкремент'),)
MODIFIED_WRITERS = ((0xEFBF, 0xEFBD, 0xEFBC, 1),)
CONTRACTS = {('Action', 0xEFB5): (
    [_COMMON[0][0],
     'полный ClassCode, SavedStateCode и старшие байты трёх Components читаемы, StateCode и OffsetScaleHigh доступны для записи',
     'PhaseGate является доступным для записи общим операндом LD A,n, исходное значение в бинарнике 11',
     *_COMMON[0][1:]],
    ['при маркере Component0.High=80 выполняется внешний RET после собственного фазового префикса, AF=8042, SP=входной SP+2',
     'на маркере HL/DE, альтернативные регистры, IX/IY сохраняются, BC сохраняется при ClassCode>=08, иначе B=fold(Yhigh), C=fold(Xhigh)',
     'маркер не отменяет PhaseGate, OffsetScaleHigh и StateCode, уже записанные собственным префиксом',
     *_COMMON_OUT,
     'при ClassCode>=08 собственный префикс задаёт StateCode=SavedStateCode и OffsetScaleHigh=0, PhaseGate не вращается',
     'при ClassCode<08 PhaseGate получает RRCA прежнего байта, его исходный бит 0 допускает инкремент OffsetScaleHigh только ниже 0F',
     'для класса ниже 08 максимум fold трёх старших компонент меньше 14 восстанавливает SavedStateCode и обнуляет OffsetScaleHigh',
     'общий хвост дополнительно обнуляет OffsetScaleHigh при ClassCode<10 и итоговом StateCode не равном 13, иначе сохраняет результат фазового префикса',
     'полный R включает собственную стоимость ниже и весь достигнутый F0F8, старший бит R сохраняется'],
    [_COMMON[2][0]+', PhaseGate и условно StateCode',
     'на маркере изменяются AF/R и при классе ниже 08 BC, собственные записи фазового префикса сохраняются, вычислитель не вызывается'],
    ['fold(b)=b XOR FF при установленном бите 7, иначе b, это инверсия отрицательного байта, а не точный модуль',
     '08, 0F, 14, 10, 13 и 11 здесь шестнадцатеричные, соответствующие пороги класса, счётчика и максимума равны 8, 15 и 20 десятичным',
     'PhaseGate общий для всех записей, при изменении только этим RRCA исходный 11 проходит цикл 11, 88, 44, 22, 11',
     'единичный бит 0 встречается один раз за четыре допустимых вызова этого цикла, число не означает четыре кадра для каждой записи',
     'если весь PhaseGate равен нулю, вращение сохраняет ноль и этот префикс не допускает инкремент через бит 0',
     'класс не меньше 08 даёт 11 M1 собственного префикса, без вращения и свёртки компонент',
     'для класса ниже 08 собственная стоимость 28+4*Gate+3*Gate*CanIncrement+NegCount+ChooseY+ChooseX+7*Release M1',
     'Gate исходный бит 0, CanIncrement проверка прежнего OffsetScaleHigh<0F, NegCount число отрицательных старших компонент',
     'ChooseY=1 при fold(Z)<fold(Y), ChooseX=1 при max(fold(Z),fold(Y))<fold(X), Release=1 при максимуме ниже 14, иначе признаки нулевые',
     *_COMMON_NOTES,
     'собственный префикс ранее проверен в 69632 случаях, полная композиция добавляет 49152 профиля ожидания и сохраняет 16384 профиля двух фазовых ходов',
     'в полной композиции проверены регистры включая R, восемь банков, кратность присваиваний, отсутствие OUT и внешний RET',
     'полное произведение входов, точные T, IRQ и нативная игра не доказаны'])}
COMMENTS = {
    0xEFB5: (['Проверка класса перед фазовым ожиданием.'], None),
    0xEFBA: ([], 'переход, если класс не меньше 8, восстановить сохранённое состояние'),
    0xEFBC: (['Вращение фазового операнда и проверка его исходного младшего бита.'], None),
    0xEFC2: ([], 'переход, если младший бит фазы был нулём, пропустить инкремент'),
    0xEFC4: (['Проверка насыщения счётчика перед инкрементом.'], None),
    0xEFC9: ([], 'переход, если счётчик не меньше 15, сохранить его'),
    0xEFCF: (['Свёртка старших байтов трёх компонент, отрицательные значения инвертируются.'], None),
    0xEFD3: ([], 'переход, если старший байт X неотрицателен, сохранить его'),
    0xEFDC: ([], 'переход, если старший байт Y неотрицателен, сохранить его'),
    0xEFE5: ([], 'переход, если старший байт глубины неотрицателен, сравнить его с Y'),
    0xEFE9: (['Поиск максимума свёрнутых компонент.'], None),
    0xEFEA: ([], 'переход, если глубина не меньше Y, сохранить текущий максимум'),
    0xEFEE: ([], 'переход, если текущий максимум не меньше X, проверить порог ожидания'),
    0xEFF1: (['Проверка порога удержания состояния.'], None),
    0xEFF3: ([], 'переход, если максимум не меньше 20, сохранить состояние ожидания'),
    0xEFF6: (['Восстановление сохранённого состояния и сброс фазового счётчика записи.'], None),
}


def name_operands(region, address, operation):
    if region != 'Action' or address != 0xEFB5:
        return operation
    operation = operation.replace('IX+#', 'IX + #')
    for literal, field in (('01', 'Components.Component0.High'), ('03', 'Components.Component1.High'), ('05', 'Components.Component2.High'),
                           ('0A', 'StateCode'), ('12', 'ClassCode'), ('16', 'SavedStateCode'), ('24', 'OffsetScaleHigh')):
        operation = operation.replace('IX + #'+literal, 'IX + @FActionRecord.'+field)
    return (operation.replace('(#EFBD)', '(@ActionObjectPhaseWaitState.PhaseGate)')
            .replace('#F0F8', '@Action.PrepareObjectOffsetTransform.Entry'))

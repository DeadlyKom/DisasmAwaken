"""Общий хвост обработчиков, подготовка операндов смещений и аргументов 6D06."""
from ActionObjectOffsetVectorFacts import CONTRACTS as OFFSET_VECTOR_CONTRACTS

_VECTOR = OFFSET_VECTOR_CONTRACTS['Action', 0x6D06]
_VECTOR_OUT = [line.replace('HIGH входного DE', 'HIGH слова V')
               for line in _VECTOR[1] if not line.startswith('R учитывает')]
_VECTOR_NOTES = [line.replace('HIGH входного DE', 'HIGH слова V').replace('входное DE', 'слово V')
                 for line in _VECTOR[3][:6]]

FUNCTIONS = {0xF0F8: ('PrepareObjectOffsetTransform', 'Проверка маркера записи и подготовка смещений для вычислителя 6D06')}
LOCAL = {0xF11D: 'StoreCounter', 0xF132: 'LoadPhase'}
STATE_FIELDS = (('Offset0', 0xB045, 'операнд первого LD A,n вычислителя B044'),
                ('Offset1', 0xB04F, 'операнд второго LD A,n, исходный байт плюс 128'),
                ('Offset2', 0xB05C, 'операнд третьего LD A,n'))
MODIFIED_WRITERS = ((0xF101, 0xB045, 0xB044, 1), (0xF109, 0xB04F, 0xB04E, 1), (0xF10F, 0xB05C, 0xB05B, 1))
CONTRACTS = {('Action', 0xF0F8): (
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает доступную FActionRecord',
     'читается Component0.High, для активной записи доступны остальные фазовые поля, класс, состояние и порог',
     'OffsetScaleLow и OffsetScaleHigh активной записи доступны для записи, ACTION банка 0 и общая RAM доступны',
     'действует договор ApplyObjectOffsetVector, шесть байтов под SP и внешний возврат не перекрывают его код, таблицы, операнды и результаты',
     'IRQ и повторный вход исключены'],
    ['при Component0.High=80 внешний RET даёт AF=8042, SP=входной SP+2, R учитывает четыре M1, остальные регистры и RAM сохранены',
     'на активной ветви нижеследующие результаты вычислителя относятся к V из прежнего OffsetScaleLow и выбранного старшего байта',
     *_VECTOR_OUT,
     'Offset0..2 получают OffsetPhase0, wrap8(OffsetPhase1+80) и OffsetPhase2',
     'OffsetScaleLow получает wrap8(старое+1), если этот кандидат ниже Phase2OrTarget, иначе сохраняется прежний байт',
     'OffsetScaleHigh обнулён при ClassCode<10 и StateCode не равном 13, иначе сохранён',
     'на активной ветви R учитывает 30+Hold+4*Small+2*Small*Different M1 подготовки плюс полный вычислитель, старший бит R сохраняется'],
    [_VECTOR[2][0] + ', три фазовых операнда и условно OffsetScaleLow/OffsetScaleHigh',
     'на ветви маркера из этого списка изменяются только AF и R, обычный RET снимает внешний возврат'],
    ['эффективное слово V перед 6D06 содержит прежний OffsetScaleLow в E и итоговый OffsetScaleHigh в D, это не входное DE всей процедуры',
     'Hold=1 при сохранении прежнего младшего масштаба, иначе 0, Small=1 при ClassCode<10, Different=1 при StateCode не равном 13, иначе соответствующий признак нулевой',
     '10, 13 и 80 в условиях полей обозначают шестнадцатеричные коды, числа M1 десятичные',
     *_VECTOR_NOTES,
     'ранний маркер возвращается до фазовых записей и не вызывает вычислитель, на активном пути внешний RET выполняет его хвост',
     '196608 прежних сценариев останавливаются перед 6D06 либо на раннем RET, новая композиция проверяет 15616 случаев до полного внешнего возврата',
     'полное произведение всех аргументов, точные T, IRQ и нативная игра не доказаны'])}
COMMENTS = {
    0xF0F8: (['Проверка маркера отсутствующей записи перед обновлением операндов.'], None),
    0xF0FD: ([], 'выход, если старший байт первой компоненты равен 80'),
    0xF0FE: (['Подготовка трёх байтов смещений вычислителя, второй сдвинут на 128 по модулю байта.'], None),
    0xF112: (['Расчёт кандидата следующего счётчика с сохранением старого значения в E.'], None),
    0xF11A: ([], 'переход, если байтовый кандидат меньше Phase2OrTarget, записать его'),
    0xF120: (['Проверка класса и состояния перед сбросом фазового счётчика.'], None),
    0xF125: ([], 'переход, если класс не меньше 16, сохранить фазовый счётчик'),
    0xF12C: ([], 'переход, если состояние равно 13, сохранить фазовый счётчик'),
    0xF132: (['Подготовка D для вычислителя и хвостовая передача с прежним CPU-стеком.'], None),
}


def qualify_mutations(modified, flow, functions, pieces):
    for item in modified:
        if item['region'] == 'Action' and item['writer'] in (0xF101, 0xF109, 0xF10F):
            item.update(target_bank=2, target_source_classified=False)


def name_operands(region, address, operation):
    if region != 'Action' or address != 0xF0F8:
        return operation
    operation = operation.replace('IX+#', 'IX + #')
    for literal, field in (('01', 'Components.Component0.High'), ('07', 'OffsetPhase0'), ('08', 'OffsetPhase1'), ('09', 'OffsetPhase2'),
                           ('0A', 'StateCode'), ('0F', 'Phase2OrTarget'), ('10', 'OffsetScaleLow'), ('12', 'ClassCode'), ('24', 'OffsetScaleHigh')):
        operation = operation.replace('IX + #'+literal, 'IX + @FActionRecord.'+field)
    for index, literal in enumerate(('B045', 'B04F', 'B05C')):
        operation = operation.replace('(#'+literal+')', '(@ActionObjectOffsetTransferState.Offset'+str(index)+')')
    return operation.replace('JP #6D06', 'JP @Action.ApplyObjectOffsetVector.Entry')

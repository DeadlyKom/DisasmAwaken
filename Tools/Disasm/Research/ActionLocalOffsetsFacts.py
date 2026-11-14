"""F6CD, фазы из 0D..0F и масштаб из 10, без маркерной проверки F0F8."""
from ActionObjectOffsetVectorFacts import CONTRACTS as OFFSET_VECTOR_CONTRACTS

_VECTOR = OFFSET_VECTOR_CONTRACTS['Action', 0x6D06]
_VECTOR_OUT = [line.replace('HIGH входного DE', 'HIGH слова V')
               for line in _VECTOR[1] if not line.startswith('R учитывает')]
_VECTOR_NOTES = [line.replace('HIGH входного DE', 'HIGH слова V').replace('входное DE', 'слово V')
                 for line in _VECTOR[3][:6]]

FUNCTIONS={0xF6CD:('ApplyRecordLocalOffsets','Увеличение фазового индекса и расчёт баз по отдельным фазам из байтов 0D..0F записи')}
LOCAL={}
MODIFIED_WRITERS=((0xF6D3,0xB045,0xB044,1),(0xF6DB,0xB04F,0xB04E,1),(0xF6E1,0xB05C,0xB05B,1))
CONTRACTS={('Action',0xF6CD):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает доступную FActionRecord',
     'Phase0OrLink, LocalPhase1, Phase2OrTarget и OffsetScaleLow читаемы, OffsetPhase0 доступен для записи',
     'действует договор ApplyObjectOffsetVector, ACTION банка 0 выбран, исходные фазовые таблицы доступны',
     'шесть байтов под SP и внешний возврат не перекрывают код, поля записи, таблицы, операнды и результаты, IRQ и повторный вход исключены'],
    ['нижеследующие результаты вычислителя относятся к V=zero_extend(OffsetScaleLow), исходные HL/DE/BC/AF входа числовых аргументов не задают',
     *_VECTOR_OUT,
     'OffsetPhase0 увеличен на один по модулю 256, это значение не является первой фазой текущего вызова',
     'Offset0..2 получают Phase0OrLink, wrap8(LocalPhase1+80) и Phase2OrTarget',
     'OffsetScaleLow и OffsetScaleHigh сохраняются, Component0.High не проверяется',
     'R добавляет 16 M1 к полному ApplyObjectOffsetVector, максимальная дополнительная рамка равна шести байтам'],
    [_VECTOR[2][0] + ', OffsetPhase0 и три фазовых операнда'],
    ['эффективное слово V перед вычислителем имеет D=00 и E=OffsetScaleLow, поэтому оно беззнаковое 0..255',
     'Phase2OrTarget здесь используется как фазовый индекс, его роли цели и предела других обработчиков не переопределяются',
     '80 в поправке второй фазы шестнадцатеричное, это десятичный полупериод 128',
     *_VECTOR_NOTES,
     '65536 сценариев этого входа входят в существующие 131072, реальные коэффициенты и три умножителя исполняются до полного RET',
     'точные регистры, R, восемь банков и записи ранее проверены, новый числовой прогон ради уточнения договора не объявляется',
     'полное произведение входов, точные T, IRQ и нативная игра не доказаны'])}
COMMENTS={0xF6CD:(['Обновление OffsetPhase0 по модулю 256, фазы текущего расчёта читаются отдельно из 0D..0F.'],None),
    0xF6D0:(['Подготовка первой фазы из Phase0OrLink, увеличенный OffsetPhase0 здесь не читается.'],None),
    0xF6D6:(['Расчёт второй фазы из LocalPhase1 с полупериодом 128 по модулю байта.'],None),
    0xF6DE:(['Подготовка третьей фазы из физического байта Phase2OrTarget, в этом состоянии он не разыменовывается как индекс записи.'],None),
    0xF6E4:(['Подготовка неотрицательного масштаба с D=00 и E=OffsetScaleLow без изменения исходного байта.'],None),
    0xF6E9:(['Расчёт коэффициентов и трёх базовых слов с исходным внешним возвратом.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF6CD):return operation
    for literal,name in (('07','OffsetPhase0'),('0D','Phase0OrLink'),('0E','LocalPhase1'),('0F','Phase2OrTarget'),('10','OffsetScaleLow')):
        operation=operation.replace('(IX+#'+literal+')','(IX + @FActionRecord.'+name+')')
    for address,name in ((0xB045,'Offset0'),(0xB04F,'Offset1'),(0xB05C,'Offset2')):
        operation=operation.replace('(#'+format(address,'04X')+')','(@ActionObjectOffsetTransferState.'+name+')')
    return operation.replace('JP #6D06','JP @Action.ApplyObjectOffsetVector.Entry')


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer'] in (0xF6D3,0xF6DB,0xF6E1):
            item.update(writer_slot=17,writer_offset=item['writer']-0x6000,writer_bank=0,
                target_slot=17,target_offset=item['target']-0x6000,target_bank=2,target_region='Action',
                target_path='Source/Action/BuildObjectOffsetCoefficients.asm',target_source_classified=True,writer_source_classified=True)

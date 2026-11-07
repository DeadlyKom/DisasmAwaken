"""F6CD, фазы из 0D..0F и масштаб из 10, без маркерной проверки F0F8."""
FUNCTIONS={0xF6CD:('ApplyRecordLocalOffsets','Увеличение фазового индекса и расчёт баз по отдельным фазам из байтов 0D..0F записи')}
LOCAL={}
MODIFIED_WRITERS=((0xF6D3,0xB045,0xB044,1),(0xF6DB,0xB04F,0xB04E,1),(0xF6E1,0xB05C,0xB05B,1))
CONTRACTS={('Action',0xF6CD):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает доступную FActionRecord',
     'читаются Unknown0D, Unknown0E, TargetIndex и Unknown10, OffsetPhase0 доступен для записи',
     'действуют договоры BuildObjectOffsetCoefficients и ApplyObjectOffsetVector, исходные фазовые таблицы доступны',
     'ACTION банка 0 выбран, шесть дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены'],
    ['OffsetPhase0 увеличен на один по модулю 256, это значение не используется как первая фаза данного вызова',
     'операнды Offset0, Offset1 и Offset2 получают Unknown0D, wrap8(Unknown0E+80) и TargetIndex соответственно',
     'DE перед вычислителем содержит D=00 и E=Unknown10, значение без знака 0..255, Unknown10 не изменяется',
     'ApplyObjectOffsetVector записывает Base0..2, HL, DE, BC, AF, AF\' и IYL определяются настоящим вычислителем и последним произведением',
     "HL', DE', BC', IX, IYH, I/IM/IFF и paging сохраняются, SP после внешнего RET увеличен на два",
     'нет проверки Component0.High и обновления Unknown24, в отличие от общего подготовителя F0F8',
     'R добавляет 16 M1 к стоимости ApplyObjectOffsetVector, максимальная дополнительная рамка равна шести байтам'],
    ['HL, DE, BC, AF, AF\', IYL, R, OffsetPhase0, три фазовых операнда, три коэффициента, Base0..2 и шесть временных байтов CPU-стека, SP внешним RET'],
    ['TargetIndex является физическим именем байта 0F по ранее доказанному применению, здесь тот же байт используется как фазовый индекс',
     'Unknown0D и Unknown0E не переименовываются глобально по одному контексту, общего назначения всех их писателей пока нет',
     '65536 сценариев этого входа входят в общий набор из 131072, реальные коэффициенты и все три умножителя исполняются до полного RET',
     'точные регистры, флаги, R, восемь банков и записи проверены, полное произведение входов, IRQ, сборка и нативный запуск не выполнялись'])}
COMMENTS={0xF6CD:(['Обновление OffsetPhase0 по модулю 256, фазы текущего расчёта читаются отдельно из 0D..0F.'],None),
    0xF6D0:(['Подготовка первой фазы из Unknown0D, увеличенный OffsetPhase0 здесь не читается.'],None),
    0xF6D6:(['Расчёт второй фазы из Unknown0E с полупериодом 128 по модулю байта.'],None),
    0xF6DE:(['Подготовка третьей фазы из физического байта TargetIndex, в этом состоянии он не разыменовывается как индекс записи.'],None),
    0xF6E4:(['Подготовка неотрицательного масштаба с D=00 и E=Unknown10 без изменения исходного байта.'],None),
    0xF6E9:(['Расчёт коэффициентов и трёх базовых слов с исходным внешним возвратом.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF6CD):return operation
    for literal,name in (('07','OffsetPhase0'),('0D','Unknown0D'),('0E','Unknown0E'),('0F','TargetIndex'),('10','Unknown10')):
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

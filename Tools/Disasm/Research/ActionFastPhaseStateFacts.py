"""State04, отдельные INC с исходной кратностью записей и общий хвост локальных фаз."""
FUNCTIONS={0xF6AB:('StepFastRecordPhases','Увеличение второй и третьей фаз на два и три перед общим расчётом локальных смещений')}
LOCAL={}
CONTRACTS={('Action',0xF6AB):(
    ['IX указывает FActionRecord, OffsetPhase1 и OffsetPhase2 доступны для записи',
     'действует договор ApplyRecordLocalOffsets, ACTION банка 0 и таблицы доступны, шесть байтов CPU-стека доступны, IRQ исключены'],
    ['OffsetPhase1 увеличен двумя INC, OffsetPhase2 тремя INC по модулю 256, все промежуточные записи сохранены',
     'хвост ApplyRecordLocalOffsets дополнительно увеличивает OffsetPhase0 на один, фазы самого вычислителя читает из 0D..0F',
     'регистры и Base0..2 определяются ApplyRecordLocalOffsets и его настоящими умножителями',
     "HL', DE', BC', IX, IYH, I/IM/IFF и paging сохраняются, SP после внешнего RET увеличен на два",
     'R добавляет 11 M1 к стоимости ApplyRecordLocalOffsets, дополнительный CALL между входом и хвостом отсутствует'],
    ['HL, DE, BC, AF, AF\', IYL, R, OffsetPhase0..2, фазовые операнды, коэффициенты и Base0..2, до шести байтов CPU-стека, SP внешним RET'],
    ['это исходная цель State04, изменение фаз записи и фазы вычислителя по 0D..0F не отождествляются',
     '65536 сценариев этого входа исчерпали все пары OffsetPhase1 и OffsetPhase2, полный общий набор содержит 131072 сценария',
     'проверены точные регистры, флаги, R, восемь банков и кратность промежуточных записей до полного внешнего RET',
     'полное произведение входов, аппаратные IRQ, сборка и нативный запуск не выполнялись'])}
COMMENTS={0xF6AB:(['Обновление второй фазы двумя отдельными INC, промежуточное значение сохраняется в исходном порядке.'],None),
          0xF6B1:(['Обновление третьей фазы тремя отдельными INC с байтовым оборачиванием.'],None),
          0xF6BA:(['Передача исходного внешнего возврата общему вычислителю локальных фаз.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF6AB):return operation
    return (operation.replace('(IX+#08)','(IX + @FActionRecord.OffsetPhase1)')
            .replace('(IX+#09)','(IX + @FActionRecord.OffsetPhase2)')
            .replace('JP #F6CD','JP @Action.ApplyRecordLocalOffsets.Entry'))

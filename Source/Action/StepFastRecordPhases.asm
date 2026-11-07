                module Action
                module StepFastRecordPhases
                ; Документация [алгоритм и проверка](../../Docs/ActionFastPhaseState.md)
                ; -----------------------------------------
                ; Увеличение второй и третьей фаз на два и три перед общим расчётом локальных смещений
                ; исходная запись 17, адреса F6AB..F6BC
                ; In:
                ;   IX указывает FActionRecord, OffsetPhase1 и OffsetPhase2 доступны для записи
                ;   действует договор ApplyRecordLocalOffsets, ACTION банка 0 и таблицы доступны, шесть байтов CPU-стека доступны, IRQ исключены
                ; Out:
                ;   OffsetPhase1 увеличен двумя INC, OffsetPhase2 тремя INC по модулю 256, все промежуточные записи сохранены
                ;   хвост ApplyRecordLocalOffsets дополнительно увеличивает OffsetPhase0 на один, фазы самого вычислителя читает из 0D..0F
                ;   регистры и Base0..2 определяются ApplyRecordLocalOffsets и его настоящими умножителями
                ;   HL', DE', BC', IX, IYH, I/IM/IFF и paging сохраняются, SP после внешнего RET увеличен на два
                ;   R добавляет 11 M1 к стоимости ApplyRecordLocalOffsets, дополнительный CALL между входом и хвостом отсутствует
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IYL, R, OffsetPhase0..2, фазовые операнды, коэффициенты и Base0..2, до шести байтов CPU-стека, SP внешним RET
                ; Note:
                ;   это исходная цель State04, изменение фаз записи и фазы вычислителя по 0D..0F не отождествляются
                ;   65536 сценариев этого входа исчерпали все пары OffsetPhase1 и OffsetPhase2, полный общий набор содержит 131072 сценария
                ;   проверены точные регистры, флаги, R, восемь банков и кратность промежуточных записей до полного внешнего RET
                ;   полное произведение входов, аппаратные IRQ, сборка и нативный запуск не выполнялись
                ; -----------------------------------------
                ; Обновление второй фазы двумя отдельными INC, промежуточное значение сохраняется в исходном порядке.
Entry:          INC (IX + @FActionRecord.OffsetPhase1)
                INC (IX + @FActionRecord.OffsetPhase1)
                ; Обновление третьей фазы тремя отдельными INC с байтовым оборачиванием.
                INC (IX + @FActionRecord.OffsetPhase2)
                INC (IX + @FActionRecord.OffsetPhase2)
                INC (IX + @FActionRecord.OffsetPhase2)
                ; Передача исходного внешнего возврата общему вычислителю локальных фаз.
                JP @Action.ApplyRecordLocalOffsets.Entry

                endmodule
                endmodule

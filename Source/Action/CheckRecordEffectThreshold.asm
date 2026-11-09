                module Action
                module CheckRecordEffectThreshold
                ; Документация [алгоритм и проверка](../../Docs/ActionRecordEffectResume.md)
                ; -----------------------------------------
                ; Выбор порога запуска большого эффекта для текущей записи
                ; исходная запись 17, код ACTION банка 0, смещения #9792..#97BE
                ; In:
                ;   HL, DE, BC и AF входных числовых аргументов не задают, IX указывает текущую FActionRecord
                ;   читаются LinkedIndex, LinkFlags, Unknown13 и байты AntiMissilePs1 и AntiMissilePs2
                ;   OtherLinkLimit и Link1ABaseLimit задают текущие байты двух изменяемых операндов LD C,n, исходно оба 0A
                ;   для фактически выбранного пути эффекта действуют условия PrepareLargeEffect и ResumeAfterRecordEffect
                ; Out:
                ;   на прямом переходе StoreRemainder HL и DE сохранены, B сохранён, C содержит выбранный порог, AF задаётся SUB Unknown13,C
                ;   на прямом переходе альтернативные и индексные регистры, I, IM, IFF и paging сохраняются, SP не меняется
                ;   при Unknown13 меньше порога вызывается PrepareLargeEffect, далее ResumeAfterRecordEffect продолжает обход записей
                ;   на пути эффекта итоговые регистры и память определяются договорами этих двух процедур
                ; Corrupt:
                ;   BC в части C и AF на прямой ветви, эффекты PrepareLargeEffect и ResumeAfterRecordEffect на ветви вызова
                ; Note:
                ;   при LinkedIndex, отличном от 1A, выбирается OtherLinkLimit, поле 02 ApplyParameterSet записывает операнд F798
                ;   при LinkedIndex=1A и сброшенном бите 3 выбирается Link1ABaseLimit, поле 00 пишет операнд F79C
                ;   при LinkedIndex=1A и установленном бите 3 наличие PS1 выбирает 1E, иначе наличие PS2 выбирает 3C, иначе 14
                ;   любой байт оборудования, отличный от FF, считается наличием, PS1 имеет приоритет над PS2
                ;   на выбранном изменяемом пути порог 00 не допускает эффект, порог FF допускает значения Unknown13 от 00 до FE
                ;   136192 сценария выполняют реальный ApplyParameterSet и выбор ветви, тело эффекта в этой серии не исполняется
                ;   прежняя сквозная серия подтверждает эффект класса 16 при исходных 0A/0A, R/T, IRQ и нативный запуск не доказаны
                ; -----------------------------------------
                ; Проверка индекса связи перед выбором ветви порога.
Entry:          LD A, (IX + @FActionRecord.LinkedIndex)
                CP #1A
                ; Чтение изменяемого OtherLinkLimit, исходный операнд равен 0A.
                LD C, #0A
                JR NZ, @Action.CheckRecordEffectThreshold.CompareValue          ; переход, если индекс связи отличается от #1A, использовать OtherLinkLimit

                ; Чтение изменяемого Link1ABaseLimit для связи 1A, исходный операнд равен 0A.
                LD C, #0A
                ; Проверка бита 3 LinkFlags.
                BIT 3, (IX + @FActionRecord.LinkFlags)
                JR Z, @Action.CheckRecordEffectThreshold.CompareValue           ; переход, если бит 3 LinkFlags сброшен, использовать Link1ABaseLimit

                ; Проверка первого и второго байтов выбора порога.
                LD A, (@ActionShipEquipment.AntiMissilePs1.Value)
                INC A
                LD C, #1E
                JR NZ, @Action.CheckRecordEffectThreshold.CompareValue          ; переход, если первый байт отличается от #FF, использовать #1E

                LD A, (@ActionShipEquipment.AntiMissilePs2.Value)
                INC A
                LD C, #3C
                JR NZ, @Action.CheckRecordEffectThreshold.CompareValue          ; переход, если второй байт отличается от #FF, использовать #3C

                LD C, #14
                ; Сравнение байта записи с выбранным порогом.
CompareValue:   LD A, (IX + @FActionRecord.Unknown13)
                SUB C
                JP NC, @Action.DispatchObjectState.StoreRemainder               ; переход, если байт не меньше порога, продолжить диспетчеризацию

                CALL @Action.PrepareLargeEffect.Entry
                ; JP @Action.ResumeAfterRecordEffect.Entry, продолжение в ResumeAfterRecordEffect.asm

                endmodule
                endmodule

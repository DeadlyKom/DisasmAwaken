                module Action
                module StepTimedPhasePattern
                ; Документация [алгоритм и проверка](../../Docs/ActionTimedPhaseState.md)
                ; -----------------------------------------
                ; Обновление таймера и двух фаз с переходом к состоянию 10 при истечении
                ; исходная запись 17, адреса F3A1..F3C7
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, Carry сохраняется декрементом таймера
                ;   IX указывает доступные PhaseMoveTimer, OffsetPhase1, OffsetPhase2 и StateCode записи
                ;   ACTION банка 0 доступен, внешний CPU-стек сохранён, IRQ не вмешиваются
                ; Out:
                ;   PhaseMoveTimer уменьшается на один по модулю 256, OffsetPhase1 увеличен на четыре, OffsetPhase2 на два на всех путях
                ;   только при исходном PhaseMoveTimer=1 таймер после временной записи нуля получает 46, StateCode получает 10
                ;   при исходном нуле таймер становится FF, переход состояния не выполняется
                ;   A равен результату декремента до возможной перезагрузки таймера, F от этого DEC с входным Carry
                ;   AF' содержит новое OffsetPhase2 и F от ADD прежнего OffsetPhase2,2, исходный AF' не сохраняется
                ;   HL, DE, BC, HL', DE', BC', IX, IY, I/IM/IFF и paging сохраняются, PC=F0F8 и SP сохраняется
                ;   R добавляет 18 M1 на обычном пути и 23 при переходе состояния, дополнительных записей CPU-стека нет
                ; Corrupt:
                ;   AF, AF', R, PhaseMoveTimer, OffsetPhase1, OffsetPhase2 и условно StateCode
                ; Note:
                ;   два EX AF,AF' сохраняют флаги таймера вокруг расчёта фаз, условный JP использует именно DEC, а не ADD последней фазы
                ;   196608 сценариев покрыли все таймеры, фазу 1 и Carry, а также все пары фаз на пути перехода
                ;   сверены точные регистры, флаги, R, восемь банков и кратность записей, включая две записи таймера при истечении
                ;   общий F0F8 не исполнялся, аппаратные IRQ, сборка и нативный запуск не выполнялись
                ; -----------------------------------------
                ; Обновление таймера состояния, ноль оборачивается в FF, истечение наступает только при исходной единице.
Entry:          LD A, (IX + @FActionRecord.PhaseMoveTimer)
                DEC A
                LD (IX + @FActionRecord.PhaseMoveTimer), A
                ; Сохранение результата и флагов декремента в AF' на время расчёта фаз.
                EX AF, AF'
                ; Расчёт следующего индекса второй фазы с шагом четыре по модулю 256.
                LD A, (IX + @FActionRecord.OffsetPhase1)
                ADD A, @ActionTimedPhaseConst.Phase1Step
                LD (IX + @FActionRecord.OffsetPhase1), A
                ; Расчёт следующего индекса третьей фазы с шагом два, её ADD останется в итоговом AF'.
                LD A, (IX + @FActionRecord.OffsetPhase2)
                ADD A, @ActionTimedPhaseConst.Phase2Step
                LD (IX + @FActionRecord.OffsetPhase2), A
                ; Восстановление A и флагов таймера перед условием истечения.
                EX AF, AF'
                JP NZ, @Action.PrepareObjectOffsetTransform.Entry               ; переход, если результат декремента таймера ненулевой, сохранить текущее состояние

                ; Обновление таймера исходной длительностью 70 и установка следующего состояния 10.
                LD (IX + @FActionRecord.PhaseMoveTimer), @ActionTimedPhaseConst.ReloadTimer
                LD (IX + @FActionRecord.StateCode), @ActionTimedPhaseConst.NextState
                JP @Action.PrepareObjectOffsetTransform.Entry

                endmodule
                endmodule

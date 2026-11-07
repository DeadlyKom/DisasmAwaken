                module Action
                module UpdateNearVectorPhase
                ; Документация [алгоритм и проверка](../../Docs/ActionNearPhase.md)
                ; -----------------------------------------
                ; Проверка близких широких векторов, случайного состояния 6 и шага фазы записи
                ; исходная запись 17, адреса F087..F0BD
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает доступные StateCode и OffsetPhase1 записи
                ;   действуют договоры FindFirstNearWideVector, MaxFoldedVectorHigh и NextRandomWord0
                ;   список широких векторов, его счётчик, глобальные High0..High2 и состояние потока 0 доступны
                ;   ACTION банка 0 выбран, шесть дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены
                ; Out:
                ;   FindFirstNearWideVector выбирает первый близкий вектор либо возвращает L=7F, его числовой результат L сравнивается с 4
                ;   при L<4 RandomHighMin получает 28+4*L и вызывается поток 0, если H>>1 не меньше порога и L=7F, StateCode=06
                ;   после StateCode=06 глобальная проверка и увеличение OffsetPhase1 пропускаются, AF=7F6A
                ;   во всех остальных случаях MaxFoldedVectorHigh вычисляет максимум глобальных свёрнутых High0..High2, при максимуме меньше 4 OffsetPhase1 увеличен по модулю 256
                ;   при увеличении A равен новой фазе, F соответствует INC прежней фазы с Carry=1, иначе A равен глобальному максимуму и F от CP с 4
                ;   HL соответствует выбранному широкому вектору либо потоку, L после глобальной проверки равен глобальному максимуму
                ;   DE и B определяются FindFirstNearWideVector, C сохраняется, альтернативные HL, DE и BC меняются только при потоке 0
                ;   AF', IX, IY, I/IM/IFF и paging сохраняются, PC=F0F8 и SP сохраняется, внешний возврат не исполнен
                ;   R точно проверен композицией поиска, потока и глобального максимума, формула накладных M1 приведена в документации
                ; Corrupt:
                ;   HL, DE, B, AF, HL', DE', BC' при потоке 0, R, RandomHighMin, StateCode либо OffsetPhase1 по ветвям, до шести байтов CPU-стека
                ; Note:
                ;   результат поиска и глобальные High0..High2 относятся к разным источникам, их близость не отождествляется
                ;   операнд RandomHighMin исходно равен 28, каждый достигнутый случайный путь пересчитывает его, новое значение не выделяет RAM
                ;   71680 сценариев этого входа и 3328 двух родительских состояний проверены совместно, общий отчёт содержит 75008 сценариев
                ;   реальные дети исполняются, сравниваются регистры, флаги, R, SP, восемь банков и все записи
                ;   проверка останавливается перед F0F8, полный кадр, IRQ, точные T, сборка и нативный запуск не выполнялись
                ; -----------------------------------------
                ; Поиск первого близкого широкого вектора, его результат L не подменяется глобальным максимумом.
Entry:          CALL @Action.FindFirstNearWideVector.Entry
                ; Проверка результата поиска перед случайным переводом текущей записи в состояние 6.
                LD A, L
                CP @ActionNearPhaseConst.SmallLimit
                JR NC, @Action.UpdateNearVectorPhase.CheckGlobal                ; переход, если результат L не меньше 4, пропустить поток 0 и проверить глобальные байты

                ; Расчёт порога 40+4*L для половины старшего байта нового слова потока 0.
                ADD A, A
                ADD A, A
                ADD A, @ActionNearPhaseConst.RandomBase
                ; Обновление исходного операнда CP n рассчитанным порогом без выделения новой памяти.
                LD (@ActionNearPhaseState.RandomHighMin), A
                ; Получение одного нового слова потока 0 для обеих случайных проверок.
                CALL @Action.NextRandomWord0.Entry
                ; Расчёт беззнаковой половины старшего байта нового слова.
                LD A, H
                SRL A
                ; Проверка половины старшего байта по только что рассчитанному RandomHighMin.
                CP #28
                JR C, @Action.UpdateNearVectorPhase.CheckGlobal                 ; переход, если половина H меньше RandomHighMin, проверить глобальные байты

                ; Проверка точного младшего байта 7F того же нового слова.
                LD A, L
                CP @ActionNearPhaseConst.RandomLowCode
                JR NZ, @Action.UpdateNearVectorPhase.CheckGlobal                ; переход, если младший байт нового слова отличается от 7F, проверить глобальные байты

                ; Обновление состояния 6, эта ветвь пропускает увеличение фазового индекса.
                LD (IX + @FActionRecord.StateCode), @ActionNearPhaseConst.SelectedState
                JP @Action.PrepareObjectOffsetTransform.Entry

                ; Проверка отдельного глобального максимума, High0..High2 не являются результатом предыдущего поиска.
CheckGlobal:    CALL @Action.MaxFoldedVectorHigh.Entry
                LD A, L
                CP @ActionNearPhaseConst.SmallLimit
                JR NC, @Action.PrepareObjectOffsetTransform.Entry               ; переход, если глобальный максимум не меньше 4, сохранить фазу и продолжить общий хвост

                ; Обновление циклического индекса OffsetPhase1 на единицу, FF переходит в 00.
                LD A, (IX + @FActionRecord.OffsetPhase1)
                INC A
                LD (IX + @FActionRecord.OffsetPhase1), A
                JP @Action.PrepareObjectOffsetTransform.Entry

                endmodule
                endmodule

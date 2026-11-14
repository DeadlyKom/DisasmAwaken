                module ArchiveEngine
                module UpdateMeters
                ; Документация [экранные индикаторы](../../Docs/ArchiveEngineMeters.md)
                ; -----------------------------------------
                ; добавление до одного столбца в каждой полосе с восстановлением страницы
                ; In:
                ;   селектор страниц настроен, State.CurrentCode содержит текущий логический код
                ;   поля обоих индикаторов содержат цели, показанные размеры, адреса и маски
                ; Out:
                ;   экранные столбцы добавлены там, где показанный размер меньше цели
                ;   исходный код страницы восстановлен, IrqSavedCode содержит этот код
                ; Corrupt:
                ;   HL, BC, AF
                ; -----------------------------------------
                ; сохранение страницы прерванного кадра и выбор теневого экрана
Entry:          LD A, (@ArchiveEnginePages.State.CurrentCode)
                LD (@ArchiveEnginePages.State.IrqSavedCode), A
                LD A, @ArchiveEngineConst.ScreenPage
                CALL @ArchiveEngine.SelectPage.Entry

                ; обновление левого и правого индикаторов
                CALL @ArchiveEngine.ExtendLeftMeter.Entry
                CALL @ArchiveEngine.ExtendRightMeter.Entry

                ; восстановление страницы кадра перед продолжением IRQ
                LD A, (@ArchiveEnginePages.State.IrqSavedCode)
                CALL @ArchiveEngine.SelectPage.Entry
                RET

                endmodule
                endmodule

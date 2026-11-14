                module ArchiveEngine
                module PrepareCombatScene
                ; Документация [запуск и цикл ENGINE](../../Docs/ArchiveEngineStartup.md)
                ; -----------------------------------------
                ; подготовка фона, индикаторов, времени и первого кадра бойцов
                ; In:
                ;   рабочий фон, маски BD и обе таблицы BAR загружены, селектор настроен
                ; Out:
                ;   копии фона доступны в страницах 13 и 14, таблица зеркальных битов готова
                ;   оба индикатора инициализированы, на рабочем растре подготовлен первый кадр
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, банковое окно
                ; -----------------------------------------
Entry:          CALL @ArchiveEngine.PrepareScenePages.Entry
                CALL @ArchiveEngine.BuildMirrorTable.Entry
                CALL @ArchiveEngine.InitializeMeters.Entry
                CALL @ArchiveEngine.InitializeTimer.Entry
                CALL @ArchiveEngine.ApplyFighterFrames.Entry
                CALL @ArchiveEngine.ComposeCombatFrame.Entry
                RET

                endmodule
                endmodule

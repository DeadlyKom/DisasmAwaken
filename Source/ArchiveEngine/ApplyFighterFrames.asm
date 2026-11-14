                module ArchiveEngine
                module ApplyFighterFrames
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; подготовка текущих кадров обоих бойцов в общей странице BAR
                ; In:
                ;   обе таблицы BAR доступны в странице 0, записи бойцов подготовлены
                ; Out:
                ;   изменённые группы и ожидающие кадры применены, IX указывает на второго бойца
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, банковое окно
                ; -----------------------------------------
Entry:          LD A, @ArchiveEngineConst.BarPage
                CALL @ArchiveEngine.SelectPage.Entry
                LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.ApplyFighterAction.Entry
                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.ApplyFighterAction.Entry
                RET

                endmodule
                endmodule

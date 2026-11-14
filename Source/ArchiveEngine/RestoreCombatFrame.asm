                module ArchiveEngine
                module RestoreCombatFrame
                ; Документация [возврат фона](../../Docs/Scene1PixelPairs.md#восстановление-фона-под-бойцом)
                ; -----------------------------------------
                ; восстановление фона из-под двух цифр и обоих предыдущих кадров бойцов
                ; In:
                ;   буфер фона цифр, записи бойцов и обе копии исходной сцены подготовлены
                ; Out:
                ;   бывшие области цифр и бойцов в рабочем растре восстановлены
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, банковое окно
                ; -----------------------------------------
Entry:          CALL @ArchiveEngine.RestoreTimerBackground.Entry
                LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.RestoreFighterBackground.Entry
                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.RestoreFighterBackground.Entry
                RET

                endmodule
                endmodule

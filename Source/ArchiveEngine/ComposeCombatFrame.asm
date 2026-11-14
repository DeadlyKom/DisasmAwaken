                module ArchiveEngine
                module ComposeCombatFrame
                ; Документация [запуск и цикл ENGINE](../../Docs/ArchiveEngineStartup.md)
                ; -----------------------------------------
                ; наложение кадров второго и первого бойцов, затем цифр таймера
                ; In:
                ;   рабочий растр и текущие записи бойцов подготовлены
                ; Out:
                ;   на рабочем растре обновлены оба бойца и цифры, прежний фон цифр сохранён
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, банковое окно
                ; -----------------------------------------
Entry:          CALL @ArchiveEngine.CalculateTimerAddress.Entry
                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.DrawFighter.Entry
                LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.DrawFighter.Entry
                CALL @ArchiveEngine.DrawTimerDigits.Entry
                RET

                endmodule
                endmodule

                module ArchiveEngine
                module CalculateTimerAddress
                ; Документация [цифры таймера](../../Docs/ArchiveEngineTimerRaster.md)
                ; -----------------------------------------
                ; расчёт положения левой цифры таймера в рабочем растре
                ; In:
                ;   ViewColumn и VerticalOffset задают положение окна сцены
                ; Out:
                ;   HL и Background равны ViewColumn + RowBytes * (VerticalOffset + 189) + 15
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
                ; расчёт смещения строки и добавление столбца между индикаторами
Entry:          LD DE, (@ArchiveEngineScene.View.RowBytes)
                LD A, (@ArchiveEngineScene.View.VerticalOffset)
                ADD A, @ArchiveEngineConst.TimerFirstRow
                CALL @ArchiveEngine.MultiplyByteWord.Entry
                LD DE, (@ArchiveEngineScene.View.ViewColumn)
                ADD HL, DE
                LD DE, @ArchiveEngineConst.MeterGapColumn
                ADD HL, DE
                LD (@ArchiveTimerRaster.Address.Background), HL
                RET

                endmodule
                endmodule

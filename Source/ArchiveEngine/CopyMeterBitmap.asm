                module ArchiveEngine
                module CopyMeterBitmap
                ; Документация [экранные индикаторы](../../Docs/ArchiveEngineMeters.md)
                ; -----------------------------------------
                ; перенос 10 последовательных строк по 15 байтов в растр ZX Spectrum
                ; In:
                ;   HL - начало 150 байтов исходного растра, DE - адрес первой строки экрана
                ; Out:
                ;   HL - адрес после исходного растра, DE - адрес за последней строкой в раскладке ULA
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
Entry:          LD B, @ArchiveEngineConst.MeterRows

                ; перенос строки и переход к следующему экранному адресу
CopyRow:        PUSH BC
                PUSH DE
                LD BC, @ArchiveEngineConst.MeterWidth
                LDIR
                POP DE
                POP BC
                CALL @ArchiveEngine.NextMeterRow.Entry
                DJNZ @ArchiveEngine.CopyMeterBitmap.CopyRow

                RET

                endmodule
                endmodule

                module ArchiveEngine
                module RestoreTimerBackground
                ; Документация [цифры таймера](../../Docs/ArchiveEngineTimerRaster.md)
                ; -----------------------------------------
                ; восстановление обеих колонок фона, сохранённых перед наложением цифр
                ; In:
                ;   Background содержит прежний адрес цифр, Buffer содержит 16 пар байтов
                ; Out:
                ;   прежние пиксели восстановлены в рабочем растре
                ;   HL - строка за последней обработанной, DE - адрес после буфера
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; -----------------------------------------
Entry:          LD HL, (@ArchiveTimerRaster.Address.Background)
                LD DE, @ArchiveTimerRaster.Buffer
                LD A, @ArchiveEngineConst.TimerDigitRows

                ; возврат двух байтов фона и переход к следующей строке цифр
RestoreRow:     EX AF, AF'
                LD A, (DE)
                LD (HL), A
                INC HL
                INC DE
                LD A, (DE)
                LD (HL), A
                DEC HL
                INC DE
                LD BC, (@ArchiveEngineScene.View.RowBytes)
                OR A
                SBC HL, BC
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveEngine.RestoreTimerBackground.RestoreRow         ; переход, если остались строки фона цифр

                RET

                endmodule
                endmodule

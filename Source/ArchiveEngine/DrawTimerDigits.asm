                module ArchiveEngine
                module DrawTimerDigits
                ; Документация [цифры таймера](../../Docs/ArchiveEngineTimerRaster.md)
                ; -----------------------------------------
                ; вывод двух цифр BCD в рабочий растр со сохранением прежнего фона
                ; In:
                ;   Seconds содержит корректное BCD, адрес фона цифр уже рассчитан
                ; Out:
                ;   обе цифры наложены, прежние байты сохраняются попарно для каждой строки
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX
                ; -----------------------------------------
                ; расчёт адреса шаблона старшей цифры, каждая цифра занимает 32 байта
Entry:          LD A, (@ArchiveEngineTimer.Value.Seconds)
                AND @ArchiveEngineConst.SecondsTens
                LD E, A
                LD D, #00
                LD HL, @ArchiveTimerRaster.Font
                ADD HL, DE
                ADD HL, DE

                ; наложение старшей цифры и сохранение левой половины фона
                LD DE, (@ArchiveTimerRaster.Address.Background)
                EX DE, HL
                LD A, @ArchiveEngineConst.TimerDigitRows
                LD IX, @ArchiveTimerRaster.Buffer
                CALL @ArchiveEngine.DrawTimerGlyph.Entry

                ; расчёт шаблона младшей цифры и наложение справа от старшей
                LD A, (@ArchiveEngineTimer.Value.Seconds)
                AND @ArchiveEngineConst.SecondsOnes
                SLA A
                SLA A
                SLA A
                SLA A
                LD E, A
                LD D, #00
                LD HL, @ArchiveTimerRaster.Font
                ADD HL, DE
                ADD HL, DE
                LD DE, (@ArchiveTimerRaster.Address.Background)
                INC DE
                EX DE, HL
                LD A, @ArchiveEngineConst.TimerDigitRows
                LD IX, @ArchiveTimerRaster.Buffer + 1
                CALL @ArchiveEngine.DrawTimerGlyph.Entry
                RET

                endmodule
                endmodule

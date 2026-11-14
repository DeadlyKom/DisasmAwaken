                module ArchiveEngine
                module UpdateTimer
                ; Документация [отсчёт времени](../../Docs/ArchiveEngineStartup.md#таймер)
                ; -----------------------------------------
                ; уменьшение счётчика кадра и оставшегося времени в BCD
                ; In:
                ;   Ticks в диапазоне 1..50, Seconds содержит две десятичные цифры BCD
                ; Out:
                ;   Ticks уменьшен, при нуле загружается 50 и обрабатывается очередная секунда
                ;   при BCD 00 и окончании периода исполняются DI и HALT
                ; Corrupt:
                ;   HL, AF, IFF меняется при остановке
                ; -----------------------------------------
                ; проверка, истёк ли очередной интервал из пятидесяти прерываний
Entry:          LD A, (@ArchiveEngineTimer.Value.Ticks)
                DEC A
                OR A
                JR Z, @ArchiveEngine.UpdateTimer.SecondPassed                   ; переход, если счётчик дошёл до нуля, обработать секунду

                LD (@ArchiveEngineTimer.Value.Ticks), A
                RET

                ; проверка младшей десятичной цифры, для ненулевой заём не нужен
SecondPassed:   LD A, @ArchiveEngineConst.TicksPerSecond
                LD (@ArchiveEngineTimer.Value.Ticks), A
                LD A, (@ArchiveEngineTimer.Value.Seconds)
                AND @ArchiveEngineConst.SecondsOnes
                JR NZ, @ArchiveEngine.UpdateTimer.Decrement                     ; переход, если младшая цифра ненулевая, вычесть единицу

                ; проверка старшей цифры, обе цифры равны нулю перед остановкой
                LD A, (@ArchiveEngineTimer.Value.Seconds)
                AND @ArchiveEngineConst.SecondsTens
                JR Z, @ArchiveEngine.UpdateTimer.StopScene                      ; переход, если обе цифры нулевые, остановить сцену

                ; заём из старшей цифры, младшая после займа равна девяти
                SUB @ArchiveEngineConst.SecondsBorrow
                OR @ArchiveEngineConst.LastDigit
                LD (@ArchiveEngineTimer.Value.Seconds), A
                RET

StopScene:      DI
                HALT
                RET

Decrement:      LD HL, @ArchiveEngineTimer.Value.Seconds
                DEC (HL)
                RET

                endmodule
                endmodule

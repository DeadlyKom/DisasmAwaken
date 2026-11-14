                module ArchiveEngine
                module InitializeTimer
                ; Документация [отсчёт времени](../../Docs/ArchiveEngineStartup.md#таймер)
                ; -----------------------------------------
                ; установка стартовых 99 секунд и первой задержки из 50 IRQ
                ; In:
                ;   параметров нет
                ; Out:
                ;   Seconds равен #99 в BCD, Ticks и A равны #32
                ; Corrupt:
                ;   AF, изменяется A, флаги сохраняются
                ; -----------------------------------------
Entry:          LD A, @ArchiveEngineConst.StartSeconds
                LD (@ArchiveEngineTimer.Value.Seconds), A
                LD A, @ArchiveEngineConst.TicksPerSecond
                LD (@ArchiveEngineTimer.Value.Ticks), A
                RET

                endmodule
                endmodule

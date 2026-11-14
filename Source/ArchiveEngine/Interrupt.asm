                module ArchiveEngine
                module Interrupt
                ; Документация [кадровое прерывание и стек](../../Docs/ArchiveEngineStartup.md#прерывание)
                ; -----------------------------------------
                ; обновление экранных индикаторов, таймера и клавиш по кадровому IRQ
                ; In:
                ;   SP указывает на сохранённый процессором адрес возврата, селектор страниц настроен
                ; Out:
                ;   обычный путь восстанавливает стек, страницу и регистры, возвращаясь с разрешёнными IRQ
                ; Corrupt:
                ;   регистры обычного пути восстанавливаются, IFF меняется, обновляется состояние сцены
                ; Note:
                ;   адрес стека хранится в изменяемом операнде RestoreStack, служебный стек растёт от Entry вниз
                ;   при истечении времени UpdateTimer выполняет DI и HALT внутри обработчика
                ; -----------------------------------------
                ; сохранение стека прерванного кода и переход на локальный стек обработчика
Entry:          EI
                LD (@ArchiveEngine.Interrupt.RestoreStack + 1), SP
                LD SP, @ArchiveEngine.Interrupt.Entry
                PUSH IX
                PUSH HL
                PUSH DE
                PUSH BC
                PUSH AF
                EXX
                EX AF, AF'
                PUSH HL
                PUSH DE
                PUSH BC
                PUSH AF

                ; обновление индикаторов и таймера, затем накопление новых нажатий
                CALL @ArchiveEngine.UpdateMeters.Entry
                CALL @ArchiveEngine.UpdateTimer.Entry
                CALL @ArchiveEngine.CollectCombatInput.Entry

                ; восстановление наборов регистров и стека прерванной сцены
                POP AF
                POP BC
                POP DE
                POP HL
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP HL
                POP IX
RestoreStack:   LD SP, #0000
                RET

                endmodule
                endmodule

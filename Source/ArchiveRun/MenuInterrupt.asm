                module ArchiveRun
                module MenuInterrupt
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; обработчик IRQ с восьмикадровой задержкой мигания стрелки
                ; In:
                ;   SP содержит адрес возврата аппаратного прерывания
                ; Out:
                ;   регистры и стек восстановлены, операнд BlinkCounter обновлён
                ;   при нуле прежнего счётчика стрелка XOR меняется на обоих экранах
                ; Corrupt:
                ;   IFF, экранная страница CPU после переключения стрелки
                ; -----------------------------------------
                ; сохранение обеих групп регистров и указателей
Entry:          EI
                PUSH AF
                EX AF, AF'
                PUSH AF
                PUSH HL
                PUSH DE
                PUSH BC
                EXX
                PUSH HL
                PUSH DE
                PUSH BC
                PUSH IX
                PUSH IY

                ; проверка счётчика до очередной смены стрелки
BlinkCounter:   LD A, #00
                OR A
                JR NZ, @ArchiveRun.MenuInterrupt.CountDown                      ; переход, если задержка ещё не истекла, уменьшить остаток без рисования

                CALL @ArchiveRun.ToggleSelectionMarker.Entry
                LD A, (@ArchiveRunState.BlinkPeriod)

                ; сохранение остатка задержки в операнде и восстановление регистров
CountDown:      DEC A
                LD (@ArchiveRun.MenuInterrupt.BlinkCounter + 1), A
                POP IY
                POP IX
                POP BC
                POP DE
                POP HL
                EXX
                POP BC
                POP DE
                POP HL
                POP AF
                EX AF, AF'
                POP AF
                RET

                endmodule
                endmodule

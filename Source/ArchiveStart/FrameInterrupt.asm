                module ArchiveStart
                module FrameInterrupt
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; кадровое прерывание с временным стеком и сохранением страницы
                ; In:
                ;   SP содержит аппаратный адрес возврата, режим IM2 активен
                ; Out:
                ;   на обычном пути регистры и SP восстановлены, код текущей страницы прежний
                ;   при Enter IRQ не возвращается, #6172 загружает ENGINE
                ; Corrupt:
                ;   IFF, состояние экрана и меню
                ; Note:
                ;   сохранённый SP лежит в изменяемом операнде RestoreStack, временный стек растёт вниз от #67A4
                ;   в двух проверенных профилях нижний адрес обращения к стеку равен #678A
                ; -----------------------------------------
                ; сохранение адреса прерванного стека и обоих наборов регистров
Entry:          EI
                LD (@ArchiveStart.FrameInterrupt.RestoreStack + 1), SP
                LD SP, @ArchiveStart.FrameInterrupt.Entry
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

                ; сохранение кода страницы и выполнение кадровой работы
                LD A, (@ArchiveStartData.Page.CurrentCode)
                LD (@ArchiveStartData.Page.IrqSavedCode), A
                CALL @ArchiveStart.HandleBankFrame.Entry
                LD A, (@ArchiveStartData.Page.IrqSavedCode)
                CALL @ArchiveStart.SelectPage.Dispatch

                ; восстановление регистров и прежнего стека
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

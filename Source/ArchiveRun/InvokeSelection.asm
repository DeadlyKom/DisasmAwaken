                module ArchiveRun
                module InvokeSelection
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; передача управления обработчику выбранной записи меню
                ; In:
                ;   индекс и адрес записей текущего меню известны
                ; Out:
                ;   DE - E, код 3 на возвращающемся пути, основной AF сохраняется
                ;   при удержании обработчик повторно не вызывается
                ; Corrupt:
                ;   HL, DE, BC, AF', IX по договору обработчика
                ; Note:
                ;   Start заменяет стек и не возвращается к AfterCallback
                ; -----------------------------------------
                ; проверка удержания клавиши подтверждения
Entry:          LD E, @ArchiveRunConst.ConfirmKeyCode
                EX AF, AF'
                LD A, (@ArchiveRunState.LastKey)
                CP @ArchiveRunConst.ConfirmKeyCode
                JP Z, @ArchiveRun.MoveSelectionUp.FinishKey                     ; переход, если подтверждение уже было в прошлом кадре, не вызывать обработчик

                ; подготовка возврата из косвенно выбранного обработчика
                PUSH DE
                PUSH AF
                LD HL, @ArchiveRun.InvokeSelection.AfterCallback
                PUSH HL

                ; расчёт адреса обработчика в четырёхбайтовой записи
                LD DE, (@ArchiveRunState.Menu.Records)
                LD A, (@ArchiveRunState.Menu.Selected)
                SLA A
                SLA A
                LD L, A
                LD H, #00
                ADD HL, DE
                INC HL
                INC HL
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                JP (HL)

                ; восстановление контекста проверки клавиш после обработчика
AfterCallback:  POP AF
                POP DE
                EX AF, AF'
                RET

                endmodule
                endmodule

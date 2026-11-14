                module ArchiveRun
                module MoveSelectionDown
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; сдвиг выбора к следующему пункту с блокировкой удержания
                ; In:
                ;   последний код клавиши, текущий и последний индексы известны
                ; Out:
                ;   DE - E, код 2, при допустимом ходе старая стрелка стёрта и индекс увеличен
                ;   основной AF сохраняется
                ; Corrupt:
                ;   HL, DE, BC, AF'
                ; -----------------------------------------
                ; проверка повторного нажатия следующего пункта
Entry:          LD E, @ArchiveRunConst.NextKeyCode
                EX AF, AF'
                LD A, (@ArchiveRunState.LastKey)
                CP @ArchiveRunConst.NextKeyCode
                JP Z, @ArchiveRun.MoveSelectionUp.FinishKey                     ; переход, если следующая клавиша ещё удерживается, сохранить выбор

                ; проверка верхней границы индекса
                LD A, (@ArchiveRunState.Menu.Selected)
                LD HL, @ArchiveRunState.Menu.LastItem
                CP (HL)
                JP Z, @ArchiveRun.MoveSelectionUp.FinishKey                     ; переход, если выбран последний пункт, оставить его

                ; стирание прежней стрелки и увеличение индекса
                PUSH DE
                CALL @ArchiveRun.ClearSelectionMarker.Entry
                POP DE
                LD A, (@ArchiveRunState.Menu.Selected)
                INC A
                LD (@ArchiveRunState.Menu.Selected), A
                EX AF, AF'
                RET

                endmodule
                endmodule

                module ArchiveRun
                module MoveSelectionUp
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; сдвиг выбора к предыдущему пункту с блокировкой удержания
                ; In:
                ;   последний код клавиши и текущий пункт сохранены в состоянии меню
                ; Out:
                ;   DE - E, код 1, при допустимом ходе старая стрелка стёрта и индекс уменьшен
                ;   основной AF сохраняется для остальных проверок того же порта
                ; Corrupt:
                ;   HL, DE, BC, AF'
                ; -----------------------------------------
                ; проверка повторного нажатия предыдущего пункта
Entry:          LD E, @ArchiveRunConst.PrevKeyCode
                EX AF, AF'
                LD A, (@ArchiveRunState.LastKey)
                CP @ArchiveRunConst.PrevKeyCode
                JP Z, @ArchiveRun.MoveSelectionUp.FinishKey                     ; переход, если предыдущая клавиша ещё удерживается, сохранить выбор

                ; проверка нижней границы индекса, заголовок недоступен
                LD A, (@ArchiveRunState.Menu.Selected)
                CP @ArchiveRunConst.FirstItem
                JP Z, @ArchiveRun.MoveSelectionUp.FinishKey                     ; переход, если выбран первый пункт, оставить его

                ; стирание прежней стрелки и уменьшение индекса
                PUSH DE
                CALL @ArchiveRun.ClearSelectionMarker.Entry
                POP DE
                LD A, (@ArchiveRunState.Menu.Selected)
                DEC A
                LD (@ArchiveRunState.Menu.Selected), A
FinishKey:      EX AF, AF'
                RET

                endmodule
                endmodule

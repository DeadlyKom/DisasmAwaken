                module ArchiveRun
                module FinishMenuText
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; восстановление адреса начала строки после вывода подписи
                ; In:
                ;   на вершине стека адрес начала строки, затем адрес возврата
                ; Out:
                ;   Cursor и HL получают сохранённый адрес, выполняется возврат
                ; Corrupt:
                ;   HL
                ; -----------------------------------------
Entry:          POP HL
                LD (@ArchiveRunState.Menu.Cursor), HL
                RET

                endmodule
                endmodule

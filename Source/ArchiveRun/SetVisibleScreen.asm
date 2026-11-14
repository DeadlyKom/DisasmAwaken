                module ArchiveRun
                module SetVisibleScreen
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; выбор видимого экрана и той же страницы для доступа через #C000
                ; In:
                ;   AF - A, номер экрана 0 или 1
                ; Out:
                ;   Visible хранит номер, порт #7FFD получает #15 для 0 или #1F для 1
                ; Corrupt:
                ;   BC, AF, отображение памяти
                ; -----------------------------------------
                ; сохранение номера и расчёт отдельных битов страницы и видимого экрана
Entry:          LD (@ArchiveRunState.Visible), A
                SLA A
                LD B, A
                SLA A
                SLA A
                OR B
                OR @ArchiveRunConst.PagingBase
                LD BC, @Hardware.PagingPort
                OUT (C), A
                RET

                endmodule
                endmodule

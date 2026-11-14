                module ArchiveRun
                module SelectDrawingScreen
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; выбор экранной страницы для записи без переключения показа
                ; In:
                ;   AF - A, номер страницы вывода 0 или 1, Visible содержит номер видимого экрана
                ; Out:
                ;   в окне #C000 выбрана страница 5 или 7, бит показа берётся из Visible
                ; Corrupt:
                ;   BC, AF, отображение памяти
                ; -----------------------------------------
                ; объединение номера страницы записи и прежнего бита показа
Entry:          SLA A
                OR @ArchiveRunConst.PagingBase
                LD B, A
                LD A, (@ArchiveRunState.Visible)
                SLA A
                SLA A
                SLA A
                OR B
                LD BC, @Hardware.PagingPort
                OUT (C), A
                RET

                endmodule
                endmodule

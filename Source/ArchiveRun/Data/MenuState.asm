                module ArchiveRunState
                ; Документация [рабочие поля меню](../../../Docs/StartArchiveMenu.md)
Menu:           FArchiveRunMenuState {
                    #0000,                                                      ; Cursor, задаётся перед выводом списка
                    #00,                                                        ; Selected, инициализация меняет на 1
                    #00,                                                        ; LastItem, вычисляется по числу записей
                    #0000                                                       ; Records, адрес текущего списка
                }
                endmodule

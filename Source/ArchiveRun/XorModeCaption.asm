                module ArchiveRun
                module XorModeCaption
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; наложение подписи текущего режима на оба экрана
                ; In:
                ;   Cursor указывает на строку настройки, текущий режим известен
                ; Out:
                ;   подпись изменена в обеих страницах и сохранён указатель в записи пункта
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, отображение памяти
                ; -----------------------------------------
                ; получение подписи режима и вывод через обе страницы
Entry:          LD A, (@ArchiveRunMenus.Memory.Current)
                CALL @ArchiveRun.FindModeCaption.Entry
                LD A, #00
                CALL @ArchiveRun.SelectDrawingScreen.Entry
                PUSH IX
                CALL @ArchiveRun.XorMenuText.Entry
                POP IX
                LD A, #01
                CALL @ArchiveRun.SelectDrawingScreen.Entry
                CALL @ArchiveRun.XorMenuText.Entry
                RET

                endmodule
                endmodule

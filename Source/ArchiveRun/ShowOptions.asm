                module ArchiveRun
                module ShowOptions
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; удаление основного списка и вывод Options
                ; In:
                ;   видим главный список меню
                ; Out:
                ;   выведен список Options, выбран первый пункт
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, отображение памяти
                ; -----------------------------------------
                ; стирание старых подписей через XOR и наложение новых
Entry:          LD HL, @ArchiveRunMenus.MainCount
                CALL @ArchiveRun.RenderMenu.Entry
                LD HL, @ArchiveRunMenus.OptionsCount
                CALL @ArchiveRun.RenderMenu.Entry
                RET

                endmodule
                endmodule

                module ArchiveRun
                module ShowMainMenu
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; удаление Options и возврат основного списка
                ; In:
                ;   видим список Options
                ; Out:
                ;   выведен главный список, выбран Start
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, отображение памяти
                ; -----------------------------------------
                ; стирание старых подписей через XOR и наложение основного списка
Entry:          LD HL, @ArchiveRunMenus.OptionsCount
                CALL @ArchiveRun.RenderMenu.Entry
                LD HL, @ArchiveRunMenus.MainCount
                CALL @ArchiveRun.RenderMenu.Entry
                RET

                endmodule
                endmodule

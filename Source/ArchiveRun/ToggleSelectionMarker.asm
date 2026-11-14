                module ArchiveRun
                module ToggleSelectionMarker
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; обратимое наложение стрелки в обеих экранных страницах
                ; In:
                ;   индекс выбранного пункта и видимая страница известны
                ; Out:
                ;   восемь байтов стрелки изменены XOR в обоих экранах, в окне страница 7
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
                ; вычисление общего адреса и наложение стрелки в первом экране
Entry:          CALL @ArchiveRun.FindSelectionMarker.Entry
                PUSH HL
                LD A, #00
                CALL @ArchiveRun.SelectDrawingScreen.Entry
                CALL @ArchiveRun.XorMarkerColumn.Entry

                ; выбор второго экрана и восстановление исходного адреса
                LD A, #01
                CALL @ArchiveRun.SelectDrawingScreen.Entry
                POP HL

                ; JP XorMarkerColumn.Entry, продолжение в XorMarkerColumn.asm

                endmodule
                endmodule

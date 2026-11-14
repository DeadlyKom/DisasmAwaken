                module ArchiveRun
                module ClearSelectionMarker
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; очистка восьми строк стрелки в обеих экранных страницах
                ; In:
                ;   выбранный пункт и видимая страница известны
                ; Out:
                ;   прежняя стрелка стёрта, в окне выбрана страница 7
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
                ; получение общего адреса и очистка в первом экране
Entry:          CALL @ArchiveRun.FindSelectionMarker.Entry
                PUSH HL
                LD A, #00
                CALL @ArchiveRun.SelectDrawingScreen.Entry
                CALL @ArchiveRun.ClearMarkerColumn.Entry

                ; выбор второй страницы и восстановление адреса перед продолжением
                LD A, #01
                CALL @ArchiveRun.SelectDrawingScreen.Entry
                POP HL

                ; JP ClearMarkerColumn.Entry, продолжение в ClearMarkerColumn.asm

                endmodule
                endmodule

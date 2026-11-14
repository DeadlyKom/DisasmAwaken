                module ArchiveRun
                module RenderMenu
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; наложение полного списка пунктов на оба экрана и установка нового выбора
                ; In:
                ;   HL - список с байтом числа записей, включая заголовок
                ; Out:
                ;   прежняя стрелка очищена, записаны Selected=1, LastItem и адрес первой записи
                ;   подписи списка изменены XOR в обеих страницах
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, отображение памяти
                ; Note:
                ;   повтор с тем же списком удаляет его подписи, заголовок занимает позицию 0
                ; -----------------------------------------
                ; очистка прежней стрелки и инициализация положения текста
Entry:          PUSH HL
                CALL @ArchiveRun.ClearSelectionMarker.Entry
                POP HL
                LD A, @ArchiveRunConst.FirstItem
                LD (@ArchiveRunState.Menu.Selected), A
                LD DE, @ArchiveRunConst.MenuTop
                LD (@ArchiveRunState.Menu.Cursor), DE

                ; чтение числа записей и сохранение предельного индекса
                LD A, (HL)
                INC HL
                LD (@ArchiveRunState.Menu.Records), HL
                LD B, A
                DEC A
                LD (@ArchiveRunState.Menu.LastItem), A

                ; чтение указателя подписи, обработчик при рисовании пропускается
NextItem:       PUSH BC
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                INC HL
                INC HL
                PUSH HL

                ; вывод подписи на первый и второй экраны
                PUSH DE
                PUSH DE
                POP IX
                LD A, #00
                CALL @ArchiveRun.SelectDrawingScreen.Entry
                CALL @ArchiveRun.XorMenuText.Entry
                POP IX
                LD A, #01
                CALL @ArchiveRun.SelectDrawingScreen.Entry
                CALL @ArchiveRun.XorMenuText.Entry

                ; расчёт адреса следующей знакоместной строки
                LD HL, (@ArchiveRunState.Menu.Cursor)
                LD A, L
                ADD A, #20
                LD L, A
                JR NC, @ArchiveRun.RenderMenu.StoreRow                          ; переход, если младший байт не переполнился, сохранить старший адрес

                LD A, H
                ADD A, #08
                LD H, A
StoreRow:       LD (@ArchiveRunState.Menu.Cursor), HL
                POP HL
                POP BC
                DJNZ @ArchiveRun.RenderMenu.NextItem

                RET

                endmodule
                endmodule

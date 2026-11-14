                module ArchiveStart
                module DrawRightDirect
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; вывод зеркальной правой полосы непосредственно из BANK в основной экран
                ; In:
                ;   маршрут и индекс правого кадра заданы
                ; Out:
                ;   флаг буфера сброшен, полоса выбрана из Direct и выведена в экран #4000
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', отображение памяти
                ; -----------------------------------------
                ; освобождение буфера и выбор страницы текущего маршрута
Entry:          XOR A
                LD (@ArchiveStart.StageRightStrip.Entry + 1), A
                LD A, (@ArchiveStartRoutes.Right.BankIndex)
                CALL @ArchiveStart.SelectBankIndex.Entry

                ; выбор прямого указателя кадра и подготовка адреса экрана
                LD A, (@ArchiveStartRoutes.RightIndex)
                LD HL, @ArchiveStartRoutes.Right.Direct00
                CALL @ArchiveStart.ResolveStrip.Entry

                ; JP CopyRightStrip.Entry, продолжение в CopyRightStrip.asm

                endmodule
                endmodule

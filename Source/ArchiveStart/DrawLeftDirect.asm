                module ArchiveStart
                module DrawLeftDirect
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; вывод левой полосы непосредственно из BANK в основной экран
                ; In:
                ;   маршрут и индекс левого кадра заданы
                ; Out:
                ;   флаг буфера сброшен, полоса выбрана из Direct и выведена в экран #4000
                ; Corrupt:
                ;   HL, DE, BC, AF, отображение памяти
                ; -----------------------------------------
                ; освобождение буфера и выбор страницы текущего маршрута
Entry:          XOR A
                LD (@ArchiveStart.StageLeftStrip.Entry + 1), A
                LD A, (@ArchiveStartRoutes.Left.BankIndex)
                CALL @ArchiveStart.SelectBankIndex.Entry

                ; выбор прямого указателя кадра и подготовка адреса экрана
                LD A, (@ArchiveStartRoutes.LeftIndex)
                LD HL, @ArchiveStartRoutes.Left.Direct00
                CALL @ArchiveStart.ResolveStrip.Entry

                ; JP CopyLeftStrip.Entry, продолжение в CopyLeftStrip.asm

                endmodule
                endmodule

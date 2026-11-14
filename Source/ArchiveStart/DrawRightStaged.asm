                module ArchiveStart
                module DrawRightStaged
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; подготовка правой полосы из фиксированного буфера для вывода в страницу 7
                ; In:
                ;   правый буфер заполнен полосой
                ; Out:
                ;   HL указывает на высоту, DE содержит адрес в окне #C000, исполняется CopyRightStrip
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', отображение памяти
                ; -----------------------------------------
                ; выбор теневой страницы и перевод адреса полосы в банковое окно
Entry:          LD A, #01
                CALL @ArchiveStart.SelectScreenForDraw.Entry
                LD HL, @ArchiveStartBuffers.Right
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                LD A, D
                OR #80
                LD D, A
                JP @ArchiveStart.CopyRightStrip.Entry

                endmodule
                endmodule

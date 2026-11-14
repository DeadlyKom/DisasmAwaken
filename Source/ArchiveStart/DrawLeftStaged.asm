                module ArchiveStart
                module DrawLeftStaged
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; подготовка левой полосы из фиксированного буфера для вывода в страницу 7
                ; In:
                ;   левый буфер заполнен полосой
                ; Out:
                ;   HL указывает на высоту, DE содержит адрес в окне #C000, исполняется CopyLeftStrip
                ; Corrupt:
                ;   HL, DE, BC, AF, отображение памяти
                ; -----------------------------------------
                ; выбор теневой страницы и перевод адреса полосы в банковое окно
Entry:          LD A, #01
                CALL @ArchiveStart.SelectScreenForDraw.Entry
                LD HL, @ArchiveStartBuffers.Left
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                LD A, D
                OR #80
                LD D, A
                JP @ArchiveStart.CopyLeftStrip.Entry

                endmodule
                endmodule

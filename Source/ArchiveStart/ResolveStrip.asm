                module ArchiveStart
                module ResolveStrip
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; чтение указателя полосы и адреса её экрана
                ; In:
                ;   HL - начало списка указателей, AF - A, индекс кадра
                ; Out:
                ;   DE - адрес экрана из заголовка, HL - адрес байта высоты
                ; Corrupt:
                ;   HL, DE, AF
                ; -----------------------------------------
                ; расчёт адреса слова указателя и чтение первых двух байтов заголовка
Entry:          LD E, A
                LD D, #00
                ADD HL, DE
                ADD HL, DE
                LD E, (HL)
                INC HL
                LD D, (HL)
                EX DE, HL
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                RET

                endmodule
                endmodule

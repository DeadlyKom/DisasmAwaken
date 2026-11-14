                module ArchiveStart
                module CopyLeftStrip
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; перенос шести байтов каждой строки левой полосы слева направо
                ; In:
                ;   HL - адрес байта ненулевой высоты, далее строки растра, DE - адрес экрана
                ; Out:
                ;   HL - конец прочитанного растра, DE - следующая экранная строка
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
                ; чтение высоты и развёрнутый перенос шести байтов строки
Entry:          LD B, (HL)
                INC HL
CopyRow:        PUSH DE
                LD C, #FF
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI

                ; восстановление столбца и переход к следующей экранной строке
                POP DE
                CALL @ArchiveStart.NextStripRow.Entry
                DJNZ @ArchiveStart.CopyLeftStrip.CopyRow

                RET

                endmodule
                endmodule

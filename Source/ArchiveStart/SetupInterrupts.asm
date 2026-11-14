                module ArchiveStart
                module SetupInterrupts
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; установка IM2 с общим вектором обработчика меню BANK
                ; In:
                ;   RAM таблицы и переходника доступна для записи
                ; Out:
                ;   таблица #5E00..#5F00 заполнена #5F, по #5F5F записан JP #67A4
                ;   I равен #5E, включены IM 2 и кадровые прерывания
                ; Corrupt:
                ;   HL, DE, BC, AF, I, IM и IFF
                ; -----------------------------------------
                ; заполнение 257 байтов общего вектора
Entry:          DI
                LD HL, @ArchiveStartConst.VectorBase
                LD D, H
                LD E, L
                INC DE
                LD (HL), @ArchiveStartConst.VectorFill
                LD BC, @ArchiveStartConst.VectorTail
                LDIR

                ; запись переходника и включение прерываний перед возвратом
                LD A, #C3
                LD (@ArchiveStartConst.VectorJump), A
                LD HL, @ArchiveStart.FrameInterrupt.Entry
                LD (@ArchiveStartConst.VectorOperand), HL
                LD A, @ArchiveStartConst.VectorPage
                LD I, A
                IM 2
                EI
                RET

                endmodule
                endmodule

                module ArchiveStart
                module MultiplyByteWord
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; умножение восьмибитового значения на слово по модулю 65536
                ; In:
                ;   DE - множимое, AF - A, множитель
                ; Out:
                ;   HL - младшие 16 бит произведения, DE сдвинуто влево на восемь, A и B равны 0
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
Entry:          LD B, #08
                LD HL, #0000

                ; проверка очередного бита перед прибавлением слагаемого
NextBit:        SRL A
                JR NC, @ArchiveStart.MultiplyByteWord.ShiftWord                 ; переход, если текущий бит нулевой, пропустить прибавление

                ADD HL, DE

                ; удвоение слагаемого для следующего разряда
ShiftWord:      SLA E
                RL D
                DJNZ @ArchiveStart.MultiplyByteWord.NextBit

                RET

                endmodule
                endmodule

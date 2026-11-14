                module ArchiveEngine
                module MultiplyByteWord
                ; Документация [адресация окна](../../Docs/Scene1PixelPairs.md#полный-фон-кадра)
                ; -----------------------------------------
                ; умножение беззнакового байта на слово с результатом по модулю 65536
                ; In:
                ;   DE - множимое слово
                ;   AF - A, множитель от 0 до 255
                ; Out:
                ;   HL - младшие 16 бит произведения, DE - исходное DE со сдвигом на восемь
                ;   B и A равны нулю, C сохранён
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; -----------------------------------------
Entry:          LD B, @ArchiveEngineConst.MeterHeight
                LD HL, #0000

                ; проверка очередного бита множителя перед прибавлением текущего слагаемого
BitStep:        SRL A
                JR NC, @ArchiveEngine.MultiplyByteWord.ShiftWord                ; переход, если очередной бит нулевой, пропустить прибавление

                ADD HL, DE

                ; удвоение слагаемого перед обработкой следующего разряда
ShiftWord:      SLA E
                RL D
                DJNZ @ArchiveEngine.MultiplyByteWord.BitStep

                RET

                endmodule
                endmodule

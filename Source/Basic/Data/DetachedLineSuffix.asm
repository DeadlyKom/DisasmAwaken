                module BasicDetachedLineSuffix
                ; Документация [фрагмент за логическим BASIC](../../../Docs/BasicProgram.md)
                assert $ == #007B
QuotedTail:     db "uck", #22                                                   ; сохранённые символы до закрывающей кавычки
LineToken:      db #CA, "20", #0D                                               ; токен LINE, две цифры и CR в исходном порядке
NextByte:       db #80                                                          ; следующий байт сектора, исходная роль неизвестна
                assert $ == #0084
                endmodule

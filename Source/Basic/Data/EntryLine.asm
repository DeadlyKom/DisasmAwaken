                module BasicProgramEntryLine
                ; Документация [исходная BASIC-программа](../../../Docs/BasicProgram.md)
                assert $ == #5DA0
Line20:         FBasicLineHeader { #00, #14, #000E }
Statement:      db #F9, #C0, "23873", #0E                                       ; RANDOMIZE USR, печатное число и маркер сохранённого числового значения
UsrNumber:      FBasicSmallInteger { #00, #00, #41, #5D, #00 }
EndLine:        db #0D                                                          ; завершение второй строки и логической программы
                assert $ == #5DB2
                endmodule

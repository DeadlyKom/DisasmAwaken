                module BasicArchiveRunLine
                ; Документация [архивный вход BASIC](../../../Docs/ArchiveMenuHandoff.md#строка-архивного-basic)
Line1:          FBasicLineHeader {
                    #00,                                                        ; LineHigh
                    #01,                                                        ; LineLow, номер строки 1
                    #0018                                                       ; BodyLength, 24 байта вместе с CR
                }

EnterDos:       db #F9, #C0, "15619", #0E                                       ; RANDOMIZE USR, печатное число и маркер числового значения
UsrNumber:      FBasicSmallInteger {
                    #00,                                                        ; Exponent, компактное целое
                    #00,                                                        ; Sign, положительное значение
                    #03,                                                        ; Low
                    #3D,                                                        ; High, адрес входа TR-DOS #3D03
                    #00                                                         ; Unused
                }

DosCommand:     db #3A, #EA, #3A, #F7                                          ; : REM : RUN, команда после вызова TR-DOS
RunName:        db #22, "RUN", #22                                             ; имя файла в кавычках, без расширения
CodeType:       db #AF                                                          ; CODE, поиск записи RUN.C
EndLine:        db #0D                                                          ; завершение строки и программы
                endmodule

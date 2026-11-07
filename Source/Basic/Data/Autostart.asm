                module BasicProgramAutostart
                ; Документация [автозапуск BASIC](../../../Docs/BasicProgram.md)
                ; Здесь используются файловые смещения, маркер не является продолжением BASIC в RAM.
                assert $ == #0077
Entry:          FTrDosBasicAutostart {
                    #80,                                                        ; Marker80, первая часть сигнатуры
                    #AA,                                                        ; MarkerAA, вторая часть сигнатуры
                    #0014                                                       ; LineNumber, строка 20 содержит RANDOMIZE USR 23873
                }
                assert $ == #007B
                endmodule

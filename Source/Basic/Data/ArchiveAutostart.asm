                module BasicArchiveAutostart
                ; Документация [архивный вход BASIC](../../../Docs/ArchiveMenuHandoff.md#строка-архивного-basic)
                ; Маркер находится сразу после логической строки, адрес метки является файловым смещением.
Entry:          FTrDosBasicAutostart {
                    #80,                                                        ; Marker80, первая часть сигнатуры
                    #AA,                                                        ; MarkerAA, вторая часть сигнатуры
                    #0000                                                       ; LineNumber, исходный номер автозапуска
                }
                endmodule

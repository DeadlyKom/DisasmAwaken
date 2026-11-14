                module ArchiveOpponentMask
                ; Документация [адрес второй записи](../../../Docs/FighterAssets.md#физические-записи-бойцов)
Value:          FArchiveFighterWord {
                    #00,                                                        ; Low, младший байт XOR двух адресов
                    #00                                                         ; High, старший байт XOR двух адресов
                }
                endmodule

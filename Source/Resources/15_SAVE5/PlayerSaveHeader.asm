                module Save5PlayerSaveHeader
                ; Документация [сохраняемые поля игрока](../../../Docs/PlayerSavedFields.md)
                assert $ == #000E
Entry:          FPlayerSaveHeader {
                    #00,                                                        ; FPlayerSaveHeader.ShipIndex, исходное значение
                    #00,                                                        ; FPlayerSaveHeader.SkimmerIndex, исходное значение
                    #00,                                                        ; FPlayerSaveHeader.StatusCode, исходное значение
                    #0000,                                                      ; FPlayerSaveHeader.RankScore, исходное значение
                    #0000,                                                      ; FPlayerSaveHeader.Money, исходное значение
                    #00,                                                        ; FPlayerSaveHeader.UsedTonnage, исходное значение
                    #00                                                         ; FPlayerSaveHeader.Capacity, исходное значение
                }
                assert $ == #0017
                endmodule

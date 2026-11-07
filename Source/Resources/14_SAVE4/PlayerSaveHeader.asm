                module Save4PlayerSaveHeader
                ; Документация [сохраняемые поля игрока](../../../Docs/PlayerSavedFields.md)
                assert $ == #000E
Entry:          FPlayerSaveHeader {
                    #06,                                                        ; FPlayerSaveHeader.ShipIndex, исходное значение
                    #FF,                                                        ; FPlayerSaveHeader.SkimmerIndex, исходное значение
                    #00,                                                        ; FPlayerSaveHeader.StatusCode, исходное значение
                    #0005,                                                      ; FPlayerSaveHeader.RankScore, исходное значение
                    #07D0,                                                      ; FPlayerSaveHeader.Money, исходное значение
                    #0D,                                                        ; FPlayerSaveHeader.UsedTonnage, исходное значение
                    #32                                                         ; FPlayerSaveHeader.Capacity, исходное значение
                }
                assert $ == #0017
                endmodule

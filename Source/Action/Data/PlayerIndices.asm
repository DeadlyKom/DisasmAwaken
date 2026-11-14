                module ActionPlayerIndices
                ; Документация [перенос полей игрока](../../../Docs/ActionTransferredPlayerFields.md)
                assert $ == #9BCB
                ; -----------------------------------------
                ; исходная физическая запись Initial
Initial:        FActionPlayerIndices {
                    #00,                                                        ; ShipIndex, копия индекса корабля из состояния станции
                    #00                                                         ; SkimmerIndex, копия индекса глайдера из состояния станции
                }
                assert $ == #9BCD
                endmodule
